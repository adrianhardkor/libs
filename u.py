#!/usr/bin/env python3
import sys,os,json,re
import wcommon as wc

import concurrent.futures
import logging
import threading
import time

import requests
import concurrent.futures
import yaml
import paramiko

def NON_WINDOWING_PARAMIKO(ip, username, key_fname, commands):
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    if key_fname != '':
        k = paramiko.RSAKey.from_private_key_file(key_fname)
        c.connect( hostname = ip, username = username, pkey = k )
    else:
        c.connect( hostname=ip, username=username, password=password)
    o = []
    for command in commands:
        stdin , stdout, stderr = c.exec_command(command)
        o.append(bytes_str(stdout.read()))
    c.close()
    return(o)


def mgmt_login(ip, username, password, become, key_fname, ping):
	timer = wc.timer_index_start()
	attempts = 1
	connected = ''
	errs = []
	if ping:
		ping_result = wc.is_pingable(ip)
		if not quiet: print(ping_result)
		if ping_result == False: login_err = 'ping:' + str(ping_result); return(-1,{'login_err':login_err},timer)
	connect_settings = {'hostname':ip, 'port':'22', 'username':str(username), 'look_for_keys':False, 'allow_agent':False, 'banner_timeout':600, 'timeout':10}
	if key_fname != '': connect_settings['pkey'] = paramiko.RSAKey.from_private_key_file(key_fname)
	else: connect_settings['password'] = password
	while attempts <= 2:
		remote_conn = paramiko.SSHClient()
		remote_conn.load_system_host_keys()
		remote_conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		try:
			connected = remote_conn.connect(**connect_settings)
			if not quiet: wc.pairprint('connected:  ' + str(wc.lunique(errs)), ip)
			break;
		except Exception as err:
			attempts += 1
			errs.append(str(err))
	if connected == '':
		# did not made connection
		return(-1,{'login_errs': errs},timer)
	else:
		# connected
		HANDLE = remote_conn.invoke_shell()
		init = HANDLE.recv(65535)
		return(HANDLE,{'_': {'mgmt_login': wc.timer_index_since(timer)}},timer)


def AllCommands(buffering,commands,exit):
	result = []
	for cmds in [buffering, commands,exit]:
		for a in cmds:
			result.append(a)
	return(result)
	

def wait(remote_conn, prompt_status, quiet, command, regexPrompt, passwordPrompt, closedPrompt, become):
	output = ''
	time.sleep(.5)
	while remote_conn.recv_ready() is False and remote_conn.exit_status_ready() is False:
		time.sleep(0.1)
	if not quiet: wc.pairprint('Ready/Sending', command)
	while prompt_status == None:
		buff = ''
		while remote_conn.recv_ready():
			buff += wc.bytes_str(remote_conn.recv(4096))
		output += buff
		time.sleep(0.1)
		if regexPrompt.search(output) != None:
			prompt_status = True
			break
		elif passwordPrompt.search(output) != None:
			prompt_status = True
			remote_conn.send(become + '\n')
			output += wait(remote_conn, None, quiet, command, regexPrompt, passwordPrompt, closedPrompt, become)
			break
		elif closedPrompt.search(output) != None:
			prompt_status = True
			break

def run_commands(remote_conn, buffering, commands, ip, quiet, become, exit, settings_prompt, result):
	timer = wc.timer_index_start()
	regexPrompt = re.compile('.*%s$' % settings_prompt)
	closedPrompt = re.compile('.* closed.$')
	passwordPrompt = re.compile('assword{:|: |}')
	commandIndex = 1
	for command in list(AllCommands(buffering, commands, exit)):
		output = ''
		prompt_status = None; # PROMPT per command
		cmdTime = wc.timer_index_start()
		if command in buffering: commandIndex = 0
		index = str(commandIndex) + command
		result[index] = []
		# last thing was recv
		remote_conn.send(command + '\n')
		output = ''
		time.sleep(.5)
		if remote_conn.exit_status_ready() == True:
			time.sleep(1.5)
			# print('\n\n\n' + 'CLOSED\n\n')
			result[str(commandIndex) + command].append(wc.bytes_str(remote_conn.recv(65535)))
			remote_conn.close()
			return(result)
		while remote_conn.recv_ready() is False and remote_conn.exit_status_ready() is False:
			time.sleep(0.1)
		# wc.pairprint(ip + ' Ready/Sending', command)
		while prompt_status == None:
			buff = ''
			while remote_conn.recv_ready():
				buff += wc.bytes_str(remote_conn.recv(4096))
			output += buff
			time.sleep(0.1)
			if regexPrompt.search(output) != None:
				prompt_status = True
				break
#			elif closedPrompt.search(output) != None:
#				wc.pairprint(closedPrompt.search(output), remote_conn.exit_status_ready())
#				prompt_status = True
#				break
			elif passwordPrompt.search(output) != None:
				prompt_status = True
				remote_conn.send(become + '\n')
				# output += wait(remote_conn, None, quiet, command, regexPrompt, passwordPrompt, closedPrompt, become)
				break
		result[index].append(output)
		result['_'][index] = wc.timer_index_since(cmdTime)
		commandIndex += 1
		if quiet: wc.pairprint(ip + ' Ready/Sending', command + '    ' + str(wc.timer_index_since(cmdTime)))
		else: print(output)
	return(result)


def PARA_CMD_LIST(ip='', commands=[], username='', password='', become='', key_fname='', quiet=False, ping=True, windowing=True, settings_prompt='', buffering=[], exit=[], driver=''):
    if windowing == False: return(NON_WINDOWING_PARAMIKO(ip, username, key_fname, commands))
    remote_conn, result,mgmt_timer = mgmt_login(ip, username, password, become, key_fname, ping)
    if remote_conn == -1: return(result['_'])
    if quiet: wc.pairprint(ip, result)
    result = run_commands(remote_conn, buffering, commands, ip, quiet, become, exit, settings_prompt, result)
    result['_']['ALL'] = wc.timer_index_since(mgmt_timer)
    # if quiet: result['_']['ip'] = ip; wc.jd(result['_'])
    return(result)

data = PARA_CMD_LIST(ip='10.88.241.7', commands=['show interface all status', 'show port async all status'], username='arcadmin', password='arcaccess', become='arcenable', quiet=True,ping=False,windowing=True, settings_prompt="([a-zA-Z0-9\-\_]+[\:]+[0-9\ ]+[>])", buffering=['no pause', 'enable'], exit=['exit', 'exit', 'exit', 'exit'])
wc.jd(data)
print('\n\n')

data = PARA_CMD_LIST(ip='10.88.240.23', commands=['show configuration | display set'], username='ADMIN', password='ArcLabAdmin', become='arcenable', quiet=True,ping=False,windowing=True, settings_prompt="([@]+[a-zA-Z0-9\.\-\_]+[>#%]+[ ])", buffering=['set cli screen-length 0'], exit=['exit'])

# http://10.88.48.21:5001/aie?settings=a10t&hostname=10.88.240.77&cmd=show_ip_int

wc.jd(data)

exit()

