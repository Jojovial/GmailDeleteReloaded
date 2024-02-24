import os
import base64
import pickle
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
TOKEN_FILE = 'token.pickle'
CREDENTIALS_FILE = 'clientservices.json'

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
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
    service = build('gmail', 'v1', credentials=creds)
    return service

def list_messages(service, query=''):
    response = service.users().messages().list(userId='joehearthstone@gmail.com', q=query).execute()  # Updated user ID
    messages = response.get('messages', [])
    return messages

def mark_as_read(service, message_id):
    service.users().messages().modify(
        userId='joehearthstone@gmail.com',  # Updated user ID
        id=message_id,
        body={'removeLabelIds': ['UNREAD']}
    ).execute()

def delete_message(service, message_id):
    service.users().messages().delete(userId='joehearthstone@gmail.com', id=message_id).execute()  # Updated user ID

def main():
    service = get_gmail_service()
    query = 'is:unread -in:inbox'
    messages = list_messages(service, query)

    for message in messages[:10]:  # Process only the first 10 messages for testing
        message_id = message['id']
        labels = service.users().messages().get(userId='joehearthstone@gmail.com', id=message_id).execute()['labelIds']  # Updated user ID
        if 'STAR' not in labels:
            delete_message(service, message_id)
        else:
            mark_as_read(service, message_id)

if __name__ == '__main__':
    main()
