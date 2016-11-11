'''
Created on Nov 1, 2013
This is a sample which downloads your files to downloads/ and sends new
files to your Kindle

Attention: It requires a valid e-paper abonement of FAZ.net

@author: karazy
'''
import faz2drive
import configparser

config = configparser.ConfigParser()
config.read('env.cfg')

# FAZ login data
FAZ_USER = config['FAZ']['Username']
FAZ_PASS = config['FAZ']['Password']

# Google Drive upload folder ID
DRIVE_UPLOAD_FOLDER_ID = config['DRIVE']['Upload_folder_id']
DRIVE_DELEGATE = config['DRIVE']['Delegate']

print ('Starting faz2googledrive...')
print ('Requesting downloads for {} and saving them to {}'.format(FAZ_USER, DRIVE_UPLOAD_FOLDER_ID))

fazload = faz2drive.FazLoader((FAZ_USER, FAZ_PASS), (DRIVE_UPLOAD_FOLDER_ID, DRIVE_DELEGATE))
fazload.downloadAvailable()

#TODO
# - improve app auth
# - improve date check?
# - cleanup and docs