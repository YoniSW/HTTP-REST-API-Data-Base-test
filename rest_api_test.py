import os
import sys
import pdb
from datetime import datetime
import urllib.request
import urllib3.util
import base64
import pytest
import json


# Test global viarables
total_pairs = dict()
uniq_pairs = dict()

# Test Parameters
TEST_OUTPUT='playerApi_files'
JSON_OUTPUT='json_files'


class RestApi:
    """
    This class will generate basic HTTP REST API properties.
    """
    def __init__(self, url='http://localhost:8000/players', user='admin', passw='admin'):
        """
        @param::url - API url string 
        """
        self._url = None
        self.url_base = url
        self.page = 1
        self.user_name = user
        self.password = passw

        # configuration
        self.THREADS = 10
        self.TIMEOUT = 15
        self.RETRIES = 1
        self.REDIRECTS = 0

        # init our timeout/retry objects
        self.timeout = urllib3.util.Timeout(connect=self.TIMEOUT, read=self.TIMEOUT)
        self.retries = urllib3.util.Retry(connect=self.RETRIES, read=self.RETRIES, redirect=self.REDIRECTS)

        # init our PoolManager
        self.http = urllib3.PoolManager(
            retries=self.retries,
            timeout=self.timeout,
            num_pools=self.THREADS,
            maxsize=self.THREADS,
            block=True
        )
    

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

    
def install_modules():
    """
    If modules not installed in your VM
    """
    os.system('''wget https://bootstrap.pypa.io/get-pip.py''')
    os.system('''export PATH="$PWD/.local/bin:$PATH"''')
    os.system('''python get-pip.py''')
    os.system('''sudo easy_install pip''')
    os.system('''pip install pytest==2.9.1''')


def run_web_server(url='https://drive.google.com/u/0/uc?id=1V4pn_Ydu6Pzudju0tFMXqKoR0gzQyeqg&export=download', file_name='twtask'):
    """
    run Linux executable process on background, if needed, deal with clone & permissions.
    """
    if not os.path.isfile('twtask'):
        os.system("wget -O {} {}".format(file_name,url))
    
    os.system("chmod 755 {}".format(file_name))
    command='./{}'.format(file_name)
    os.spawnl(os.P_NOWAIT, *command)


#py.test -m pymodules
@pytest.mark.pymodules
def test_py_modules():
    # TODO: implement function
    print ('')


#py.test -m pyversion
@pytest.mark.pyversion
def test_py_version():
    assert float('.'.join(map(str,sys.version_info[:2]))) > 3.6, 'python version is too old: {}'.format(sys.version_info[:2])


def request(P):
    """
    @param::http - Object
    @param::url - desired url 
    """
    try:
        headers = urllib3.make_headers(basic_auth='{}:{}'.format(P.user_name,P.password))
        response = P.http.request('GET', P.url,headers=headers)
        data_bytes=response.data
        data_list = sorted(json.loads(data_bytes.decode("utf-8").replace("'", '"')), key=lambda a: list(a.keys()))
        
        with open('{}/page_{}.json'.format(JSON_OUTPUT,P.page), 'w') as d:
            d.write(json.dumps(data_list))
        print (P.url)
        return (data_list, response.status)
    except Exception: # SSL error, timeout, host is down, firewall block, etc.
        return (data_list, response.status)


def add_uniq_pairs(player, page):
    """
    @param::player - name and ID
    Function will add a player to uniq_pairs only if doesn't exist
    """
    uniq_pairs['{}/{}'.format(player['Name'],player['ID'])]= page



def add_total_pairs(player, page):
    """
    @param::player - name and ID
    Function will add a player to full_pairs list with page number
    Format:: {name: [[page, ID1], [page, ID2]......[page, IDn]]}
    """
    if total_pairs.get(player['Name']) is None:
        total_pairs[player['Name']] = list()
        total_pairs[player['Name']].append((page,player['ID']))
        return
    
    total_pairs[player['Name']].append((page,player['ID']))


def dump_database_to_structure(data, page):
    for player in data:
        add_uniq_pairs(player, page)
        add_total_pairs(player, page)


def test_illegal_name():
    """
    @param::player - name and ID
    Function return true if: 
    """
    defected_name = []
    lst = total_pairs.get("")
    lst += total_pairs.get('null')
    if len(lst) > 1:
        for i in total_pairs.get(""):
            defected_name.append('{}/{}'.format(i[0], i[1]))

    assert len(defected_name) < 1, 'Test fail, {} illegal names in page/id: {}'.format(len(defected_name),defected_name)


def test_illegal_id():
    """
    @param::player - name and ID
    Function return true if: 
    """
    defected_id = []
    for key in total_pairs:
        if len(total_pairs[key])==1:
            if total_pairs[key][0][1] == '':
                defected_id.append('{}/{}'.format(total_pairs[key][0][0], key))
        else:
            for pair in total_pairs[key]:
                if pair[1] == '':
                    defected_id.append('{}/{}'.format(pair[0], key))

    assert len(defected_id) < 1, 'Test fail, empty ID in page/name: {}'.format(defected_name)


def test_one_2_one_name(player):
    """
    @param::player - name and ID
    Function return true if: 
    """
    if uniq_pairs.get(player['Name']): 
        if player['ID'] != uniq_pairs[player['Name']]:
            return True

    else:
        uniq_pairs[player['Name']]=player['ID']
    
    return False


def test_one_2_one_id(player):
    """
    @param::player - name and ID
    Function return true if: 
    """
    
    if player['ID'] != uniq_pairs[player['Name']]:
        return True

    else:
        uniq_pairs[player['Name']]=player['ID']
    
    return False



def main():
    status, no_page_change, prev_uniq_len, uniq_len = 200, 0, 0, -1
    Players=RestApi()
    
    # pull until we get teapot client error
    os.mkdir(JSON_OUTPUT)
    while status !=418 and no_page_change < 100:
        Players.url = Players.page
        data, status = request(Players)
        uniq_len = prev_uniq_len
        if uniq_len==prev_uniq_len: no_page_change+=1
        else: no_page_change=0&no_page_change
        dump_database_to_structure(data, Players.page)
        prev_uniq_len = uniq_len
        Players.page += 1

    try:
        test_illegal_id()
        test_illegal_name()
        
    except Exception as e:
        print (e)
    

    print ('Checked {} pages'.format(Players.page))
    print ('Found {} uniq pairs'.format(len(uniq_pairs)))
    print ('Found {} total pairs'.format(len(total_pairs)))

    with open('total_pairs', 'w') as d:
        for key in sorted(total_pairs):
            d.write('{}: {}\n'.format(key, set(total_pairs[key])))

    with open('uniq_pairs', 'w') as d:
        for key in uniq_pairs:
            d.write('{}: {}\n'.format(key, uniq_pairs[key]))


if __name__ == '__main__':
    test_py_version()
    run_web_server()
    #start_time = datetime.now()
    copy=1
    path = os.path.join(os.getcwd(), TEST_OUTPUT)
    while os.path.isdir(path+str(copy)): copy+=1
    path+=str(copy)
    os.mkdir(path)
    os.chdir(path)
    main()
    #print('Execution time: ' + str(datetime.now() - start_time) + 'ms')