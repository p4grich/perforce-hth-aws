import salt

import salt
import sys
import platform
import string
import random

def master_ip():
	return __salt__['mine.get']("master","network.interface_ip")['master']

def status():
	return "installed, master is at " + master_ip()

def setup_swarm(superuser, superpass, appuser, lto_password, swarm_url):
	dockerid = __salt__['cmd.run']("docker run --name swarm -p 80:80 -d --restart always dscheirer/swarm:0.0.2 " +
		" -u " + superuser + 
		" -P " + superpass + 
		" -s " + appuser + 
		" -S " + lto_password + 
		" -H " + master_ip() +
		" -p " + master_ip() + ":1666" +
		" -U " + swarm_url)
	# TODO: wait until port 80 is up?  
	return dockerid

def setup_swarmcron():
	return __salt__['cmd.run']("docker run --name swarmcron --restart always -d dscheirer/swarm-cron:0.0.1 -u http://" + master_ip())
