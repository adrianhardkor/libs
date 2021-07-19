#!/usr/bin/env python3
from __future__ import print_function
import datetime
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import wcommon as wc
import pickle

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

class GCAL():
	def __init__(self, CALENDAR_ID, SCOPES, PICKLE_TOKEN_FILE, creds_json):
		self.CALENDAR_ID = CALENDAR_ID
		self.SCOPES = SCOPES
		self.PICKLE_TOKEN_FILE = PICKLE_TOKEN_FILE
		self.creds_json = creds_json

	def Connect(self):
		connect = wc.timer_index_start()
		creds = None
		if os.path.exists(self.PICKLE_TOKEN_FILE):
			with open(self.PICKLE_TOKEN_FILE, 'rb') as token:
				creds = pickle.load(token)
		if not creds or not creds.valid:
			if creds and creds.expired and creds.refresh_token:
				creds.refresh(Request())
			else:
				flow = InstalledAppFlow.from_client_secrets_file(self.creds_json, self.SCOPES)
				creds = flow.run_local_server(port=0)
			# Save the credentials for the next run
			with open(self.PICKLE_TOKEN_FILE, 'wb') as token:
				pickle.dump(creds, token)
		self.service = build('calendar', 'v3', credentials=creds)
		return(self.service)
	def GET_CAL(self, calendarId):
		now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
		events_result = self.service.events().list(calendarId=calendarId, timeMin=now, maxResults=365, singleEvents=True, orderBy='startTime').execute()
		events = events_result.get('items', [])
		return(events)


CAL = GCAL('', SCOPES, '/opt/google/cal.pickle', '/opt/google/credentials.json')
CAL.Connect()
data = CAL.GET_CAL('c_mssn01vn2ualcgtf1l4ugjtqe4')
wc.jd(data)
	
#def main():
#    """Shows basic usage of the Google Calendar API.
#    Prints the start and name of the next 10 events on the user's calendar.
#    """
#    creds = None
#    # The file token.json stores the user's access and refresh tokens, and is
#    # created automatically when the authorization flow completes for the first
#    # time.
#    if os.path.exists('token.json'):
#        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
#    # If there are no (valid) credentials available, let the user log in.
#    if not creds or not creds.valid:
#        if creds and creds.expired and creds.refresh_token:
#            creds.refresh(Request())
#        else:
#            flow = InstalledAppFlow.from_client_secrets_file(
#                'credentials.json', SCOPES)
#            creds = flow.run_local_server(port=0)
#        # Save the credentials for the next run
#        with open('token.json', 'w') as token:
#            token.write(creds.to_json())
#
#    service = build('calendar', 'v3', credentials=creds)
#
#    # Call the Calendar API
#    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
#    print('Getting the upcoming 10 events')
#    events_result = service.events().list(calendarId='primary', timeMin=now,
#                                        maxResults=10, singleEvents=True,
#                                        orderBy='startTime').execute()
#    events = events_result.get('items', [])
#
#    if not events:
#        print('No upcoming events found.')
#    for event in events:
#        start = event['start'].get('dateTime', event['start'].get('date'))
#        print(start, event['summary'])
#
#
#if __name__ == '__main__':
#    main()
#
#
#        def Connect(self):
#                connect = wc.timer_index_start()
#                creds = None
#                if os.path.exists(self.PICKLE_TOKEN_FILE):
#                        with open(self.PICKLE_TOKEN_FILE, 'rb') as token:
#                                creds = pickle.load(token)
#                if not creds or not creds.valid:
#                        if creds and creds.expired and creds.refresh_token:
#                                creds.refresh(Request())
#                        else:
#                                flow = InstalledAppFlow.from_client_secrets_file(self.creds_json, self.SCOPES)
#                                creds = flow.run_local_server(port=0)
#                        # Save the credentials for the next run
#                        with open(self.PICKLE_TOKEN_FILE, 'wb') as token:
#                                pickle.dump(creds, token)
#
