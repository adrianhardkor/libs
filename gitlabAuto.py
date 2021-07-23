#!/usr/bin/env python3
import os
import sys
import wcommon as wc
import re
import jinja2
import requests
import json
import gitlab

timer = wc.timer_index_start()
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
	def GetFiles(self, path):
		results = {}
		ref = 'master'
		data = self.project.repository_tree(ref=ref, all=True)
		for d in data:
			try:
				# YAML
				wc.log_fname(wc.bytes_str(self.project.repository_raw_blob(d['id'])), d['id'])
				results[d['name']] = wc.read_yaml(d['id'])
				wc.rmf(d['id'])
			except Exception:
				try:
					# JSON
					results[d['name']] = json.loads(self.project.repository_raw_blob(d['id']))
				except Exception:
					try:
						# REGULAR FILE
						results[d['name']] = self.project.repository_raw_blob(d['id']).split('\n')
					except Exception:
						# folder?
						pass

		return(results)

# G = GITLAB('https://pl-acegit01.as12083.net/', wc.env_dict['GITLAB_TOKEN'], 300)
# wc.jd(G.GetFiles('asset-data/'))
# print(wc.timer_index_since(timer))

