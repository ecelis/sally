from __future__ import print_function

import datetime
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets https://www.googleapis.com/auth/drive'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Sally'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sally.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def get_service(service, api_version):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    if service is 'sheets':
        discoveryUrl = ('https://%s.googleapis.com/rest?'
            'version=%s' % (service, api_version))
        service_response = discovery.build(service, api_version, http=http,
            discoveryServiceUrl=discoveryUrl, cache_discovery=False)
    #to avoid ImportError: file_cache is unavailable when using oauth2client >= 4.0.0
    # https://github.com/google/google-api-python-client/issues/299
    else:
        service_response = discovery.build(service, api_version, http=http,
            cache_discovery=False)
    return service_response

if __name__ == '__main__':
    get_credentials()
