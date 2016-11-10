'''
Created on Nov 1, 2013

@author: pete
'''
import requests
import datetime
import json
import urlparse3
import os
import google_drive as gdrive

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

    def __init__(self, faz_login, drive_config):
        '''
        @param faz_login: tuple of FAZ login information (user, password)
        @param drive_config: tuple of Gmail login information (user, password)
        '''
        self.fazLogin = faz_login
        self.drive_config = drive_config
        
        # path to store pdf files
        self.storePath = "../downloads/"
        
        # download FAZ with rhein main part
        self.downloadRMZ = False
        # download FAZ only
        self.downloadFAZ = True
        # if new files were downloaded, send them directly to kindle
        self.download2Kindle = False
        
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

    def download(self, year, month, day, rmz = False):
        url = self.getDownloadLink( year, month, day, rmz)
        
        # if link could not be extracted
        if(not url):
            print ("No download link could be found for %d-%02d-%02d" % (year, month, day))
            return False
        
        # get file name from url
        filename =  url.split('/', )[-1]
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

        self.upload2Drive(filename)
        return True
    
    def getDownloadLink(self, year, month, day, rmz = False):
        s_year = str(year)
        s_month = "%02d" % (month)
        s_day = "%02d" % (day)
        if(rmz):
            url_base = "http://www.faz.net/e-paper/epaper/pdf/FAZ_RMZ/"
            url = "http://www.faz.net/e-paper/epaper/overview/FAZ_RMZ/%s-%s-%s" % (s_year, s_month, s_day)
        else:
            url_base = "http://www.faz.net/e-paper/epaper/pdf/FAZ/"
            url = "http://www.faz.net/e-paper/epaper/overview/FAZ/%s-%s-%s" % (s_year, s_month, s_day)
        req = self.s.get(url)
        
        # if status not ok, return false
        if(req.status_code != 200):
            return False

        json_info = json.loads(req.text)
        pdf_name = json_info["ausgabePdf"]
        
        dl_url = "%s%s-%s-%s/%s"  % (url_base, s_year, s_month, s_day, pdf_name)
        return dl_url

    def downloadAvailable(self):
        url = "http://www.faz.net/e-paper/epaper/list/FAZ"
        req = self.s.get(url)
        if(req.status_code != 200):
            return False
        json_info = json.loads(req.text)
        for i in range(0, len(json_info)):
            # check all available publications
            entities = json_info[i]["ausgaben"]
            for entity in entities: 
                # extract date
                date = entity["displayDatum"]
                day, month, year = date.split(".")
                day = int(day)
                month = int(month)
                year = int(year)
                if entity["typ"] == "FAZ" and self.downloadFAZ:
                    self.download(year, month, day, False)
                if entity["typ"] == "FAZ_RMZ" and self.downloadRMZ:
                    self.download(year, month, day, True)
    
    def upload2Drive(self, filename):        
        print ("Upload file to Google Drive")
        gdrive.upload(filename)