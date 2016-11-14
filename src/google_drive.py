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
APPLICATION_NAME = 'FAZ 2 Google Drive'
MIME_TYPE = 'application/pdf'


def getServiceCredentials(delegate, keyFile):
    print('Validating service credentials')
    credentials = ServiceAccountCredentials.from_json_keyfile_name(keyFile, scopes=SCOPES)
    delegated_credentials = credentials.create_delegated(delegate)
    return delegated_credentials


def upload(filename, file_folder, upload_folder_id, delegate, keyFile):
    credentials = getServiceCredentials(delegate, keyFile)
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)
    
    file_loc = file_folder + filename

    #for filename, mimeType in FILES:
    metadata = {'name': 'FAZ_' + filename}
    metadata['mimeType'] = MIME_TYPE
    metadata['parents'] = [upload_folder_id]
    #if mimeType:        
    #Upload file   
    res = service.files().create(body=metadata, media_body=file_loc).execute()
    if res:
        print('Uploaded "%s" (%s)' % (filename, res['mimeType']))
    else:
        print('No respsonse from Google Drive')
