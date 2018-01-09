from __future__ import print_function

import datetime
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
## TODO flags comes from sheets quickstart, check and remove if needed
flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Sally'

G_PRODUCT='sheets'
G_API='v4'


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
                                   'sheets.googleapis.com-python-quickstart.json')

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


def get_service():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/rest?'
                    'version=v4')
    #to avoid ImportError: file_cache is unavailable when using oauth2client >= 4.0.0
    # https://github.com/google/google-api-python-client/issues/299
    service = discovery.build(G_PRODUCT, G_API, http=http,
            discoveryServiceUrl=discoveryUrl, cache_discovery=False)

    return service


def get_spreadsheet(spreadsheetId):
    service = get_service()
    request = service.spreadsheets().get(spreadsheetId=spreadsheetId, ranges=[],
            includeGridData=False)
    response = request.execute()
    return response


def create_sheet(spreadsheetId, sheet):
    body = {
            "addSheet": {
                "properties": {
                    "title": sheet,
                    "gridProperties": {
                        "rowCount": 100,
                        "columnCount": 9
                        }
                    }
                }
            }
    service = get_service()
    request = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheetId,
            body={ 'requests': [body] })
    response = request.execute()
    return response

def insert_to(spreadsheetId, sheet, rows=[['','','','','','','','']], offset=2):
    """Insert a new scraped site in a google spreadsheet

    spreadsheet = spreadsheet_ID
    row = [CALIFICACION,SITIO,OFERTA,TELÉFONO,EMAIL,ECOMMERCE,LUGAR,FECHA]
    offsset = row number to insert
    """
    service = get_service()

    rangeName = sheet + '!A' + str(offset)
    majorDimension = 'ROWS'
    value_input_option = 'RAW' ## USER_ENTERED
    today = datetime.datetime.now().strftime('%m/%d/%Y')
    body = { 'values': rows }
    result = service.spreadsheets().values().update(
        spreadsheetId=spreadsheetId, range=rangeName,
        valueInputOption=value_input_option, body=body).execute()
    # {'updatedRows': 2, 'updatedRange': 'Sheet1!A2:H3', 'spreadsheetId': '1AxioUWtPJItfnv--JxNg5-oiUUMJgW4uoQopx-JlH00', 'updatedCells': 16, 'updatedColumns': 8}
    # TODO log this
    print('{0} cells updated.'.format(result.get('updatedRows')))
    return result
