#!/usr/bin/env python3
import os
import sys
import wcommon as wc
import re
import jinja2
import requests
import json
import time

class XRAY():
	def __init__(self, client_id, client_secret):
		self.client_id = client_id
		self.client_secret = client_secret
		self.BASEURL = "https://xray.cloud.xpand-it.com"
	def Authenticate(self):
		# data = wc.REST_POST(self.BASEURL + "/api/v2/authenticate", headers={'Content-Type':'application/json'}, args=json.dumps({'client_id':self.client_id,'client_secret':self.client_secret}), verify=False)
		# response = requests.request('POST', self.BASEURL + "/api/v2/authenticate", headers={'Content-Type':'application/json'}, data=json.dumps({'client_id':self.client_id,'client_secret':self.client_secret}), verify=False)
		# response_text = response.text.strip('"').strip()
		# self.token = response_text
		# self.headers = {'Content-Type':'application/json', 'Authentication': 'Bearer ' + response_text}
		wc.log_fname(json.dumps({'client_id':self.client_id,'client_secret':self.client_secret}), 'cloud_auth.json')
		command = 'curl -H "Content-Type: application/json" -X POST --data @"cloud_auth.json" https://xray.cloud.xpand-it.com/api/v2/authenticate'
		# print(command)
		self.token = wc.exec2(command).strip('"').strip()
		wc.rmf('cloud_auth.json')
		return(self.token)
	def ImportCucumber(self, cucumber):
		wc.log_fname(json.dumps(cucumber), 'tmp.json')
		wc.jd(self.headers)
		data = json.loads(wc.REST_POST(self.BASEURL + '/api/v2/import/execution/cucumber', verify=False, headers=self.headers, args=json.dumps(cucumber)))
#		wc.log_fname(json.dumps(cucumber), 'report.json')
#		data = wc.exec2('curl -H "Content-Type: application/json" -X POST -H "Authorization: Bearer %s"  --data @"report.json" https://xray.cloud.xpand-it.com/api/v2/import/execution/cucumber' % self.token)
#		wc.rmf('report.json')
#		wc.jd(data.split('\n'))
		# wc.jd(self.headers)
		wc.jd(data)
		return(data)
	def ImportExecution(self, PASSED_FAILED, summary, description, parent_story, starttime):
                # current epoch (end):  time.time()
                # args['now'] = time.strftime('%Y-%m-%dT%H:%M:%S+01:00', time.localtime(args['now']))
		timer = time.strftime('%Y-%m-%dT%H:%M:%S+01:00', time.localtime(time.time())) 
		tests = [{'testKey':parent_story, 'start': starttime, 'finish':timer, 'comment':'execution ' + PASSED_FAILED, 'status':PASSED_FAILED}]
		bob_json = {'info':{'summary':summary,'description':description,'user':'jenkins'},'tests':tests}
		try:
			bob_json['info']['description'] = bob_json['info']['description'] + '\n\nRuntime:' + str(wc.timer_index_since(wc.validate))
		except Exception as err:
			bob_json['info']['description'] = bob_json['info']['description'] + '\n\nErr: ' + str(err)
		# wc.jd(bob_json)
		# wc.jd(self.headers)
		# print(self.BASEURL + '/api/v2/import/execution')
		# response = requests.request('POST', self.BASEURL + '/api/v2/import/execution', headers=self.headers, data=json.dumps(bob_json))
		# result = response.text

		wc.log_fname(json.dumps(bob_json), 'bob.json') 
		command = 'curl -H "Content-Type: application/json" -X POST -H "Authorization: Bearer ' + self.token + '"  --data @"bob.json" https://xray.cloud.xpand-it.com/api/v2/import/execution'
		# print(command)
		result = wc.exec2(command)
		wc.rmf('bob.json')
		
		print(result.split('\n'))
		return(result)
		# curl -H "Content-Type: application/json" -X POST -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0ZW5hbnQiOiJkMWFkMGEyZi04NDQ3LTM4OWQtODI0NS01ZDJlMWM1ZDYwNjEiLCJhY2NvdW50SWQiOiI2MDAwMTM3YTIwOGRiZjAxMDdmZDE2OTAiLCJpc1hlYSI6ZmFsc2UsImlhdCI6MTYyNjk4NTMwOCwiZXhwIjoxNjI3MDcxNzA4LCJhdWQiOiIzRkY3M0MwOEU4NDA0NUUxOEFCMzA1MjQ5OTFDNjdBRiIsImlzcyI6ImNvbS54cGFuZGl0LnBsdWdpbnMueHJheSIsInN1YiI6IjNGRjczQzA4RTg0MDQ1RTE4QUIzMDUyNDk5MUM2N0FGIn0.1sMJjaC6QvzDJMfuVTSbqWKKuFcqwkUTjDFmvc4RhWs"  --data @"bob.json" https://xray.cloud.xpand-it.com/api/v2/import/execution

# X = XRAY('3FF73C08E84045E18AB30524991C67AF', "691a37d11648d0ab6b86860df69d77fb9e2c342e7fa1bdcc1d9cdfa3fde598d1")
# token = X.Authenticate()
# X.ImportCucumber(cucumber)
# print(token)
# wc.jd(X.headers)
# token=$(curl -H "Content-Type: application/json" -X POST --data @"cloud_auth.json" https://xray.cloud.xpand-it.com/api/v2/authenticate| tr -d '"')
# curl -H "Content-Type: application/json" -X POST -H "Authorization: Bearer $token"  --data @"report.json" https://xray.cloud.xpand-it.com/api/v2/import/execution/cucumber

#{
#    "info" : {
#        "summary" : "Execution of automated DCIM validation",
#        "description" : "This execution was automatically created when importing execution results from an external source",
#        "user" : "jenkins"
#    },
#    "tests" : [
#        {
#            "testKey" : "XT-479",
#            "start" : "2021-07-22T11:47:35+01:00",
#            "finish" : "2021-07-22T11:50:56+01:00",
#            "comment" : "Successful execution",
#            "status" : "PASSED"
#        }
#     ]
#}
#
