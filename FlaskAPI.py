#!/usr/bin/env python3
import os
import sys
import wcommon as wc
if 'port' not in wc.argv_dict.keys(): wc.argv_dict['port'] = '5000'
from werkzeug.utils import secure_filename
import json
import re
import skinny
# import cablemedic
import velocity
import flask
import Mongo; # shared_libs
import time
import paramiko
import qrcode
import base64
from io import BytesIO
import lepton
import gitlabAuto
try:
	from qrcode.image.pure import PymagingImage
except Exception:
	pass

flaskIP = wc.cleanLine(wc.grep('10.88', wc.exec2('ifconfig')))[1]
# wc.jd(wc.wcheader)
# Mongo.TryDeleteDocuments(Mongo.runner)

def flaskArgsPayload():
	try:
		args = {k: v for k, v in flask.request.args.items()}
	except Exception:
		args = {}
	try:
		payload = {k: v for k, v in flask.request.get_json().items()}
	except Exception:
		payload = {}
	return(args,payload)

def vagent_getter():
	response = {}
	args,payload = flaskArgsPayload()
	if args == {}: objects = Mongo.MONGO._GETJSON(Mongo.runner)
	else: objects = Mongo.MONGO._GETJSON(Mongo.runner, criteria=args)
	fake = 1
	for deviceObj in objects:
		if 'runId' not in deviceObj.keys():
			deviceObj['runId'] = str(fake)
			fake = fake + 1
		response[deviceObj['runId']] = deviceObj
	return(response)

def flask_RDU():
	@Mongo.MONGO.app.route('/rdu', methods=['GET'])
	def rdu():
		# return(flask.jsonify(Mongo.rduModem.objects()))
		return(flask.jsonify(Mongo.MONGO._GETJSON(Mongo.rduModem)))

def flask_downloader():
	@Mongo.MONGO.app.route('/download', methods=['GET'])
	def downloadFile():
		#For windows you need to use drive name [ex: F:/Example.pdf]
		# /download?fname=adrian_test.csv
		fname = flask.request.args['fname']
		return(flask.send_file('./' + fname, as_attachment=True))


def flask_uploader():
	@Mongo.MONGO.app.route('/upload', methods = ['POST'])
	def upload_file():
		args,payload = flaskArgsPayload()
		Mongo.MONGO.app.config['UPLOAD_FOLDER'] = './'
		_FNAME = str(flask.request.files['file']).split("'")[1]
		wc.pairprint(_FNAME, os.path.exists('./' + _FNAME)) 
		if os.path.exists('./' + str(flask.request.files['file'])) is False:
			wc.exec2('/usr/bin/touch ./' + _FNAME)
		f = flask.request.files['file']
		secure_f = secure_filename(f.filename)
		f.save(secure_f)
		print('\n\n\n')
		wc.pairprint(f.filename, secure_f)
		print('\n\n\n')
		return('file uploaded successfully')
  

def flask_AIS():
	@Mongo.MONGO.app.route('/ais', methods=['GET'])
	def ais():
		AIS = {}
		if flask.request.args == {}:
			routers = Mongo.MONGO._GETJSON(Mongo.Router)
			servers = Mongo.MONGO._GETJSON(Mongo.Server)
			CMTSs = Mongo.MONGO._GETJSON(Mongo.CMTS)
			modems = Mongo.MONGO._GETJSON(Mongo.Modem)
			SGs = Mongo.MONGO._GETJSON(Mongo.SG)
			Firewalls = Mongo.MONGO._GETJSON(Mongo.Firewall)
		else:
			routers = Mongo.MONGO._GETJSON(Mongo.Router, criteria=flask.request.args)
			servers = Mongo.MONGO._GETJSON(Mongo.Server, criteria=flask.request.args)
			CMTSs = Mongo.MONGO._GETJSON(Mongo.CMTS, criteria=flask.request.args)
			modems = Mongo.MONGO._GETJSON(Mongo.Modem, criteria=flask.request.args)
			SGs = Mongo.MONGO._GETJSON(Mongo.SG, criteria=flask.request.args)
			Firewalls = Mongo.MONGO._GETJSON(Mongo.Firewall, criteria=flask.request.args)
			wc.jd(flask.request.args)
		for deviceTypeObj in [routers, servers, CMTSs, modems, SGs]:
			for deviceObject in deviceTypeObj:
				if 'name' not in deviceObject.keys(): return(flask.jsonify(deviceObject))
				AIS[deviceObject['name']] = deviceObject
		return(flask.jsonify(AIS))

