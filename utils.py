from __future__ import print_function
import base64
import email
from apiclient import errors
from bs4 import BeautifulSoup
from datetime import datetime
import requests
import os


def ListMessagesMatchingQuery(service, user_id, query=''):
    """List all Messages of the user's mailbox matching the query.

    Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        query: String used to filter messages returned.
        Eg.- 'from:user@some_domain.com' for Messages from a particular sender.

    Returns:
        List of Messages that match the criteria of the query. Note that the
        returned list contains Message IDs, you must use get with the
        appropriate ID to get the details of a Message.
    """
    try:
        response = service.users().messages().list(userId=user_id,
                                                   q=query).execute()
        messages = []
        if 'messages' in response:
            messages.extend(response['messages'])

        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            response = service.users().messages().list(userId=user_id, q=query,
                                                       pageToken=page_token).execute()
            messages.extend(response['messages'])

        return messages
    except errors.HttpError, error:
        print('An error occurred: %s' % error)


def GetMessage(service, user_id, msg_id):
    """Get a Message with given ID.

    Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        msg_id: The ID of the Message required.

    Returns:
        A Message.
    """
    try:
        message = service.users().messages().get(userId=user_id, id=msg_id).execute()
        return message
    except errors.HttpError, error:
        print('An error occurred: %s' % error)


def GetMomentOfTheDay(m):
    """Get the MomentOfTheDay from Message sent by Cult

    Args:
        m: Message returned by GetMessage

    Returns:
        Dictionary like:
        {
            moment: 'https://.../.png',         # Url to the moment image
            class: 'S & C',                     # Workout Session
            center: 'Harlur'                    # Center Location
        }
    """
    body = bytes(str(m['payload']['body']['data']).encode('utf-8'))
    html = base64.urlsafe_b64decode(body)

    soup = BeautifulSoup(html, 'html.parser')
    src = soup.select('img[alt="Cult Moment of the day"]')[0]['src']
    klass, br, center = soup.select('span[style="color:#bbbbbb"]')[1].contents

    return {
        'moment': src,
        'class': klass.strip(),
        'center': center.strip()
    }


def SaveMomentOfTheDay(m, savedirp):
    """Saves moments to a directory if the moment has not already been saved

    Args:
        m: Message returned by GetMessage
        savedirp: Path to directory at which to save the moments

    Returns:
        Nothing
    """
    when = datetime.fromtimestamp(int(m['internalDate']) / 1000)
    when = when.strftime("%d-%m-%Y")

    mod = GetMomentOfTheDay(m)

    klass = mod['class'].replace(' | ', '_').replace(':', '.')
    center = mod['center']

    savep = os.path.join(savedirp, '%s_%s_%s.png' % (when, klass, center))

    if not os.path.exists(savep):
        r = requests.get(mod['moment'])

        if r.status_code == 200:
            if r.content:
                with open(savep, 'wb') as wf:
                    wf.write(r.content)
                print('Saved:', '"%s"' % savep)
            else:
                print('Fetched a blank moment!')
        else:
            print('Failed to fetch moment:', klass, mod['center'])
    else:
        print('Moment already fetched:', '"%s"' % savep)
