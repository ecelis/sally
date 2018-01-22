import logging
import sally.google.authorize as authorize

def get_uploads(folder_id):
    service = authorize.get_service('drive', 'v3')
    results = service.files().list(
            pageSize=100,fields="nextPageToken, files(id, name, mimeType)",
            q="'%s' in parents and mimeType != 'application/vnd.google-apps.folder'"
            % folder_id).execute()
    items = results.get('files', [])
    return items
# application/vnd.google-apps.spreadsheet

