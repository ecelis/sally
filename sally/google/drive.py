import sally.google.authorize as authorize

def get_uploads():
    service = authorize.get_service('drive', 'v3')
    results = service.files().list(
            pageSize=10,fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])
    if not items:
        print('No files found')
    else:
        print('Files:')
        for item in items:
            print('{0} ({1})'.format(item['name'], item['id']))
