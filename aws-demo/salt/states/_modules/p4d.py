import salt
from P4 import P4, P4Exception
import sys
import platform
import string
import random

def status():
	return "installed"

def setup(appuser, password):
	# we should be able to connect to the local P4 on 1666
	p4 = P4()
	p4.port = "localhost:1666"
	p4.user = "super"
	try:
		p4.connect()
		table = p4.run("protect", "-o")[0]
		p4.run("protect", "-i")
		# store all depots in /depots (only metadata in /p4/metadata)
		p4.run("configure", "set", "server.depot.root=/p4/depots");
		# set up some security
		p4.run("configure", "set", "run.users.authorize=1")
		p4.run("configure", "set", "dm.user.noautocreate=2")
		p4.run("configure", "set", "cluster.id=yourserver")
		p4.run("configure", "set", "dm.keys.hide=2")
		p4.run("configure", "set", "dm.keys.hide=2")
		p4.run("configure", "set", "monitor=2")
		p4.run("configure", "set", "lbr.autocompress=1")
		# structured logging
		# 3 -> errors
		# 6 -> user
		# 7 => events
		# 8 => integrity
		p4.run("configure", "set", "serverlog.file.3=errors.csv")
		p4.run("configure", "set", "serverlog.maxmb.3=256")
		p4.run("configure", "set", "serverlog.retain.3=4")
		p4.run("configure", "set", "serverlog.file.6=errors.csv")
		p4.run("configure", "set", "serverlog.maxmb.6=256")
		p4.run("configure", "set", "serverlog.retain.6=4")
		p4.run("configure", "set", "serverlog.file.7=errors.csv")
		p4.run("configure", "set", "serverlog.maxmb.7=256")
		p4.run("configure", "set", "serverlog.retain.7=4")
		p4.run("configure", "set", "serverlog.file.8=errors.csv")
		p4.run("configure", "set", "serverlog.maxmb.8=256")
		p4.run("configure", "set", "serverlog.retain.8=4")
		# now secure the password
		p4.run("configure", "set", "security=3")
		p4.run_password("", password)
		p4.password = password
		p4.run_login()
		# create an "applications" user
		p4.input = p4.run("user","-o",appuser)[0]
		p4.run("user","-i","-f")
		# modify protects to make it an admin user
		table = p4.run("protect", "-o")[0]
		table["Protections"].append("admin user " + appuser + " * //...")
		p4.input = table
		p4.run("protect", "-i")
		# set up a long timeout group for the appuser
		group = p4.run_group("-o", "long_timeout")[0]
		group['Timeout'] = 'unset'
		group['Users'] = [appuser]
		p4.input = group
		p4.run("group", "-i")
		# set the app user password (random)
		app_pass = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(26))
		p4.input = [ app_pass, app_pass ]
		p4.run("passwd", appuser)

		return "OK"
	except P4Exception:
		return p4.errors

def get_ticket(user, super_password):
	# we should be able to connect to the local P4 on 1666
	p4 = P4()
	p4.port = "localhost:1666"
	p4.user = "super"
	p4.password = super_password

	try:
		p4.connect()
		p4.run_login()

		return p4.run_login("-p","-a",user)[0]
	except P4Exception:
		return p4.errors
