'''
Utility functions for email generation 
- loading contacts from csv
- creating EmailMessage objects
- generating random timestamps
'''

import csv
from datetime import timedelta
from email.message import EmailMessage
import random

CONTACTS_FILE = 'contacts.csv'

def load_contacts(contact_file=CONTACTS_FILE):
    contacts = {}
    with open(contact_file, newline='') as f:
        for row in csv.DictReader(f):
            contacts[row['id']] = {
                'email': row['email'],
                'name': row['name'],
                'surname': row['surname']
            }
    return contacts

def create_message(sender, recipient, subject, body, date):
    msg = EmailMessage()
    msg['From'] = sender
    msg['To'] = recipient
    msg['Subject'] = subject
    msg['Date'] = date.strftime('%a, %d %b %Y %H:%M:%S %z')
    msg.set_content(body, cte='7bit')
    return msg

def generate_timestamp(start_date, end_date):
    interval_secs = int((end_date-start_date).total_seconds())
    
    if interval_secs <= 0:
        return start_date
    
    offset = random.randint(1, interval_secs)   # pick a random offset in seconds within the interval
    date = start_date + timedelta(seconds=offset)   # add offset to the start date
    return date