def flask_NewCall():
	@Mongo.MONGO.app.route('/new_call', methods=['GET'])
	def new():
		return(flask.jsonify({'got':'logs?'}))

def flask_RunJenkinsPipeline():
	@Mongo.MONGO.app.route('/jenkins/runPipe', methods=['POST'])
	def pipeline():
		args,body = flaskArgsPayload()
		import jenkins
		J = jenkins.JENKINS(body.pop('JEN_IP'), body.pop('username'), body.pop('token'))
		monitor = J.RunPipeline(body['Pipe'], body)
		wc.pairprint('monitor', monitor)
		return(flask.jsonify({'monitor':'http://10.88.48.21:' + str(wc.argv_dict['port']) + '/runner?runId=' + str(monitor)}))

def flask_validated():
	@Mongo.MONGO.app.route('/validated', methods = ['GET'])
	def validated():
		headers = {'PRIVATE-TOKEN': 'hWfVZcD71VgDMcpzZhK7'}
		timer = wc.timer_index_start()
		args,payload = flaskArgsPayload()
		branch = args['branch']
		if branch.lower() not in ['main', 'master']:
			return(flask.jsonify(Mongo.MONGO._GETJSON(Mongo.validationDevice, criteria={'branch':branch})))
		else:
			# main/master = INVENTORY PAGE DASHBOARD
			G = gitlabAuto.GITLAB('https://pl-acegit01.as12083.net/', headers['PRIVATE-TOKEN'], 300)
			results = G.GetFiles('asset-data/')
			for disregard in ['.gitlab-ci.yml', 'online', 'template.dcim.yml']:
				if disregard in results.keys(): del results[disregard]
			result = []
			headers = []
			for k3 in list(results.keys()):
				if results[k3] == None: continue
				for h in results[k3].keys():
					headers.append(h)
			headers = wc.lunique(headers)
			for kk in list(results.keys()):
				if results[kk] == None: continue
				for hh in headers:
					if hh not in results[kk].keys(): results[kk][hh] = ''
				try:
					results[kk]['uuid'] = str(kk).split('.')[0]
					results[kk]['GetInterfaceURL'] = 'http://10.88.48.21:5000/show_interfacesAIE?uuid=' + str(kk).split('.')[0]
				except Exception:
					pass
				result.append(results[kk])
			# results['_'] = wc.timer_index_since(timer)
			result = json.loads(json.dumps(result, sort_keys=True))
			return(flask.jsonify(result))

			results = []
			devices = json.loads(wc.REST_GET('https://pl-acegit01.as12083.net/api/v4/projects/300/repository/tree?ref=master', headers=headers))
			for d in devices:
				# https://pl-acegit01.as12083.net/arc-lab/asset-data/raw/master/23dbc8f8-c4e0-4c21-8be5-0335e43ad344.dcim.yml
				if d['path'].endswith('.dcim.yml') is False: continue
				blob_id = json.loads(wc.REST_GET('https://pl-acegit01.as12083.net/api/v4/projects/300/repository/files/' + d['path'] + '?ref=master', headers=headers))['blob_id']
				wc.log_fname(json.loads(wc.REST_GET('https://pl-acegit01.as12083.net/api/v4/projects/300/repository/blobs/' + blob_id + '/raw', headers=headers))['response.body'], './data.yml')
				data = wc.read_yaml('./data.yml')
				results.append({d['path']: data})
			results.append({'_timer': str(wc.timer_index_since(timer))})
			return(flask.jsonify(results))

