#!/usr/bin/env python3
import wcommon as wc
# library modules
from jira import JIRA
import json

def dirClassJIRA(classmate, fields=[]):
    result = {}
    temp = vars(classmate)
    for item in temp:
        if str(temp[item]) in ['None', '[]', '{}']: continue
        result[str(item)] = str(temp[item])
        if str(item) == 'description': result[str(item)] = result[str(item)].split('\n')
    return(result)



user = 'adrian.krygowski@wowinc.com'
server = 'https://wowinc.atlassian.net'
apikey = wc.env_dict['JIRA_TOKEN']

options = {
 'server': server
}

jira = JIRA(options, basic_auth=(user,apikey) )

if 'ticket' in wc.argv_dict.keys():
	ticket = wc.argv_dict['ticket']
	issue = jira.issue(ticket)
	wc.jd(dirClassJIRA(issue.fields)); exit()

def FormatJiraRaw(raw):
	wc.jd(wc.mcsplit(raw, ['{"','"}']))
	exit()

def get_all_issues(jira_client, project_name, fields):
	results = {}
	issues = []
	i = 0
	chunk_size = 100
	while True:
		# fields = fields.append('description') -- fields=fieldslist
		chunk = jira_client.search_issues(f'project = {project_name}', startAt=i, maxResults=chunk_size)
		i += chunk_size
		issues += chunk.iterable
		if i >= chunk.total:
			break
	wc.jd(fields)
	for issue in issues:
		# wc.jd(results[str(issue)])
		# FormatJiraRaw(results[str(issue)]['raw'])
		results[str(issue)] = dirClassJIRA(issue.fields)
		for field in fields.keys():
			if fields[field] == -1: continue
			if field in results[str(issue)].keys():
				# wc.pairprint(fields[field], results[str(issue)][field])
				if type(fields[field]) == list:
					for f in fields[field]:
						if f not in results[str(issue)][field]: results.pop(str(issue))
				else:
					if fields[field] not in results[str(issue)][field]: results.pop(str(issue))
			else: results.pop(str(issue))
	return(results)

# wc.jd(dirClassJIRA(issue.fields))
wc.jd(get_all_issues(jira, 'AARC', {'components':wc.argv_dict['components']}))
# ['id','labels','issuetype','priority']))

