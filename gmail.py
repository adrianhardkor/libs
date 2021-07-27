# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START gmail_quickstart]
from __future__ import print_function
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import wcommon as wc
from email.mime.text import MIMEText
import base64

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://mail.google.com/']

def create_message(sender, to, subject, message_text):
  message = MIMEText(message_text)
  message['to'] = to
  message['from'] = sender
  message['subject'] = subject
  return({'raw': wc.bytes_str(base64.urlsafe_b64encode(message.as_string().encode('utf-8')))})

def send_message(service, user_id, message):
    message = service.users().messages().send(userId=user_id, body=message).execute()
    print('Message Id: %s' % message['id'])
    return(message)

def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                wc.argv_dict['cred'], SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)
    message = create_message('management@adriankrygowski.com', 'adrian.krygowski@gmail.com', 'test1', '1\n2')
    print(send_message(service, 'me', message))

#    # Call the Gmail API
#    results = service.users().drafts().list(userId='me').execute()
#    wc.jd(results)
#    labels = results.get('labels', [])
#
#    if not labels:
#        print('No labels found.')
#    else:
#        print('Labels:')
#        for label in labels:
#            print(label['name'])

if __name__ == '__main__':
    main()
# [END gmail_quickstart]
