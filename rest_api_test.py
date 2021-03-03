import os
import sys
from datetime import datetime
import urllib.request
import base64
import pytest
import json
import threading


URL_BASE = 'http://localhost:8000/players'


class RestApi:
    """
    This class will generate basic HTTP REST API properties.
    """
    def __init__(self, url, user='admin', passw='admin'):
        """
        @param::url - API url string 
        """
        self._url = None
        self.url_base = url
        self.user_name = user
        self.password = passw
    

    @property
    def url(self):
        return self._url


    @url.setter
    def url(self, page):
        if not page:
            self._url = self.url_base
        else:
            self._url = ('{}?page={}'.format(self.url_base, page))
     

    @url.deleter
    def url(self):
        del self._url

        

def authorized_request(req, encoded_credentials):
    """
    @param::encoded_credentials - ascii format credentials
    """
    req.add_header('Authorization', 'Basic %s' % encoded_credentials.decode("ascii"))
    

def install_modules():
    """
    If modules not installed in your VM
    """
    os.system('''wget https://bootstrap.pypa.io/get-pip.py''')
    os.system('''export PATH="$PWD/.local/bin:$PATH"''')
    os.system('''python get-pip.py''')
    os.system('''sudo easy_install pip''')
    os.system('''pip install pytest==2.9.1''')


def run_server():
    """
    run Linux executable, if needed, clone the file first.
    """
    if not os.path.isfile('twtask'):
        os.system("wget -O twtask https://drive.google.com/u/0/uc?id=1V4pn_Ydu6Pzudju0tFMXqKoR0gzQyeqg&export=download")
    
    os.system("chmod 755 twtask")
    os.system("./twtask")
    ## TODO: run server in defferent thread
    print ('###### twtask #######')
    pass



def main():
    """
    out_file_path='data'
    with urllib.request.urlopen(req) as response, open(out_file_path, 'wb') as out_file:
        data = response.read()
        out_file.write(data)

    """
    t1 = threading.Thread(target=run_server, args=[])
    t1.start()
    page=1
    no_error=True
    Players=RestApi(URL_BASE)
    credentials = ('%s:%s' % (Players.user_name, Players.password))


    while no_error and page<200000:
        Players.url = page
        req = urllib.request.Request(Players.url)
        authorized_request(req, base64.b64encode(credentials.encode('ascii')))
        print (Players.url)
        del Players.url
        try:
            with urllib.request.urlopen(req) as response:
                data_bytes = response.read()
                data_list = json.loads(data_bytes.decode("utf-8").replace("'", '"'))
                data_json = json.dumps(data_list, indent=4, sort_keys=True)
                #print (data_json)
                page += 1
        
        except Exception as e:
                print ('ERROR handler: {}'.format(e))
                if '111' in str(e):
                    t1 = threading.Thread(target=run_server, args=[])
                    t1.start()
                    continue
                else:
                    no_error = False
                
        
    
    print ('Checked {} pages'.format(page))




if __name__ == '__main__':
    
    assert float('.'.join(map(str,sys.version_info[:2]))) > 3.6, 'python version is too old: {}'.format(sys.version_info[:2])
    start_time = datetime.now()
    main()
    print('Execution time: ' + str(datetime.now() - start_time) + 'ms')