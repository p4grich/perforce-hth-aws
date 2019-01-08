#!/bin/bash

# init.sh --ip (master ip addr) --id (master/p4d-host/etc.) --wait (URL to aws wait handle) --password (password for p4d super user)

die()
{
	echo "$1" && exit 1
}

restart_salt()
{
	# $1 is master or minior
	SALT_TYPE=$1
	service salt-$SALT_TYPE stop || die "failed to stop $SALT_TYPE"
	# sometimes python takes a bit to stop-stop
	RETRY=100
	for ITER in `seq 1 $RETRY`;
	do
		ps aux|grep python|grep -q salt-$SALT_TYPE
		if [ $? -eq 1 ]; then
			service salt-$SALT_TYPE start || die "failed to start $SALT_TYPE"
			return 0
		fi
		echo "Waiting for salt-$SALT_TYPE to stop"
		sleep 1
	done

	return 1
}

# basic argument parsing
# --ip (addr) --id (master/p4d-host/etc.) --wait (URL to aws wait handle) --password (password for p4d super user)
while [[ $# -gt 1 ]]; do
	key="$1"

	case $key in
    	--ip)
		    MASTER_IP="$2"
		    shift # past argument
		    ;;
	    --id)
		    ID="$2"
		    shift # past argument
		    ;;
	    --wait)
		    COMPLETE_URL="$2"
		    shift # past argument
		    ;;
	    --password)
		    PASSWORD="$2"
		    shift # past argument
		    ;;
		--swarmurl)
			SWARMURL="$2"
			shift # past argument
			;;
    	*)
            die "unknown option $key"
    ;;
esac
	shift # past argument or value
done

# echo "URL is $COMPLETE_URL" | logger

# setup the salt minion (and master)
if [ ! -e /etc/init.d/salt-minion ]; then
	yum install -y wget curl psmisc net-tools || die "failed to install curl"
	curl -o bootstrap_salt.sh -L https://bootstrap.saltstack.com || die "failed to get salt bootstrap"

	OPTS=""
	if [ "$ID" = "master" ]; then 
	  	yum install -y python-yaml || die "Failed to install python support on master."
		OPTS="-M -J {\"interface\":\"$MASTER_IP\",\"gitfs_remotes\":[\"https://github.com/robinsonj/perforce-formula\"],\"fileserver_backend\":[\"git\",\"roots\"]}"
	fi

	# umm, sometimes this appears to fail even though it's working?
	# the salt bootstrap code is prone to breaking, so either probably
	# find a version that works and only use that one
	bash bootstrap_salt.sh $OPTS

	if [ "$ID" = "master" ]; then 
	  yum install -y GitPython || die "Failed to install python support on master."
	  restart_salt master
	fi
fi

if [ "$ID" = "master" ]; then 
	DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
	# lame, but I get circualr refs in AWS if I pre-seed this based on the template, so detect it here
	# this will not work for a "production" system as it needs a real FQDN
	if [ "$SWARMURL" == "aws-detect" ]; then
		SWARMURL="https://$(curl http://169.254.169.254/latest/meta-data/public-ipv4)"
	fi
	# make sure to leave the --wait key for last as COMPLETE_URL may be blank
	setsid sh $DIR/key_wait.sh --password "$PASSWORD" --swarmurl "$SWARMURL" --wait "$COMPLETE_URL"
	echo "key_wait has been launched" | logger
fi

sed -i -e "s/#master:.*/master: $MASTER_IP/" -e "s/#id:.*/id: $ID/" /etc/salt/minion || die "failed to setup minion"
restart_salt minion || die "failed to restart minion"
