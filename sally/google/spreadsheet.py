import os
import sys
import datetime
import logging
from sally.google import authorize

logger = logging.getLogger(__name__)


def get_spreadsheet(spreadsheetId):
    service = authorize.get_service('sheets', 'v4')
    request = service.spreadsheets().get(spreadsheetId=spreadsheetId, ranges=[],
            includeGridData=False)
    response = request.execute()
    return response


def create_spreadsheet(name):
    service = authorize.get_service('sheets', 'v4')
    body_ = {
        "properties": {
            "title": name
        }
    }

    request = service.spreadsheets().create(body=body_)
    response = request.execute()
    return response


def create_sheet(spreadsheetId, sheet):
    body = {
            "addSheet": {
                "properties": {
                    "title": sheet,
                    "gridProperties": {
                        "rowCount": 100,
                        "columnCount": 9,
                        "frozenRowCount": 1
                        }
                    }
                }
            }
    service = authorize.get_service('sheets', 'v4')
    request = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheetId,
            body={ 'requests': [body] })
    response = request.execute()
    return response


def insert_to(spreadsheetId, sheet, rows=[['','','','','','','','']], offset=1):
    """Insert a new scraped site in a google spreadsheet

    spreadsheet = spreadsheet_ID
    row = [CALIFICACION,SITIO,OFERTA,TELÉFONO,EMAIL,ECOMMERCE,LUGAR,FECHA]
    offsset = row number to insert
    """
    service = authorize.get_service('sheets', 'v4')

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
    return result


def get_settings(spreadsheetId=os.environ['SALLY_SETTINGS_ID']):
    range_ = 'settings!A1:F1000'
    service = authorize.get_service('sheets', 'v4')
    request = service.spreadsheets().values().get(spreadsheetId=spreadsheetId,
            range=range_, majorDimension='COLUMNS', valueRenderOption='UNFORMATTED_VALUE',
            dateTimeRenderOption='FORMATTED_STRING')
    response = request.execute()
    settings = {
            "allowed_domains": response['values'][0][1:],
            "disallowed_domains": response['values'][1][1:],
            "allowed_keywords": response['values'][2][1:],
            "disallowed_keywords": response['values'][3][1:],
            "networks": response['values'][4][1:],
            "ecommerce": response['values'][5][1:]
            }
    return settings


def get_urls(spreadsheetId):
    range_ = 'A1:A1000'
    service = authorize.get_service('sheets', 'v4')
    request = service.spreadsheets().values().get(spreadsheetId=spreadsheetId,
            range=range_, majorDimension='COLUMNS', valueRenderOption='UNFORMATTED_VALUE',
            dateTimeRenderOption='FORMATTED_STRING')
    response = request.execute()
    logger.debug(response['values'][0])
    return response['values'][0]


def get_score(spreadsheetId=os.environ['SALLY_SETTINGS_ID']):
    range_ = 'score!A2:B1000'
    service = authorize.get_service('sheets', 'v4')
    request = service.spreadsheets().values().get(spreadsheetId=spreadsheetId,
            range=range_, majorDimension='ROWS', valueRenderOption='UNFORMATTED_VALUE',
            dateTimeRenderOption='FORMATTED_STRING')
    response = request.execute()
    logger.debug(response)
    score = {
            "email": response['values'][0][1],
            "telephone": response['values'][1][1],
            "ecommerce": response['values'][2][1],
            "offer": response['values'][3][1],
            "network": response['values'][4][1],
            "secure_url": response['values'][5][1],
            "cart": response['values'][6][1]
            }
    return score
