#!/usr/bin/env python3
import os
import sys
import wcommon as wc
import json
import requests
# wc.jenkins_header(); # load inputs from Jenkinsfile
# wc.jd(wc.wcheader)
_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJVc2VyIjoibGVwdG9uIiwia2V5IjozLCJleHAiOjE2MTI5OTE2NzF9.j2kF-mJJecSBfPQyfyYQ5YpFs09_sSL0DhJCrbghJL4'
url = 'https://storage.googleapis.com/lepton-docs/ColdFusion1-Api-REST.html'

class LEPTON():
	def __init__(self, IP, user, pword):
		self.user = user
		self.pword = pword
		self.IP = 'https://' + IP + ':8443'; # http
		self.__name__ = 'AWX'
	def REST_POST(self, url, args={}, headers={'Content-Type': 'application/json', 'Authorization': 'Basic bGVwdG9uOmxlcHRvbg=='}, verify=False):
		return(json.loads(wc.REST_POST(self.IP + url, user=self.user, pword=self.pword, verify=False, args=args, headers=headers, convert_args=True)))
	def REST_GET(self, url):
		return(json.loads(wc.REST_GET(self.IP + url, user=self.user, pword=self.pword,verify=False)))
	def MapPorts(self, endpoint, A, B):
		out = self.REST_POST('/chassis/do/' + endpoint, args={'Direction':'TwoWay', 'Pairs':[{'A':A,'B':B}]})
		if (endpoint == 'unmap' and out['response.status_code'] == '204') or out["Response"] ==  "<Response [204]>":
			out = {'response.body': {'Success': '%s %s:  Response 204' % (A,B)}}
		elif 'response.body' in out.keys():
			# wc.jd(out)
			if str(out['response.body']).strip() != '': out['response.body'] = json.loads(out['response.body'])
		return(out)
	def GetStatus(self):
		_DO_SHOW_FLOW_PORTS = []
		version = LEPTON.REST_GET(self, '/system/do/version')
		out = {'chassis': LEPTON.REST_POST(self, '/chassis/do/show-cards')}
		data = LEPTON.REST_GET(self, '/chassis')
		out['chassis']['Serial'] = data['Serial']
		out['chassis']['Model'] = data['Model']
		for v in version.keys():
			out['chassis'][v] = version[v]
		SLOTID = 0
		out['ports'] = {}
		for l in data['Linecards']:
			if type(l) is not dict:
				SLOTID += 1
				continue; # null for slot missing
			l = LEPTON.REST_GET(self, str(l['Url']))
			linecard = {'Model': l['Model'], 'Name': l['Name']}
			# linecard['Description'] = l['Description']
			for Port in l['Ports']:
				url = '/chassis/linecards/%s/ports/%s' % (SLOTID, Port['Url'].split('/')[-1])
				PortProp = LEPTON.REST_GET(self, url)
				if len(str(PortProp['Id'])) == 1:
					_PORT = '.'.join([str(PortProp['Slot']),'0' + str(PortProp['Id'])])
				else:
					_PORT = '.'.join([str(PortProp['Slot']),str(PortProp['Id'])])
				_DO_SHOW_FLOW_PORTS.append(_PORT)
				out['ports'][_PORT] = {'url': url, 'linecard': linecard}
				for pp in PortProp.keys():
					if type(PortProp[pp]) == list:
						out['ports'][_PORT][pp] = PortProp[pp]
					elif type(PortProp[pp]) == dict:
						out['ports'][_PORT][pp] = {}
						for ppp in PortProp[pp].keys():
