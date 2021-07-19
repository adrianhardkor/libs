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
	epics = {}
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
	for issue in issues:
		story = str(issue)
		results[story] = dirClassJIRA(issue.fields)
		if results[story]['issuetype'] == 'Epic': epics[story] = results.pop(story); continue
		for field in fields.keys():
			if fields[field] == -1: continue
			if field in results[story].keys():
				if type(fields[field]) == list:
					for f in fields[field]:
						if f not in results[story][field]: results.pop(story)
				else:
					if fields[field] not in results[story][field]: results.pop(story)
			else: results.pop(story)
		# if 'customfield_10006' in results[story].keys(): epics[results[story]['customfield_10006']] = results.pop(story)
	return(results)

# wc.jd(dirClassJIRA(issue.fields))
wc.jd(get_all_issues(jira, wc.argv_dict['board'], {'components':wc.argv_dict['components']}))
# ['id','labels','issuetype','priority']))

