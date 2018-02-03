# -*- coding: utf-8 -*-
"""Google spreadsheets interface for Sally crawler."""
import os
import logging
from crabs.google import authorize

logger = logging.getLogger(__name__)


def get_spreadsheet(spreadsheetId):
    """Return an existing spreadsheet given by the ID."""
    service = authorize.get_service('sheets', 'v4')
    request = service.spreadsheets().get(
        spreadsheetId=spreadsheetId,
        ranges=[], includeGridData=False)
    response = request.execute()
    return response


def create_spreadsheet(title):
    """Return a new spreadsheet with given _title_."""
    service = authorize.get_service('sheets', 'v4')
    body_ = {
        "properties": {
            "title": title
        }
    }

    request = service.spreadsheets().create(body=body_)
    response = request.execute()
    return response


def create_sheet(spreadsheetId, title):
    """Return a new sheet with given _title_ at given spreadsheet ID."""
    body = {
        "addSheet": {
            "properties": {
                "title": title,
                "gridProperties": {
                    "rowCount": 100,
                    "columnCount": 9,
                    "frozenRowCount": 1
                    }
                }
            }
        }
    service = authorize.get_service('sheets', 'v4')
    request = service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheetId,
        body={'requests': [body]})
    response = request.execute()
    return response


def insert_to(
        spreadsheetId,
        sheet,
        rows=[['', '', '', '', '', '', '', '']],
        offset=1):
    """
    Insert a new item in a google spreadsheet. Return updated spreadshet.

    Arguments:
    spreadsheetId - ID of target spreadsheet
    row - I.E. [SCORE,URL,OFFER,META,TELEPHONE,EMAIL,ECOMMERCE,SHOPING CART,
        SOCIAL NETWORKS, LOCATION, CRAWLING DATE]
    offsset - row number to skip in spreadsheet before insert, like in headers
    """
    service = authorize.get_service('sheets', 'v4')
    rangeName = sheet + '!A' + str(offset)
    value_input_option = 'RAW'
    body = {'values': rows}
    response = service.spreadsheets().values().update(
        spreadsheetId=spreadsheetId, range=rangeName,
        valueInputOption=value_input_option, body=body).execute()
    return response


def get_settings(spreadsheetId=os.environ['SALLY_SETTINGS_ID']):
    """Return crawler settings from given spreadsheet ID."""
    range_ = 'settings!A1:G1000'
    service = authorize.get_service('sheets', 'v4')
    request = service.spreadsheets().values().get(
        spreadsheetId=spreadsheetId,
        range=range_, majorDimension='COLUMNS',
        valueRenderOption='UNFORMATTED_VALUE',
        dateTimeRenderOption='FORMATTED_STRING')
    response = request.execute()
    logger.debug(response)
    settings = {
        "allowed_domains": response['values'][0][1:],
        "disallowed_domains": response['values'][1][1:],
        "allowed_keywords": response['values'][2][1:],
        "disallowed_keywords": response['values'][3][1:],
        "networks": response['values'][4][1:],
        "ecommerce": response['values'][5][1:],
        "allowed_countries": response['values'][6][1:]
        }
    return settings


def get_urls(spreadsheetId):
    """Return URLs to crawl from given Google spreadsheet ID."""
    range_ = 'A1:A1000'
    try:
        service = authorize.get_service('sheets', 'v4')
        request = service.spreadsheets().values().get(
            spreadsheetId=spreadsheetId,
            range=range_,
            majorDimension='COLUMNS',
            valueRenderOption='UNFORMATTED_VALUE',
            dateTimeRenderOption='FORMATTED_STRING')
        response = request.execute()
        logger.debug(response['values'][0])
        return response['values'][0]
    except Exception as ex:
        logger.error(ex, exc_info=True)
        return []


def get_score(spreadsheetId=os.environ['SALLY_SETTINGS_ID']):
    """Return score values from given Google spreadsheet ID."""
    range_ = 'score!A2:B1000'
    service = authorize.get_service('sheets', 'v4')
    request = service.spreadsheets().values().get(
        spreadsheetId=spreadsheetId,
        range=range_,
        majorDimension='ROWS',
        valueRenderOption='UNFORMATTED_VALUE',
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
        "cart": response['values'][6][1],
        "likes": response['values'][7][1]
        }
    return score
