'''
Generates random NEW/REPLY/FWD emails
'''

import os
from utils import *

NOISE_TEMPLATES_FOLDER = 'noise_templates'

def pick_sender_recipient():
    contacts = load_contacts()
    
    people = list(contacts.values())
    sender, recipient = random.sample(people, 2)
    
    return sender, recipient

def load_noise_templates(folder=NOISE_TEMPLATES_FOLDER):
    noise_templates=[]

    for filename in os.listdir(folder):
        path = os.path.join(folder, filename)
        with open(path) as f:
            lines = f.readlines()     
            subject = lines[0].split(': ')[1].strip()
            body = "".join(lines[1:])        
     
        noise_templates.append({ 
            'filename': filename,
            'subject': subject,
            'body':body
        }) 
    return noise_templates


def generate_noise_emails(noise_level, start_date, end_date):
    noise_emails = []           # for EmailMessage objects
    noise_emails_to_fwd = []    # for generating FWD emails and graph
    templates = load_noise_templates()
    
    for _ in range(noise_level):
        sender, recipient = pick_sender_recipient()
        sender = sender['email']
        recipient = recipient['email']
        
        date = generate_timestamp(start_date, end_date)

        email_type = random.choice(['NEW', 'REPLY', 'FWD'])

        template = random.choice(templates)
        subject = template['subject']
        body = template['body']
      
        if email_type == 'REPLY':
            subject = 'Re: ' + subject
        
        if email_type == 'FWD':
            if noise_emails_to_fwd:
                fwd_email=random.choice(noise_emails_to_fwd)
              
                fwd_block = (''
                '\n----- Forwarded message -----\n'
                f'From: {fwd_email['from']}\n'
                f'To: {fwd_email['to']}\n'
                f'Date: {fwd_email['date'].strftime('%a,%d %b %Y %H:%M:%S %z')}\n'
                f'Subject: {fwd_email['subject']}\n\n'
                f'{fwd_email['body']}'
                )
                body = fwd_block + '\n\n'+ body

        noise_email = create_message(sender, recipient, subject, body, date)
        
        noise_emails.append({
            'date': date,
            'email':noise_email
            })

        noise_emails_to_fwd.append({
            'from':sender,
            'to':recipient,
            'date':date,
            'subject':subject,
            'body':body,
            'email_type':email_type,
            'source':'noise'
        })
        
    return noise_emails, noise_emails_to_fwd
   
