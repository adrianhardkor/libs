#!/usr/bin/env python3
import os
import sys
import wcommon as wc
import re
import jinja2
import requests
import json
import gitlab

# timer = wc.timer_index_start()
class GITLAB():
	def __init__(self, url, token, project):
		pass
		self.url = url
		self.token = token
		self.handle = gitlab.Gitlab(self.url, private_token=self.token,api_version=4,ssl_verify=False)
		self.handle.auth()
		self.project = self.handle.projects.get(project)
		# self.project = self.handle.projects.list()
		# print(self.project)
	def GetFiles(self, path, ref='master'):
		results = {}
		data = self.project.repository_tree(ref=ref, all=True)
		for d in data:
			extension = d['name'].split('.')[-1].lower()
			if extension in ['yaml', 'yml']:
				# YAML
				wc.log_fname(wc.bytes_str(self.project.repository_raw_blob(d['id'])), d['id'])
				results[d['name']] = wc.read_yaml(d['id'])
				wc.rmf(d['id'])
				wc.pairprint(d['name'], 'yaml') 
			elif extension == 'json':
				# JSON
				results[d['name']] = json.loads(wc.bytes_str(self.project.repository_raw_blob(d['id'])))
				wc.pairprint(d['name'], 'json')
			elif extension in ['j2', 'jinja', 'jinja2']:
				results[d['name']] = wc.bytes_str(self.project.repository_raw_blob(d['id']))
				wc.pairprint(d['name'],'j2')
			else:
				# REGULAR FILE
				try:
					results[d['name']] = wc.bytes_str(self.project.repository_raw_blob(d['id'])).split('\n')
				except Exception:
					pass
				wc.pairprint(d['name'], 'line')

		return(results)

# G = GITLAB('https://pl-acegit01.as12083.net/', wc.env_dict['GITLAB_TOKEN'], 300)
# wc.jd(G.GetFiles('asset-data/'))
# print(wc.timer_index_since(timer))

