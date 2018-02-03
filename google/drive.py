import logging
import sally.google.authorize as authorize

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

def get_uploads(folder_id):
    service = authorize.get_service('drive', 'v3')
    results = service.files().list(
            pageSize=100,fields="nextPageToken, files(id, name, mimeType)",
            q="'%s' in parents and mimeType != 'application/vnd.google-apps.folder'"
            % folder_id).execute()
    items = results.get('files', [])
    return items


def get_files(folder_id):
    service = authorize.get_service('drive', 'v3')
    results = service.files().list(
            pageSize=100,fields="nextPageToken, files(id, name, mimeType)",
            q="'%s' in parents and mimeType != 'application/vnd.google-apps.folder'"
            % folder_id).execute()
    items = results.get('files', [])
    return items




def mv(file_id, to_folder):
    try:
        service = authorize.get_service('drive', 'v3')
        # retrieve the existing parents to remove
        file_ = service.files().get(fileId=file_id, fields='parents').execute()
        previous_parents = ','.join(file_.get('parents'))
        # Move the file to the new folder
        file_ = service.files().update(fileId=file_id,
                removeParents=previous_parents,
                addParents=to_folder,
                fields='id, parents').execute()

        return file_
    except Exception as ex:
        logger.error("Can't mv file in drive: %s" % ex, exc_info=True)
        return None