def flask_validate():
	@Mongo.MONGO.app.route('/validate', methods = ['GET'])
	def validate():
		validate = wc.timer_index_start()
		args,payload = flaskArgsPayload()
		branch = args['branch']
		if branch in ['master', 'main']: return(flask.jsonify({'DO NOT RUN ON': branch}))
		uuid = ''
		if 'uuid' in args.keys():  uuid = args['uuid']
		# master = wc.exec2('export GIT_SSH_COMMAND="ssh -i /opt/gitlab_root"; cd ../asset-data/; rm *.yml; git checkout master; git branch --set-upstream-to=origin/master master; git stash; git pull; ls;').split('\n')
		G = gitlabAuto.GITLAB('https://pl-acegit01.as12083.net/', 'hWfVZcD71VgDMcpzZhK7', 300)
		wc.LoadMasterDevices4Duplicates('master', G); # /asset-data/
		# repos = wc.exec2('export GIT_SSH_COMMAND="ssh -i /opt/gitlab_root"; cd ../asset-data/; rm *.yml; git checkout %s; git branch --set-upstream-to=origin/%s %s; git stash; git pull; ls;' % (branch,branch,branch)).split('\n')
		# out = wc.lsearchAllInline('branch is', repos)
		# if out == []: return(flask.jsonify({'err':repos}))
		# repos = wc.exec2('cd ../asset-data/; ls -1;').split('\n')
		# return(flask.jsonify({'master':master,'repos':repos,'Duplicates':wc.Duplicates, 'UUIDS': wc.UUIDS, 'cllis':wc.cllis}))
		# out.append(repos)

		
		VALIDATION = wc.validateITSM([], uuid, G, branch, CIDR='10.88.0.0/16')
		Mongo.MONGO._DELETE(Mongo.validationDevice, criteria={'branch':branch}, force=True)
		for uu in VALIDATION.keys():
			if uu == 'runtime' or VALIDATION[uu] == 'runtime': continue
			DEVICE = {'uuid':uu,'branch':branch,'valid':VALIDATION[uu]['valid']}
			for blah in ['itsm','dcim','cable']:
				try:
					DEVICE[blah] = VALIDATION[uu]['data'][blah]
				except Exception:
					pass
			for blah2 in ['timer','interfaces_to_cable']:
				if blah2 in VALIDATION[uu].keys(): DEVICE[blah2] = str(VALIDATION[uu][blah2])
			try:
				Mongo.MONGO._UPDATE(Mongo.validationDevice, {'uuid':uu}, DEVICE)
			except Exception as err:
				DEVICE['_err'] = str(err)
				return(flask.jsonify(DEVICE))
		# out.append(wc.validateITSM(repos, uuid, directory='../asset-data/', CIDR='10.88.0.0/16'))
		return(flask.jsonify({'runtime': str(wc.timer_index_since(validate)) + ' ms'}))

def flask_runtimelogger():
	@Mongo.MONGO.app.route('/runner', methods = ['POST', 'GET', 'PUT'])
	def run():
		wc.pairprint('runner:   method', flask.request.method)
		if str(flask.request.method) != 'GET':
			args,payload = flaskArgsPayload()
			try:
				Mongo.MONGO._UPDATE(Mongo.runner, args, payload)
				return(flask.jsonify(vagent_getter()))
			except Exception as err:
				return(json.dumps({'err':str(err)}))
		else:
			# wc.jd(vagent_getter())
			return(flask.jsonify(vagent_getter())); # [GET]

def GenQR_PNG(url):
	img = qrcode.make(url, image_factory=PymagingImage)
	buffered = BytesIO()
	img.save(buffered)
	return(base64.b64encode(buffered.getvalue()).decode())

def flask_qr():
	@Mongo.MONGO.app.route('/qrservice', methods = ['GET'])
	def qr():
		args,payload = flaskArgsPayload()
		if 'instructions' in args.keys():
			return(flask.render_template(args['instructions'] + '.html'))
		qr_fname = 'qr.png'
		# wc.rmf('templates/' + qr_fname)
		if 'uuid' in args.keys(): myUUID = args['uuid']
		else: myUUID = wc.genUUID()
		link = 'http://10.88.48.21:5000/ais?uuid=' + myUUID
		img_str = GenQR_PNG(link)
		result = flask.render_template('qr_page.html', adrian_test=str(args), img_str=img_str, link=link, myUUID=myUUID, dcim=wc.read_file('templates/dcim.yml').split("\n"), itsm=wc.read_file('templates/itsm.yml').split("\n"), cable=wc.read_file('templates/cable.yml').split("\n"))
		return(result)

