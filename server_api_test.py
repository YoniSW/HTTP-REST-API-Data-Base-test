#################################################
# Updated test: https://tinyurl.com/y8xwbt5v    #
# Contact: yonigoel@gmail.com                   #
#                                               #
#################################################

import os
import sys
import re
import pip
import csv
import urllib.request
import urllib3.util
import base64
import pytest
import json
#import selenium


# Test global viarables
total_pairs = dict()
uniq_pairs = dict()
errors=0

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


def save_to_csv(data_list, file_name, header=None):
    """
    Save the data sets using the file name
    @param::data_set - dict() to save into file
    @param::file_name - of the save data
    """
    global errors
    if len(data_list)==0:
        return
    errors+=1
    try:
        skip = 0
        with open(file_name, 'w') as csvfile:
            writer = csv.writer(csvfile , lineterminator='\n')
            for tup in data_list:
                try:
                    if header is not None:
                        writer.writerow(header)
                        header=None

                    writer.writerow(tup)
                except AttributeError:
                    skip +=1
                    continue
    except IOError:
        print("I/O error")
  

def run_web_server(url='https://drive.google.com/u/0/uc?id=1V4pn_Ydu6Pzudju0tFMXqKoR0gzQyeqg&export=download', file_name='twtask'):
    """
    run Linux executable process on background, if needed, deal with clone & permissions.
    """
    if not os.path.isfile('twtask'):
        os.system("wget -O {} {}".format(file_name,url))
    
    os.system("chmod 755 {}".format(file_name))
    command='./{}'.format(file_name)
    os.spawnl(os.P_NOWAIT, *command)


