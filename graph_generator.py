'''
Generates a communication graph
Scenario emails -> solid lines
Noise emails -> dashed lines
'''
import graphviz

GRAPH_OUTPUT_FILE = 'graph.png'

def generate_communication_graph(email_data):
    
    graph = graphviz.Digraph(format='png')
    for email in email_data:
        sender = email['from']
        recipient = email['to']
        date = email['date']
        email_type = email['email_type']

        if email['source'] == 'noise':
            style = 'dashed'    # for noise emails
        else:
            style = 'solid'     # for scenario emails
        label = f"{email_type} \n {date.strftime('%H:%M:%S')}"

        graph.edge(sender, recipient, label = label, style = style)
    graph.render(GRAPH_OUTPUT_FILE,cleanup=True)