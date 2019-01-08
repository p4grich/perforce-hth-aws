#!/bin/bash

# salt-deploy.sh
SALT_ROOT="$1"
PASSWORD="$2"
SWARMURL="$3"

APPUSER="applications"

function die
{
	echo "$1" && exit 1
}

if [ ! -e /srv/salt ] ; then
	ln -s $SALT_ROOT/salt/states /srv/salt
fi

if [ ! -e /srv/pillar ] ; then
	ln -s $SALT_ROOT/salt/pillar /srv/pillar
fi

if [ "$PASSWORD" == "" ]; then
	PASSWORD="pa55wOrd"
fi

echo "syncing salt..."
salt '*' saltutil.sync_all || die "salt sync failed"

echo "refreshing pillar data"
salt '*' saltutil.refresh_pillar || die "refresh pillar failed"

echo "updating mines"
salt '*' mine.update || die "failed to update mine data"

# set up the router so it can reach the services as they come up
# this isn't great but otherwise we need direct wiring across all nodes or two "apply" states,
# one for pre-deploy (our network only) and one for post (world)
# alternatively the AWS template could hold off (?) on applying the final security group until
# we get to a complete state
echo "apply master states..."
salt 'master' state.apply || die "failed to setup the master"

# first create the default p4d (the main broker is unconfigured, so no access from the outside yet)
echo "apply p4d states..."
salt 'p4d-host' state.apply || die "failed to apply salt states to the p4d host"
# now configure the super password, configure security, etc.
echo "setup p4d..."
salt 'p4d-host' p4d.setup $APPUSER $PASSWORD || die "failed to setup p4d host"

# now grab the long timeout token for other application services
LTO_TOKEN=$(salt --out=raw 'p4d-host' p4d.get_ticket $APPUSER $PASSWORD | sed "s/[^:]*:[ ]*'\([^']*\)'.*/\1/")
if [ ! $? -eq 0 ]; then
	die "failed to get the LTO token"
else
	echo "LTO token for $APPUSER is $LTO_TOKEN"
fi

# set up the app server
echo "apply app-host states..."
salt 'app-host' state.apply || die "failed to apply salt states to the app host"

# configure the services
echo "setup swarm..."
salt 'app-host' app.setup_swarm super $PASSWORD $APPUSER $LTO_TOKEN $SWARMURL || die "failed to deploy swarm"
echo "setup swarm-cron..."
salt 'app-host' app.setup_swarmcron || die "failed to deploy swarm-cron"

# done!
echo "done!"
