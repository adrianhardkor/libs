#!/usr/bin/env python3
import sys,os,json
import wcommon as wc

import concurrent.futures
import logging
import threading
import time

import requests
import concurrent.futures

import velocity
V = velocity.VELOCITY(wc.argv_dict['IP'], user=wc.argv_dict['user'], pword=wc.argv_dict['pass'])
data,report = V.RunScript(V.GetInventory(), 'TCC3/shared/stc_ports.py', parameters=[{'name':'python_parameter','value':'N12U'}])

print('\n\n\n\n')
wc.jd(json.loads(data['html_report'][-1][8:].replace('\\','')))
exit()


def compareDict(d1, d2, level='root',ignore_case=False):
    if isinstance(d1, dict) and isinstance(d2, dict):
        if d1.keys() != d2.keys():
            s1 = set(d1.keys())
            s2 = set(d2.keys())
            return('{:<20} + {} - {}'.format(level, s1-s2, s2-s1))
            common_keys = s1 & s2
        else:
            common_keys = set(d1.keys())

        for k in common_keys:
            compareDict(d1[k], d2[k], level='{}.{}'.format(level, k))

    elif isinstance(d1, list) and isinstance(d2, list):
        if len(d1) != len(d2):
            return('{:<20} len1={}; len2={}'.format(level, len(d1), len(d2)))
        common_len = min(len(d1), len(d2))

        for i in range(common_len):
            compareDict(d1[i], d2[i], level='{}[{}]'.format(level, i))

    else:
        if d1 != d2:
            return('{:<20} {} != {}'.format(level, d1, d2))
    return('')

data = compareDict({"one":1},{"ONE":1})
# if data == "{}": print(True)
print(data)
# wc.jd(data)
exit()


wc.jd(wc.IP_get('1.1.1.1/30')); exit()

settings = 'juniper_junos'
cmds = json.loads(wc.REST_GET('https://pl-acegit01.as12083.net/wopr/validateDCIM/raw/master/%s.j2' % settings))['response.body'].split('\n')
# wc.jd(cmds); exit()

IPs = {'IP':['10.88.240.23','10.88.240.32','10.88.240.47', '10.88.232.12','10.88.240.20', '10.88.240.26','10.88.240.29','10.88.240.41', '10.88.240.44','10.88.240.65']}
IPs = {'IP': ['10.88.240.47', '10.88.240.44']}

#juniper_junos:
#  username: "ADMIN"
#  private_key_file: "/opt/paramiko-test-key"
#  ansible_ssh_common_args: '-okexalgorithms=+diffie-hellman-group1-sha1 '
#  vendor: 'juniper_junos'
#  prompt: "([@]+[a-zA-Z0-9\.\-\_]+[>#%]+[ ])"
#  buffering: 'set cli screen-length 0'
#  exit: "exit"
#def PARA_CMD_LIST(commands=[], ip='', driver='', username='', password='', become='', key_fname='', quiet=False,ping=True,windowing=True, settings_prompt='', buffering='', exit=[])

def AIEmulti(ip, settings, cmds):
	wc.jd({'cmd':cmds})
	attempt = json.loads(wc.REST_PUT('http://10.88.48.21:%s/aie?settings=%s&hostname=%s' % (str(wc.argv_dict['port']), settings, ip), verify=False, convert_args=True, args={'cmd':cmds}))
	return(attempt)

wc.jd(wc.MULTIPROCESS(AIEmulti, IPs['IP'], {'settings':'juniper_junos', 'cmds':cmds})); exit()

# REST_PUT(url, headers={"Content-Type": "application/json", "Accept": "application/json"}, user='', pword='', args={},verify=False,convert_args=False)

wc.jd(wc.MULTIPROCESS(wc.PARA_CMD_LIST, IPs['IP'], {'commands':['show 1'], 'driver':'', 'username':'ADMIN', 'become':True, 'key_fname':'/opt/paramiko-test-key', 'ping':True, 'settings_prompt':"([@]+[a-zA-Z0-9\.\-\_]+[>#%]+[ ])", 'exit':['exit']}, processes=6)); exit()


print(wc.PARA_CMD_LIST(commands=['show 1'], ip='10.88.240.32', driver='juniper_junos', username='ADMIN', become=True, key_fname='/opt/paramiko-test-key', ping=False, settings_prompt="([@]+[a-zA-Z0-9\.\-\_]+[>#%]+[ ])", exit=['exit'] )); exit()












def get_wiki_page_existence(wiki_page_url, timeout=10):
    response = requests.get(url=wiki_page_url, timeout=timeout)

    page_status = "unknown"
    if response.status_code == 200:
        page_status = "exists"
    elif response.status_code == 404:
        page_status = "does not exist"

    return wiki_page_url + " - " + page_status

