#!/bin/bash

# FIXME
# port from actual packer templates!

function _set_links(){
for formula_service in $(ls /usr/share/salt-formulas/reclass/service/ ); do
  echo -e "\n===Link service metadata for formula ${formula_service} ...\n"
  [ ! -L "/srv/salt/reclass/classes/service/${formula_service}" ] && \
    ln -s /usr/share/salt-formulas/reclass/service/${formula_service} /srv/salt/reclass/classes/service/${formula_service}
done
}

echo "deb [arch=amd64] http://apt.mirantis.com/xenial/ ${MCP_VERSION} salt" > /etc/apt/sources.list.d/mcp_salt.list
apt-get update
apt-get install git jq -y
apt-get install salt-formula* -y --allow-unauthenticated
git clone --recursive $CLUSTER_MODEL /srv/salt/reclass
pushd /srv/salt/reclass
git checkout $CLUSTER_MODEL_REF
git submodule update --init --recursive
popd

git clone https://github.com/salt-formulas/salt-formulas-scripts /srv/salt/scripts
# Parameters, for salt-formulas-scripts/bootstrap.sh
export FORMULAS_SOURCE=pkg
export HOSTNAME=apt01
export DOMAIN=$CLUSTER_NAME.local
export CLUSTER_NAME=$CLUSTER_NAME
export DISTRIB_REVISION=${MCP_VERSION}
/srv/salt/scripts/bootstrap.sh
_set_links || true
salt-call state.sls salt
echo "COMPLETED" > /srv/initComplete
