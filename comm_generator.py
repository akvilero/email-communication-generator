'''
Generates scenario emails, optionally adds noise emails,
writes them to an mbox file and generates communication graph.

NOISE_LEVEL determines how many random noise emails are generated:
- total noise emails = int(NOISE_LEVEL * number of scenario emails) (rounded down)
- if NOISE_LEVEl = 0, no noise emails are added
'''

from datetime import datetime, timedelta
import mailbox

from graph_generator import *
from utils import *
from noise_generator import *

SCENARIOS_FOLDER = 'scenarios'
SCENARIO_TEMPLATES_FOLDER = 'templates'
SCENARIO_FILENAME = 'scenario_3.csv'
OUT_FILENAME = 'out.mbox'
NOISE_LEVEL = 0 # number multiplier for noise emails
START_TIMESTAMP = datetime(2025, 1, 1, 8, 30, 0)    # starting point for scenario emails


def parse_scenario(scenario_file=SCENARIO_FILENAME, folder=SCENARIOS_FOLDER):
    path = os.path.join(folder, scenario_file)
    events = []
    
    with open(path, newline='') as f:
        for row in csv.DictReader(f):
            t_max = row['t_max']
            params = [row['param1'], row['param2']]
            event = {
                'e_id': row['e_id'],
                't_max': timedelta(minutes= int(t_max)),
                'from': row['from'],
                'to': row['to'],
                'type': row['type'],
                'template': row['template'],
                'params': params,
                'fwd_id':row['fwd_id']
            } 
            events.append(event)
    return events

def fill_template(template_filename, params, folder=SCENARIO_TEMPLATES_FOLDER):
    if template_filename == '':
        return '', ''
    
    path = os.path.join(folder, template_filename) 
    if not os.path.exists(path):
        raise FileNotFoundError(f"Template file '{path}' does not exists")
   
    with open(path) as f:
        lines = f.readlines()
   
    if not lines or not lines[0].startswith('#subject:'):
        raise ValueError(f"Template file '{path}' must start with '#subject:")
    
    subject = lines[0].split(': ')[1].strip()   # subject is the first line after '#subject:'
    body = "".join(lines[1:])   # body is all remaining lines
    
    # replace placeholder parameters
    for i, param in enumerate(params, start=1):
        placeholder = f'${i}'
        subject = subject.replace(placeholder, param)
        body = body.replace(placeholder, param)

    return subject, body

def generate_scenario_emails(start_time):
    contacts = load_contacts()
    events = parse_scenario()
    emails = {} # store email data for forwards and graph generation
    scenario_communication = [] # for EmailMessage objects

    for event in events:
        sender = contacts[event['from']]['email']
        recipient = contacts[event['to']]['email']

        date = generate_timestamp(start_time, start_time + event['t_max'])        
        subject, body = fill_template(event['template'], event['params'])

        email_type = event['type'].upper()
        if email_type == 'REPLY':
            subject = 'Re: ' + subject
        
        if email_type == 'FWD':
            fwd_id = event['fwd_id']
            
            fwd_block = (''
                '\n----- Forwarded message -----\n'
                f'From: {emails[fwd_id]['from']}\n'
                f'To: {emails[fwd_id]['to']}\n'
                f'Date: {emails[fwd_id]['date'].strftime('%a,%d %b %Y %H:%M:%S %z')}\n'
                f'Subject: {emails[fwd_id]['subject']}\n\n'
            )
            body = fwd_block + emails[fwd_id]['body'] + '\n\n'+ body
            
        
        email = create_message(sender, recipient, subject, body, date)
        scenario_communication.append({
            'date':date,
            'email':email
        })
        
        emails[event['e_id']] = {
            'from':sender,
            'to':recipient,
            'date':date,
            'subject':subject,
            'body':body,
            'email_type': email_type,
            'source':'scenario'
        }
        
        start_time = date
    return scenario_communication, emails

        
def generate_sequence():
    scenario_communication, emails = generate_scenario_emails(START_TIMESTAMP)
   
   # noise generation
    if NOISE_LEVEL > 0:
        noise_level = int(NOISE_LEVEL*len(scenario_communication))  # number of noise emails
        
        # noise emails sent between first and last scenario email
        if len(scenario_communication) > 1:
            dates = [item['date'] for item in scenario_communication]
            start_date = min(dates)
            end_date = max(dates)
        
        # or within 30 minutes if there is only one scenario email 
        else:
            start_date = scenario_communication[0]['date']
            end_date = start_date + timedelta(minutes=30)

        noise_emails, noise_emails_for_graph = generate_noise_emails(noise_level, start_date, end_date)
    else:
        noise_emails = []
        noise_emails_for_graph = []
    
    # combine scenario and noise emails, then sort them by date
    communication = scenario_communication + noise_emails
    communication = sorted(communication, key=lambda email:email['date'])
        
    # write all emails to .mbox file
    mbox = mailbox.mbox(OUT_FILENAME)
    for item in communication:
        mbox.add(item['email'])
    mbox.flush()
    mbox.close()

    # prepare data and generate graph
    scen_emails_for_graph=list(emails.values())
    generate_communication_graph(scen_emails_for_graph+noise_emails_for_graph) 

if __name__ == "__main__":
    generate_sequence()