wiki_page_urls = [
    "https://en.wikipedia.org/wiki/Ocean",
    "https://en.wikipedia.org/wiki/Island",
    "https://en.wikipedia.org/wiki/this_page_does_not_exist",
    "https://en.wikipedia.org/wiki/Shark",
]

def THREADER(fn, mylist, attr, max_workers=3):
    timer = wc.timer_index_start()
    result = {'Results':{}}
    mylistKEY = list(mylist.keys())[0]; # only 1 supported
    _FN = attr
    _FN['fn'] = fn
#    for l in mylist.keys():
#        _FN[l] = mylist[l]
    # ThreadPoolExecutor for I/O processing
    # ProcessPoolExecutor for CPU processing 

def worker(IP):
    print('Starting ' + str(threading.currentThread().getName()))
    print(wc.is_pingable(IP))

# CLASS THAT NEEDS ITS OWN HANDLER THREADER.IS_PINGABLE AND VALIDATE
def THREADER2(fn, mylist, attr):
	threadArgs = {'target': fn}
	results = {}
	mylistKEY = list(mylist.keys())[0]; # only 1 supported
	timer = wc.timer_index_start()
	threads = {}
	for looper in mylist[mylistKEY]:
		threadArgs['args'] = [looper]
		thread = threading.Thread(**threadArgs)
		thread.start()
		# threads[looper] = {'thread': thread}
		results[looper] = thread.join()
	results['timer'] = wc.timer_index_since(timer)
	return(results)

	print('took ' + str(wc.timer_index_since(timer)))
	is_alive = True
	wc.jd(dict(vars(thread))); exit()
	wc.pairprint(i, twrv.join())
	results[i] = thread.join()

	while is_alive:
		is_alive = False 
		for l in list(threads.keys()):
			t = threads[l]['thread']
			if t.is_alive:
				is_alive = True
				threads[l]['is_alive'] = t.is_alive
			else: threads.pop(l)
		print(list(threads.keys()))
	wc.pairprint('THREADER2', wc.timer_index_since(timer))

# wc.jd(THREADER(get_wiki_page_existence, {'wiki_page_url':wiki_page_urls}, {'timeout':10}))

IPs = {'IP':['10.88.240.23','10.88.240.32','10.88.240.47', '10.88.240.53','10.88.240.54','10.88.240.20', '10.88.240.26','10.88.240.29','10.88.240.41', '10.88.240.44','10.88.240.50','10.88.240.65']}
# wc.jd(THREADER(wc.is_pingable, IPs, {}, max_workers=5))

# vars(class)
 


serial = {}
timer = wc.timer_index_start()
# for i in IPs['IP']: serial[i] = wc.is_pingable(i)
serial['runtime'] = wc.timer_index_since(timer)
wc.jd(serial)



# wc.jd(THREADER2(wc.is_pingable, IPs, {}))
print("NEXT")



#from threading import Thread
#class ThreadWithReturnValue(Thread):
#    def __init__(self, group=None, target=None, name=None,
#                 args=(), kwargs={}, Verbose=None):
#        Thread.__init__(self, group, target, name, args, kwargs)
#        self._return = None
#    def run(self):
#        # print(type(self._target))
#        if self._target is not None:
#            self._return = self._target(*self._args, **self._kwargs)
#    def join(self, *args):
#        Thread.join(self, *args)
#        return self._return
#
#timer = wc.timer_index_start()
#for i in IPs['IP']:
#    twrv = ThreadWithReturnValue(target=wc.is_pingable, args=(i,))
#    twrv.start()
#    wc.pairprint(i, twrv.join())
#wc.pairprint('Thread3', wc.timer_index_since(timer))

def is_pingable(IP, adrian):
	return({'adrian':adrian,'pingable':wc.is_pingable(IP)})






def two2one(foo, bar):
    # one = [i1 i2 i3]
    # two = [v1 v2 v4]
    # result = {i1:v1, i2:v2, i3:v3}
    results = {}
    for f, b in zip(foo, bar):
        results[f] = b
    return(results)

import inspect
import multiprocessing
from functools import partial

def MULTIPROCESS(funct, mylist, non_rotating_args, processes=5):
    # args must match funct-args
    results = {}
    t = wc.timer_index_start()
    pool = multiprocessing.Pool()
    pool = multiprocessing.Pool(processes=processes)
    outputs = pool.map(partial(funct, **non_rotating_args), mylist)
    results = two2one(mylist,outputs)
    results['timer'] = wc.timer_index_since(t)
    return(results)

IIPs = {'IP':[], 'adrian':[]}
for i in IPs['IP']: IIPs['IP'].append(i); IIPs['adrian'].append(1)
wc.jd(MULTIPROCESS(wc.is_pingable, IPs['IP'], {'adrian':'non-rotating-args'}))
 
