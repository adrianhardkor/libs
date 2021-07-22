#!/usr/bin/env python3
import os
import sys
import wcommon as wc
import re
import jinja2
import requests
import json

class XRAY():
	def __init__(self, client_id, client_secret):
		self.client_id = client_id
		self.client_secret = client_secret
		self.BASEURL = "https://xray.cloud.xpand-it.com"
	def Authenticate(self):
		# data = wc.REST_POST(self.BASEURL + "/api/v2/authenticate", headers={'Content-Type':'application/json'}, args=json.dumps({'client_id':self.client_id,'client_secret':self.client_secret}), verify=False)
		response = requests.request('POST', self.BASEURL + "/api/v2/authenticate", headers={'Content-Type':'application/json'}, data=json.dumps({'client_id':self.client_id,'client_secret':self.client_secret}), verify=False)
		response_text = response.text.strip('"').strip()
		
		self.headers = {'Content-Type':'application/json', 'Authentication': 'Bearer ' + response_text}
		# self.token = wc.exec2('token=$(curl -H "Content-Type: application/json" -X POST --data @"cloud_auth.json" https://xray.cloud.xpand-it.com/api/v2/authenticate').strip('"').strip()
		return(response_text)
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

# X = XRAY('3FF73C08E84045E18AB30524991C67AF', "691a37d11648d0ab6b86860df69d77fb9e2c342e7fa1bdcc1d9cdfa3fde598d1")
# token = X.Authenticate()
# X.ImportCucumber(cucumber)
# print(token)
# wc.jd(X.headers)
# token=$(curl -H "Content-Type: application/json" -X POST --data @"cloud_auth.json" https://xray.cloud.xpand-it.com/api/v2/authenticate| tr -d '"')
# curl -H "Content-Type: application/json" -X POST -H "Authorization: Bearer $token"  --data @"report.json" https://xray.cloud.xpand-it.com/api/v2/import/execution/cucumber

