'''
Created on Nov 1, 2013
This is a sample which downloads your files to downloads/ and sends new
files to your Kindle

Attention: It requires a valid e-paper abonement of FAZ.net

@author: pete
'''
import faz2drive

# FAZ login data
FAZ_USER = "USERNAME"
FAZ_PASS = "PASSWORD"

# Google Drive upload folder ID
DRIVE_UPLOAD_FOLDER_ID = 'FOLDER_ID'

fazload = faz2drive.FazLoader((FAZ_USER, FAZ_PASS), (DRIVE_UPLOAD_FOLDER_ID))
fazload.downloadAvailable()
