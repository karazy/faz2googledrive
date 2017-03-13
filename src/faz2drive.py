import requests
import datetime
import json
import os
import google_drive as gdrive
import time
import errno
import re

# debian hack
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
import ssl


# hack for older debian version according to
# http://stackoverflow.com/questions/14102416/python-requests-requests-exceptions-sslerror-errno-8-ssl-c504-eof-occurred
class MyAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block):
        self.poolmanager = PoolManager(num_pools=connections,
                                       maxsize=maxsize, 
                                       ssl_version=ssl.PROTOCOL_TLSv1)

class FazLoader(object):

    STORE_PATH = "downloads/"

    def __init__(self, faz_login, drive_config):
        '''
        @param faz_login: tuple of FAZ login information (user, password)
        @param drive_config: tuple of Gmail login information (user, password, delegate, key file)
        '''
        self.fazLogin = faz_login
        self.drive_config = drive_config
        
        # path to store pdf files
        
        self.storePath = os.path.join(os.path.dirname(__file__), FazLoader.STORE_PATH) 

        self.make_sure_path_exists(self.storePath)
        
        # download FAZ with rhein main part
        self.downloadRMZ = True
        # download FAZ only
        self.downloadFAZ = True
        
        self.s = requests.Session()
        self.s.mount('https://', MyAdapter())
        
        data = {"loginUrl": "/mein-faz-net/", 
                  "redirectUrl": "/e-paper/",
                  "loginName" : self.fazLogin[0],
                  "password" : self.fazLogin[1]
                  }
        req = self.s.post("https://www.faz.net/membership/loginNoScript", data)
        req = self.s.get("http://www.faz.net/e-paper/")
        
    def _deletePrevious(self, filename):
        f_time = filename[-8:-4]
        f_date = filename[0:8]
        found_older = False
        pdf_files = [f for f in os.listdir(self.storePath) if f.endswith('.pdf')]
        for pdf_file in pdf_files:
            pdff_time = pdf_file[-8:-4]
            pdff_date = pdf_file[0:8]
            
            # same version but one file is older: 
            if(pdff_date == f_date and filename != pdf_file):
                # delete older file
                found_older = True
                os.remove(self.storePath+pdf_file)
                print ("removed older version of " + filename + ": "+pdf_file)
        return found_older



    def download(self, downloadId, isoDate):
        baseUrl = 'http://epaper.faz.net/epaper/download/'

        url = baseUrl + downloadId

        filename = isoDate + '.pdf'
        if os.path.isfile(self.storePath + filename):
            print ("File " + filename +" already exists")
            return False
        
        print ("Downloading to " + filename)
        req = self.s.get(url,stream=True)
        f = open(self.storePath + filename, "wb")
        for chunk in req.iter_content(chunk_size=20*1024): 
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
                f.flush()
        f.close()

        # remove previous versions
        found_prev = self._deletePrevious(filename)        
        keyFile = os.path.join(os.path.dirname(__file__), self.drive_config[2]) 

        self.upload2Drive(filename, self.drive_config[0], self.drive_config[1], keyFile)
        self.removeDownload(filename)
        return True


    def downloadAvailable(self):
        currentDate = (time.strftime("%d.%m.%Y"))
        isoDate = (time.strftime("%Y-%m-%d"))
        dayOfWeek = datetime.datetime.today().weekday()

        downloadId = self.getDownloadId(currentDate, dayOfWeek)        

        #self.download(year, month, day, False)
        self.download(downloadId, isoDate)
    

    def getDownloadId(self, currentDate, dayOfWeek):

        url = "http://epaper.faz.net/api/epaper/change-release-date"
        headers = {
            'Accept': 'application/json',
            'Content-Type':'application/json',
            'X-Requested-With': 'XMLHttpRequest'
            }

        if dayOfWeek == 6:
            print('It is Sunday. Time for FAS.')
            payload = {'slug': 'FAS', 'releaseDate': currentDate}
        else:
            payload = {'slug': 'FAZ', 'releaseDate': currentDate}

        
        req = self.s.post(url, json=payload, headers=headers)
        
        if(req.status_code != 200):
            print('Failed to retrieve download id. Status {}'.format(req.status_code))
            return False
        else:
            json_info = json.loads(req.text) 
            if len(json_info) == 0:
                print('No FAZ/FAS publications found.')   
            
            content =  json_info['htmlContent']
            return self.extractDownloadId(content)
    

    def extractDownloadId(self, content):
        m = re.search('/webreader/(\d+)', content)
        id = m.group(1)
        
        return id
    

    
    def upload2Drive(self, filename, upload_folder_id, delegate, kef_file):        
        print ("Upload file to Google Drive")
        gdrive.upload(filename, self.storePath, upload_folder_id, delegate, kef_file)


    def make_sure_path_exists(self, path):
        try:
            os.makedirs(path, exist_ok=True)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

    def removeDownload(self, filename):        
        os.remove(self.storePath + '/' + filename)
        print('Removed download file  {}'.format(filename))