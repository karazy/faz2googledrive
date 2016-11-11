from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from oauth2client.service_account import ServiceAccountCredentials

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/drive.file'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'FAZ 2 Google Drive'
MIME_TYPE = 'application/pdf'
UPLOAD_FOLDER_ID = '0B2jwM0WcLmizNVNLMHhyTDltZDA'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    print('Validating credentials')
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'faz-drive-uploader.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        print('No credentials found. Authorize.')
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def getServiceCredentials():
    print('Validating service credentials')
    credentials = ServiceAccountCredentials.from_json_keyfile_name('faz2drive-81a367166595.json', scopes=SCOPES)
    return credentials


def upload(filename):
    """Shows basic usage of the Google Drive API.

    Creates a Google Drive API service object and outputs the names and IDs
    for up to 10 files.
    """
    #credentials = get_credentials()
    credentials = getServiceCredentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)
    
    file_loc = '../downloads/' + filename

    #for filename, mimeType in FILES:
    metadata = {'name': 'FAZ_' + filename}
    metadata['mimeType'] = MIME_TYPE
    metadata['parents'] = [UPLOAD_FOLDER_ID]
    #if mimeType:        
    #Upload file   
    res = service.files().create(body=metadata, media_body=file_loc).execute()
    if res:
        print('Uploaded "%s" (%s)' % (filename, res['mimeType']))
    else:
        print('No respsonse from Google Drive')
    #
    #results = service.files().list(
     #   pageSize=10,fields="nextPageToken, files(id, name)").execute()
    #items = results.get('files', [])
    #if not items:
    #    print('No files found.')
    #else:
    #    print('Files:')
    #    for item in items:
    #        print('{0} ({1})'.format(item['name'], item['id']))

def main():
    get_credentials()

if __name__ == '__main__':
    main()

