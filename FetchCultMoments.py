from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import Utils

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def FetchCultMoments(savedirp):
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)

    messages = Utils.ListMessagesMatchingQuery(service, 'me', query='subject:Your Cult Moment of the day is here')
    for message in messages:
        m = Utils.GetMessage(service, 'me', message['id'])
        r = Utils.SaveMomentOfTheDay(m, savedirp)
        if r is True:
            print('Done fetching all Moments.')
            break
 

if __name__ == '__main__':
    from sys import argv, exit
    savedirp = argv[1] if len(argv) > 1 else None
    if not savedirp or not os.path.isdir(savedirp):
        print('Usage: FetchCultMoments /path/to/save/moments/')
        exit(1)
    FetchCultMoments(argv[1])