def ParseSettingsYML(url):
	settings = json.loads(wc.REST_GET(url))['response.body']
	s = {}
	for line in settings.split('\n'):
		if line.startswith('  '):
			sline = line.split(':')
			index = sline.pop(0).strip()
			value = ':'.join(sline).strip()
			value = wc.mcsplit(value, ['"',"'"])
			try:
				value.pop(-1)
				value.pop(0)
			except Exception:
				pass
			value = ','.join(value)
			# if len(value) == 1: value = value[0]
			# else: value = value[1]
			s[path][index] = value
		else:
			path = line.strip(':')
			s[path] = {}
	return(s)

def PullCmds(args,payload):
	result = []
	commands = sorted(wc.lsearchAllInline('cmd', list(args.keys())))
	if payload != {}:
		for a in payload['cmd']:
			result.append(a.strip())
	else: 
		for a in commands:
			# &cmd1=blah&cmd2=blah
			result.append(args[a].replace('_',' '))
	return(result)

def flask_AIEngine():
	@Mongo.MONGO.app.route('/aie', methods = ['GET', 'PUT'])
	def engine():
		timer = int(time.time())
		paramiko_args = {}
		result = {}
		args,payload = flaskArgsPayload()
		# INVENTORY = RAW.INVENTORY.YML?
		settings = ParseSettingsYML('https://raw.githubusercontent.com/adrianhardkor/shared_libs/main/settings.yml')
		settings_name = args['settings']
		settings = settings[settings_name]
		# print(settings)
		# return(flask.jsonify(settings))
		CMDS = PullCmds(args,payload)
		if settings['private_key_file'].endswith('.txt'):
			# first line
			# u/p/p
			upp = wc.read_file(settings['private_key_file']).split('\n')
			paramiko_args['password'] = upp[0]
			if len(upp) > 1: paramiko_args['become'] = upp[1]
		else: paramiko_args['key_fname'] = settings['private_key_file']
		if settings['vendor'] == 'gainspeed':
			blind = {'commands':['show config | match prompt'],'ip':args['hostname'],'username':settings['username'],'password':wc.read_file(settings['private_key_file']),'windowing':False,'ping':False,'quiet':False}
			prompt = wc.cleanLine(wc.PARA_CMD_LIST(**blind)[0])
			settings['prompt'] = '|'.join([ prompt[1].split(';')[0],  prompt[3].split(';')[0] ])
		paramiko_args['commands'] = CMDS
		paramiko_args['ip'] = args['hostname']
		paramiko_args['driver'] = settings['vendor']
		paramiko_args['username'] = settings['username']
		paramiko_args['ping'] = False
		paramiko_args['quiet'] = True
		if 'buffering' in settings.keys(): paramiko_args['buffering'] = settings['buffering'].split(',')
		if 'exit' in settings.keys():
			for e in settings['exit'].split(','):
				paramiko_args['commands'].append(e)
			paramiko_args['exit'] = settings['exit'].split(',')
		paramiko_args['settings_prompt'] = settings['prompt']
		try:
			raw = wc.PARA_CMD_LIST(**paramiko_args)
		except Exception as err:
			return(flask.jsonify({'errFlask': str(err)}))
		for cmd in raw.keys():
			if cmd == "_": pass
			elif 'json' in wc.cleanLine(cmd): 
				# JUNIPER
				# wc.jd(raw[cmd].split('\r\n')[0:-2])
				raw[cmd] = '\n'.join(raw[cmd].split('\r\n')[1:-2])
				try:
					raw[cmd] = json.loads(raw[cmd])
				except Exception as err:
					print(raw[cmd])
					raw[cmd] = raw[cmd].split('\n')
					raw['_'] = str(err)
			elif 'xml' in wc.cleanLine(cmd):
				raw[cmd] = '\n'.join(raw[cmd].split('\r\n')[1:-2])
				try:
					raw[cmd] = wc.xml_loads2(raw[cmd])
				except Exception as err2:
					raw[cmd] = raw[cmd].split('\n')
					raw['_'] = str(err2)
			elif type(raw[cmd]) == dict: pass
			else: raw[cmd] = raw[cmd].split('\r\n')
		return(flask.jsonify(raw)); # {'command': 'output'}

