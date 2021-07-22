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
		data = wc.REST_POST(self.BASEURL + "/api/v2/authenticate", headers={'Content-Type':'application/json'}, args=json.dumps({'client_id':self.client_id,'client_secret':self.client_secret}), verify=False)
		self.token = str(data)
		self.headers = {'Content-Type':'application/json', 'Authentication': 'Bearer ' + str(data)}
		return(data)
	def ImportCucumber(self, cucumber):
		data = wc.REST_POST(self.BASEURL + '/api/v2/import/execution/cucumber', verify=False, headers=self.headers, args=json.dumps(cucumber))
		wc.jd(data)
		return(data)


