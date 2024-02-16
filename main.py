import os
import base64
import pickle
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
TOKEN_FILE = 'token.pickle'
CREDENTIALS_FILE = 'credentials.json'

def get_gmail_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
    service = build('gmail', 'v1', credentials=creds)
    return service

def list_messages(service, query=''):
    response = service.users().messages().list(userId='me', q=query).execute()
    messages = response.get('messages', [])
    return messages

def mark_as_read(service, message_id):
    service.users().messages().modify(
        userId='me',
        id=message_id,
        body={'removeLabelIds': ['UNREAD']}
    ).execute()

def delete_message(service, message_id):
    service.users().messages().delete(userId='me', id=message_id).execute()

def main():
    service = get_gmail_service()
    query = 'is:unread -in:inbox from:joehearthstone@gmail.com'
    messages = list_messages(service, query)

    for message in messages:
        message_id = message['id']
        labels = service.users().messages().get(userId='me', id=message_id).execute()['labelIds']
        if 'STAR' not in labels:
            delete_message(service, message_id)
        else:
            mark_as_read(service, message_id)

if __name__ == '__main__':
    main()
