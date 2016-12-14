'''
Execute the FAZ download and Google Drive upload process

Attention: It requires a valid e-paper abonement of FAZ.net

@author: karazy
'''
import faz2drive
import configparser
import os

config = configparser.ConfigParser()
config_file = os.path.join(os.path.dirname(__file__), 'env.cfg')
config.read(config_file)

# FAZ login data
FAZ_USER = config['FAZ']['Username']
FAZ_PASS = config['FAZ']['Password']

# Google Drive upload folder ID
DRIVE_UPLOAD_FOLDER_ID = config['DRIVE']['Upload_folder_id']
#Drive E-Mail of Google Apps user that is owner of the folder
DRIVE_DELEGATE = config['DRIVE']['Delegate']
#Google Service Account key file used for authentication
DRIVE_KEY_FILE = config['DRIVE']['Key_file']

print ('Starting faz2googledrive...')
print ('Requesting downloads for FAZ user {} and saving them to {} for delegate {}'.format(FAZ_USER, DRIVE_UPLOAD_FOLDER_ID, DRIVE_DELEGATE))

fazload = faz2drive.FazLoader((FAZ_USER, FAZ_PASS), (DRIVE_UPLOAD_FOLDER_ID, DRIVE_DELEGATE, DRIVE_KEY_FILE))
fazload.downloadAvailable()