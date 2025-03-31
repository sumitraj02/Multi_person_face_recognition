"""
This module sends emails with attachments to the participants
Reference - https://developers.google.com/gmail/api/quickstart/python

In order to run this module, you need to enable Gmail API and download client_secrets.json file
"""

from email import encoders
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import mimetypes
import os
import time

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText
import base64
import cv2

# If modifying these scopes, delete the file token.json.
# We are using Gmail API to send emails
SCOPES = ['https://www.googleapis.com/auth/gmail.send']


def authentication():
    creds = None

    # Check if token.json exists
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # Authenticate if no valid credentials found
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('gmail_api/client_secrets.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Save credentials
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds


def prepare_and_send_email(sender, recipient, subject, message_text, im0: bytes):
    """Prepares and send email with attachment"""

    creds = authentication()

    try:
        service = build('gmail', 'v1', credentials=creds)
        msg = create_message(sender, recipient, subject, message_text, im0)
        send_message(service, 'me', msg)

    except HttpError as error:
        print(f'An error occurred: {error}')


def create_message(sender, to, subject, message_text, img_file):
    """Create a message for an email."""

    message = MIMEMultipart()
    message['from'] = sender
    message['to'] = to
    message['subject'] = subject

    base_loc = './static/violations/'
    location = 'GLB'

    current_date_time = time.strftime("%H-%M-%S_%d-%m-%Y", time.localtime(time.time()))
    if not os.path.exists(base_loc):
        os.makedirs(base_loc)

    file_name = f'{base_loc}violation_{location}_{current_date_time}.jpg'
    cv2.imencode('.jpg', img_file)[1].tofile(file_name)

    msg = MIMEText(message_text)
    message.attach(msg)

    content_type, encoding = mimetypes.guess_type(file_name)
    main_type, sub_type = content_type.split('/', 1)

    print(f'Attachment main_type = {main_type}, subtype= {sub_type}, encoding = {encoding}')

    if main_type == 'image':
        with open(file_name, 'rb') as fp:
            msg = MIMEImage(fp.read(), _subtype=sub_type)
    else:
        with open(file_name, 'rb') as fp:
            msg = MIMEBase(main_type, sub_type)
            msg.set_payload(fp.read())
            encoders.encode_base64(msg)

    filename = os.path.basename(file_name)
    msg.add_header('Content-Disposition', 'attachment', filename=filename)
    message.attach(msg)

    return {'raw': base64.urlsafe_b64encode(message.as_string().encode()).decode()}


def send_message(service, user_id, message):
    """Send an email message."""
    try:
        message = service.users().messages().send(userId=user_id, body=message).execute()
        print('Message Id: %s' % message['id'])
        return message
    except HttpError as error:
        print('An error occurred: %s' % error)


if __name__ == '__main__':
    # Send email using your credentials
    prepare_and_send_email(
        sender='it22064@glbitm.ac.in',
        recipient='sumitkumar918403@gmail.com',
        subject='People detected ',
        message_text='People counting thresold system',
        im0=cv2.imread('static/output.png')
    )