def flask_leptonDash():
	@Mongo.MONGO.app.route('/woDash', methods = ['GET'])
	def leptonInner():
		credsL = wc.cleanLine(wc.read_file('/opt/lepton')); # printenv not working?
		credsV = wc.cleanLine(wc.read_file('/opt/velocity'))
		args,payload = flaskArgsPayload()
		L = lepton.LEPTON(credsL[0], credsL[1], credsL[2])
		L.INV = L.GetStatus()
		V = velocity.VELOCITY(credsV[0], credsV[1], credsV[2])
		V.CONNECTIONS = V.GetConnections({'Connections':'Only'})
		# return(flask.jsonify(V.CONNECTIONS))
		data = lepton.FormatLeptonDashboard(L.INV)
		for p in data.keys():
			wc.pairprint(p, wc.lsearchAllInline2('lepton01_*', list(V.CONNECTIONS.keys())))
			if 'lepton01_' + str(p) in V.CONNECTIONS.keys():  data[p]['Velocity'] = V.CONNECTIONS['lepton01_' + p]
		return(flask.jsonify(data))
		# return(flask.jsonify(L.INV['ports']))

def flask_stcDash():
	@Mongo.MONGO.app.route('/stcDash', methods = ['GET'])
	def stcInner():
		credsV = wc.cleanLine(wc.read_file('/opt/velocity'))
		args,payload = flaskArgsPayload()
		V = velocity.VELOCITY(credsV[0], credsV[1], credsV[2])
		ResourceTopologies = V.GetTopologiesByResource()
		# return(flask.jsonify(ResourceTopologies))
#		for N12U in list(ResourceTopologies.keys()):
#			if N12U.startswith(args['chassis'] + '||') is False: ResourceTopologies.pop(N12U)
#			else: ResourceTopologies[N12U.split('|')[-1]] = ResourceTopologies.pop(N12U)
		data,report = V.RunScript({}, 'TCC3/shared/stc_ports2.py', parameters=[{'name':'python_parameter','value':args['chassis']}])
		raw = json.loads(data['html_report'][-1][8:].replace('\\',''))['//' + args['chassis']]
		STC = raw['PartNum'].split('-')[-1]

		result = []
		for slot in raw['slots'].keys():
			s = raw['slots'][slot]
			slotType = s['PartNum']
			firmware = s['FirmwareVersion']
			slotStatus = s['Status']
			for port in s['ports'].keys():
				p = s['ports'][port]
				splitP = port.split('/')
				pDATA = {'PortName':p['Location'], 'slotType': slotType, 'firmware':firmware, 'ownershipState': p['OwnershipState'], 'ownerUser':p['OwnerUser'], 'slotStatus':slotStatus,'top_inactive':[],'top_reserved':[]}
				if STC + '||S' + splitP[3] + 'P' + splitP[4] in ResourceTopologies.keys():
					for top in ResourceTopologies[STC + '||S' + splitP[3] + 'P' + splitP[4]].keys():
						if ResourceTopologies[STC + '||S' + splitP[3] + 'P' + splitP[4]][top]['activeRes'] == {}:
							pDATA['top_inactive'].append(top)
						else: pDATA['top_reserved'].append(ResourceTopologies[STC + '||S' + splitP[3] + 'P' + splitP[4]][top])
				result.append(pDATA)
				
		# result.append(list(ResourceTopologies.keys()))
		return(flask.jsonify(result))


# FLASK WEB-API
def flask_default():
	@Mongo.MONGO.app.route('/', methods=['GET'])
	def home():
		return "<h1>DFEAULT</h1><p>Got default, but is working</p>"

if  __name__ == "__main__":
	# Executables
	flask_default()
	flask_RDU(); # /rdu
	flask_uploader()
	flask_AIEngine(); # /aie?hostname=10.88.240.26
	flask_downloader()
	flask_validate(); # /validate
	flask_validated(); # /validated - get validate results
	flask_AIS(); # /ais
	flask_NewCall(); # /new_call
	flask_leptonDash(); # /woDash
	flask_stcDash(); # stcDash
	flask_RunJenkinsPipeline()
	flask_qr(); # / qr
	flask_runtimelogger(); # /runner
	if 'port' in wc.argv_dict.keys():
		Mongo.MONGO.app.run(debug=True, host=flaskIP, port=int(wc.argv_dict['port']))
	else: Mongo.MONGO.app.run(debug=True, host=flaskIP)