def request(P):
    """
    @param::P - RestApi object
    Function will send request to desired HTTP and return data & status_code 
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
    if uniq_pairs.get("%s/%s" % (player['Name'],player['ID'])) is None:
        uniq_pairs["%s/%s" % (player['Name'],player['ID'])] = page


def add_total_pairs(player, page):
    """
    @param::player - name and ID
    Function will add a player to full_pairs list with page number
    Format:: {name: [[page, ID1], [page, ID2]......[page, IDn]]}
    """
    values=player['Name']
    _id=player['ID']

    if total_pairs.get(values) is None:
        total_pairs[values] = list()
        total_pairs[values].append((page,_id))
        return
    
    if len(total_pairs.get(values)) == 1:
        if total_pairs.get(values)[0][1]!=_id:
            total_pairs[values].append((page,_id))
        return
    
    for item in total_pairs.get(values):
        if item[1]==_id:
            return

    total_pairs[values].append((page,_id))
            
    
def dump_database_to_structure(data, page):
    for player in data:
        add_uniq_pairs(player, page)
        add_total_pairs(player, page)


def backup_data():
    """
    Write dictionaries to text files
    """
    with open('total_pairs', 'w') as d:
        for key in sorted(total_pairs):
            d.write('{}: {}\n'.format(key, set(total_pairs[key])))

    with open('uniq_pairs', 'w') as d:
        for key in uniq_pairs:
            d.write('{}: {}\n'.format(key, uniq_pairs[key]))


@pytest.mark.server
def test_web_server(_test=True):
    if not _test:
        if os.path.isfile('twtask')==False:
            print ('Linux exe not found, triggering run_web_server()')
            run_web_server()
            return
    else:
        assert os.path.isfile('twtask')==True, 'Linux executable does not exist'
    

@pytest.mark.pymodules
def test_py_modules(_test=True):
    """
    If modules not installed in your VM
    """
    if not _test:
        try:
            import os
            import sys
            import pip
        except ImportError:
            os.system('''wget https://bootstrap.pypa.io/get-pip.py''')
            os.system('''export PATH="$PWD/.local/bin:$PATH"''')
            os.system('''python get-pip.py''')
            os.system('''sudo easy_install pip''')

        
    modules = ['re','urllib','base64', 'pytest', 'json', 'csv']
    missing = []
    for mod in modules:
        if mod not in sys.modules:
            missing.append(mod)
            if not _test:
                pip.main(['install', mod])
    

    assert not _test or len(missing) == 0, 'Missing modules: {}'.format(missing)


@pytest.mark.pyversion
def test_py_version(_test=True):
    assert not _test or float('.'.join(map(str,sys.version_info[:2]))) > 3.6, 'python version is too old: {}'.format(sys.version_info[:2])


@pytest.mark.illegal_name
def test_illegal_name(_test=True):
    """
    @param::player - name and ID
    Test will fail if at leat one name is illegal
    """
    suspect = list()
    for key in uniq_pairs:
        player = key.split('/')
        if player[0] == '' or player[0] == 'null':
            suspect.append((player[0],player[1],uniq_pairs[key] ))

    file_name='illegal_names.csv'
    save_to_csv(suspect,file_name, ('Illegal name', 'id', 'page'))
    assert not _test or len(suspect) == 0, 'Test fail! found {} illegal names, saved to: {}'.format(len(suspect),os.path.join(os.getcwd(),file_name))


@pytest.mark.illegal_id
def test_illegal_id(_test=True):
    """
    @param::player - name and ID
    """
    #uniq_pairs["test/"] = 1
    suspect=list()
    sus = list(filter(lambda x: not x.split('/')[1].isdigit(), uniq_pairs))
    if sus:
        for key in uniq_pairs:
            player = key.split('/')
            if player[0]+'/' in sus:
                suspect.append((player[0],player[1], uniq_pairs[key]))
    
    file_name='illegal_IDs.csv'  
    save_to_csv(suspect,file_name, ('name', 'illegal id', 'page'))  
    assert not _test or len(suspect) == 0, 'Test fail, found {} empty IDs, saved to: {}'.format(len(suspect),os.path.join(os.getcwd(),file_name))


@pytest.mark.one_2_one_name
def test_one_2_one_name(_test=True):
    """
    @param::player - name and ID
    Test will fail if at least 1 Name is assotiated with more that one ID 
    """
    names=list(map(lambda x: x.split('/')[0], uniq_pairs))
    names = list(filter(('').__ne__, names))
    names = list(filter(('null').__ne__, names))

    suspect=list()
    if len(names)!=len(set(names)):
        sus=set([x for x in names if names.count(x) > 1])
        if sus:
            for name in sus:
                for page, _id in total_pairs.get(name):
                    suspect.append((name, _id, page))
        
        file_name='one_2_one_names.csv'
        save_to_csv(suspect,file_name, ('name', 'illegal id', 'page')) 
        assert not _test or len(suspect) == 0, 'Test fail, found {} one_2_one_names, saved to: {}'.format(len(suspect),os.path.join(os.getcwd(),file_name))


@pytest.mark.one_2_one_id
def test_one_2_one_id(_test=True):
    """
    @param::player - name and ID
    Test will fail if at least 1 ID is assotiated with more that one name 
    """
    suspect=list()
    names=list(map(lambda x: x.split('/')[1], uniq_pairs))
    names = list(filter(('').__ne__, names))
    if len(names)!=len(set(names)):
        sus=set([x for x in names if names.count(x) > 1])
        
        if sus:
            for _id in sus:
                for key in uniq_pairs:
                    if int(_id) == int(key.split('/')[1]):
                        suspect.append((key.split('/')[0],key.split('/')[1], uniq_pairs[key]))

        file_name='one_2_one_ids.csv'
        save_to_csv(suspect,file_name, ('name', 'illegal id', 'page'))
        assert not _test or len(suspect) == 0, 'Test fail, found {} one_2_one_ids, saved to: {}'.format(len(suspect),os.path.join(os.getcwd(),file_name))
        

def pull_server_data():
    teapot_error, status, no_new_pairs, prev_uniq_len, uniq_len = 418, 200, 0, 0, -1
    Players=RestApi()
    os.mkdir(JSON_OUTPUT)
    
    while status!=teapot_error and no_new_pairs < 100:
        Players.url = Players.page
        data, status = request(Players)
        uniq_len = prev_uniq_len
        if uniq_len==prev_uniq_len: no_new_pairs+=1
        else: no_new_pairs=0&no_new_pairs
        dump_database_to_structure(data, Players.page)
        prev_uniq_len = uniq_len
        Players.page += 1


def test_db_api():
    """
    run all test scenarios if not running in mark mode
    """
    _test=False
    test_illegal_name(_test)
    test_illegal_id(_test)
    test_one_2_one_name(_test)
    test_one_2_one_id(_test)


@pytest.fixture(scope="session", autouse=True)
def main():
    copy=1
    path = os.path.join(os.getcwd(), TEST_OUTPUT)
    while os.path.isdir("%s%s" % (path,copy)): copy+=1
    path+=str(copy)
    os.mkdir(path)
    os.chdir(path)
    pull_server_data()
    test_db_api()
    backup_data()
    print ('Found {} error types, test path: {}'.format(errors, path))


if __name__ == '__main__':
    test_py_version()
    test_py_modules(False)
    test_web_server()
    main()