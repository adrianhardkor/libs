#!/usr/bin/env python3
import wcommon as wc
import json

data = json.loads(wc.read_file(wc.argv_dict['fname']))



add = {}
intf = {}





phys = {}
for line in data['1show int']:
	cline = wc.cleanLine(line)
	if len(cline) < 3: continue
	# if '241' in line: print(line)
	if cline[-4:-1] == ['line', 'protocol', 'is']:
		interface = cline[-7]
		flag = False
		phys[wc.icx_interface_format(interface)] = interface
		intf[interface] = {'status':'/'.join([cline[-5],cline[-1]])}
	elif cline[2] == 'for': 
		intf[interface]['statusFor'] = line[13:].strip().replace('or', '').strip()
	elif cline[0:2] == ['Hardware', 'is']:
		intf[interface]['mac'] = cline[5]
	elif cline[0:2] == ['Configured', 'speed']:
		intf[interface]['speed'] = {'configured':cline[2], 'actual':cline[4]}
		intf[interface]['duplex'] = {'configured': cline[7], 'actual':cline[9]}
	elif cline[0:3] == ['Configured', 'mdi', 'mode']:
		intf[interface]['mdi'] = {'configured': cline[3], 'actual':cline[5]}
	elif 'port state is' in line:
		segment2 = []
		segment = line.split(',')
		# print(segment)
		for s in segment:
			s = wc.cleanLine(s.strip())
			segment2.append(s)
		intf[interface]['vlan'] = {}
		try:
			intf[interface]['vlan'] = {'carrying num of vlans': int(segment2[0][3])}
		except Exception:
			if segment2[0][0:5] == ['Untagged', 'member', 'of', 'L2', 'VLAN']: intf[interface]['vlan']['access'] = segment2[0][-1]
		intf[interface]['port state'] = cline[-1]
	elif cline[0] == 'MACsec': intf[interface]['MACsec'] = cline[-1]
	elif cline[0] == 'MTU': intf[interface]['MTU'] = cline[1]
	elif cline[0:3] == ['Internet', 'address', 'is']: 
		intf[interface]['ip'] = {'ip': cline[3].split('/')[0], 'cidr':cline[3].split('/')[-1], 'network': wc.IP_get(cline[3])[0]}
		add[cline[3].split('/')[0]] = interface
for mac in data['2show mac-address all']:
	cmac = wc.cleanLine(mac)
	if len(cmac) != 5: continue
	if cmac[1] in phys.keys():
		intf[phys[cmac[1]]]['arp'] = {'mac': cmac[0], 'type':cmac[2], 'vlan':cmac[3], 'action':cmac[4]}
		# wc.pairprint(cmac, phys[cmac[1]])




wc.jd(result)
# wc.jd(phys)