#							if type(PortProp[pp][ppp]) == list:
#								out['ports'][_PORT][pp][ppp] = str(PortProp[pp][ppp])
#							else:
#								# wc.pairprint(str(pp) + '\t' + str(ppp),PortProp[pp][ppp])
							out['ports'][_PORT][pp][ppp] = PortProp[pp][ppp]
					else:
						out['ports'][_PORT][pp] = PortProp[pp]
			SLOTID += 1
		# /do/show-flow
		for _P in LEPTON.REST_POST(self, '/chassis/do/show-flow', args={"Ports": _DO_SHOW_FLOW_PORTS})['Ports']:
			__Port = _P['Port']
			if 'Mode' not in out['ports'][__Port].keys():
				out['ports'][__Port]['Mode'] = _P['Mode']
			for direction in ['Ingress', 'Egress']:
				if _P[direction] != []:
					if 'MAP' not in out['ports'][__Port].keys():
						out['ports'][__Port]['MAP'] = {}
					for pairedP in _P[direction]:
						if type(pairedP) is str:
							if pairedP not in out['ports'][__Port]['MAP'].keys():
								out['ports'][__Port]['MAP'][pairedP] = []
							out['ports'][__Port]['MAP'][pairedP].append(direction)
						elif type(pairedP) is list:
							for pairedPP in pairedP:
								if pairedPP not in out['ports'][__Port]['MAP'].keys():
									out['ports'][__Port]['MAP'][pairedPP] = []
								out['ports'][__Port]['MAP'][pairedPP].append(direction)	
			# print(_P)
		return(out)

def FormatByType(input1):
	if type(input1) in [str, int]: return(input1)
	elif type(input1) == list:
		if len(input1) == 1: return(input1[0])
		else: return(str(input1))

def FormatLeptonDashboard(LINV):
	result = {}
	for lPort in LINV['ports']:
		result[lPort] = {'Description':'','PhyLink':'','Protocol':'','MAP':'','Model':'', 'Sfp':{}, 'Velocity':''}
		if 'MAP' in LINV['ports'][lPort].keys():
			result[lPort]['MAP'] = list(LINV['ports'][lPort]['MAP'].keys())[0]
		result[lPort]['Model'] = LINV['ports'][lPort]['linecard']['Model']
		for top in ['Description', 'PhyLink', 'Protocol','ModulePresent','Speed']:
			result[lPort][top] = FormatByType(LINV['ports'][lPort][top])
		if result[lPort]['ModulePresent']:
			if 'Sfp' in LINV['ports'][lPort].keys(): sfpType = 'Sfp'
			else: sfpType = 'Qsfp'
			for top2 in ['VendorName', 'VendorPartNumber', 'TxPower', 'RxPower']:
				result[lPort]['Sfp'][top2] = FormatByType(LINV['ports'][lPort][sfpType][top2])
				flags = []
				for flag in ['RxLOL', 'RxLOS', 'TxDisable', 'TxFault', 'TxLOL', 'TxLOS','ModuleReady']:
					if FormatByType(LINV['ports'][lPort][sfpType][flag]): flags.append(flag)
				result[lPort]['Sfp']['flags'] = str(flags)
	return(result)

#{'Port': '2.63', 'Mode': 'Online', 'PhyLink': ['NUL'], 'Ingress': [], 'Egress': []}
#{'Port': '2.64', 'Mode': 'Online', 'PhyLink': ['NUL'], 'Ingress': [], 'Egress': []}
#{'Port': '3.1', 'Mode': 'Online', 'PhyLink': ['UP', 'UP', 'UP', 'UP'], 'Ingress': ['3.2'], 'Egress': [['3.2']]}
#{'Port': '3.2', 'Mode': 'Online', 'PhyLink': ['UP', 'UP', 'UP', 'UP'], 'Ingress': ['3.1'], 'Egress': [['3.1']]}

# LEP = LEPTON(wc.argv_dict['IP'], wc.argv_dict['user'], wc.argv_dict['pass'])
# status = LEP.GetStatus()
# for p in status['ports'].keys():
#	wc.pairprint(p, wc.lunique(status['ports'][p]['PhyLink']))

# wc.jd(status['ports']['1.64'])

# 
# # Apply LEPTON class to VELOCITY-INVENTORY-LEPTON
# for port in status['ports'].keys():
# 	speed = wc.lunique(status['ports'][port]['Speed'])
# 	if len(speed) == 1:
# 		speed = speed[0]
# 	else:
# 		speed = ' '.join(speed)
# 	wc.pairprint(port,speed)
