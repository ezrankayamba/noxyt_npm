from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from email.mime.text import MIMEText
import base64

token_storage = 'client_id.token.pickle'
cred_file = 'client_id.json'
base_email = 'npmnoxytsoftwaresolutionsnots'


def send_message(service, message):
    try:
        return (service.users().messages().send(userId='me', body=message).execute())
    except Exception as e:
        print(f'An error occurred: {e}')


def create_message(sender, to, subject, message_text):
    message = MIMEText(message_text, 'html')
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes())
    raw = raw.decode()
    return {'raw': raw}


def init_service():
    SCOPES = ['https://www.googleapis.com/auth/gmail.modify',
              'https://www.googleapis.com/auth/gmail.settings.basic']
    creds = None
    if os.path.exists(token_storage):
        with open(token_storage, 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(cred_file, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_storage, 'wb') as token:
            pickle.dump(creds, token)
    return build('gmail', 'v1', credentials=creds)


def create_labels(service, name):
    m, s, f = get_labels(name)
    labels = service.users().labels()
    res1 = labels.create(userId='me', body={'name': m}).execute()
    res2 = labels.create(userId='me', body={'name': s}).execute()
    res3 = labels.create(userId='me', body={'name': f}).execute()
    return (res1, res2, res3)


def get_name(c):
    return f'COMP2{c.id:05}'


def setup_alias(service, c):
    res = create_labels(service, get_name(c))
    fltr = {
        'criteria': {'to': c.email},
        'action': {'addLabelIds': [res[0]['id']]}
    }
    settings = service.users().settings()
    return settings.filters().create(userId='me', body=fltr).execute()


def get_labels(name):
    m = f'Payments/{name}'
    s = f'Payments/{name}/Success'
    f = f'Payments/{name}/Fail'
    return (m, s, f)


def my_labels(service, c):
    name = get_name(c)
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])
    m, s, f = get_labels(name)
    labels = list(filter(lambda x: x['name'] == m or x['name'] == s or x['name'] == f, labels))
    if len(labels) >= 2:
        res = {}
        for x in labels:
            if x['name'] == s:
                res['success'] = x['id']
            elif x['name'] == f:
                res['fail'] = x['id']
            elif x['name'] == m:
                res['main'] = x['id']
        return res
    return None
