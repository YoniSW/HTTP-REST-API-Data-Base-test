import os
import sys
import urllib.request
import base64
import pytest
import json


URL_BASE = 'http://localhost:8000/players'


class RestApi:
    """
    This class will generate basic HTTP REST API properties.
    """
    def __init__(self, url, page_start=False, user='admin', passw='admin'):
        """
        @param::url - API url string 
        @param::page_start - if exists
        """
        self.url_base = url
        self.page = page_start
        self.url = self.set_url(self.page)
        self.user_name = user
        self.password = passw
    
    
    def set_url(self, page):
        """
        The function will set url to next page
        """
        if not page:
            url = self.url_base
        else:
            url = ('{}?page={}'.format(self.url_base, self.page))
        
        return url


def install_modules():
    os.system('''wget https://bootstrap.pypa.io/get-pip.py''')
    os.system('''export PATH="$PWD/.local/bin:$PATH"''')
    os.system('''python get-pip.py''')
    os.system('sudo easy_install pip')


def run_server():
    os.system("wget -O twtask https://drive.google.com/u/0/uc?id=1V4pn_Ydu6Pzudju0tFMXqKoR0gzQyeqg&export=download")
    os.system("chmod 755 twtask")
    ## TODO: run server in defferent thread

    

def main():
    """
    out_file_path='data'
    with urllib.request.urlopen(req) as response, open(out_file_path, 'wb') as out_file:
        data = response.read()
        out_file.write(data)

    """
    Players=RestApi(URL_BASE,1)
    credentials = ('%s:%s' % (Players.user_name, Players.password))
    encoded_credentials = base64.b64encode(credentials.encode('ascii'))
    req = urllib.request.Request(Players.url)
    print ('Players.url: {}'.format(Players.url))
    req.add_header('Authorization', 'Basic %s' % encoded_credentials.decode("ascii"))

    try:
        with urllib.request.urlopen(req) as response:
            data_bytes = response.read()
            data_list = json.loads(data_bytes.decode("utf-8").replace("'", '"'))
            data_json = json.dumps(data_list, indent=4, sort_keys=True)
            print (data_json)
           
    except Exception as e:
            print ('YONI: {}'.format(e))




if __name__ == '__main__':
    assert float('.'.join(map(str,sys.version_info[:2]))) > 3.6, 'python version is too old: {}'.format(sys.version_info[:2])
    main()
