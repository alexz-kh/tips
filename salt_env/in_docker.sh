#!/bin/bash -xe

export CLUSTER_NAME=mcp-offline
export CLUSTER_MODEL=https://github.com/Mirantis/mcp-offline-model.git
export CLUSTER_MODEL_REF=master
export MCP_VERSION=nightly
export DISTRIB_REVISION=2018.1
export EXTRA_FORMULAS="ntp aptly nginx iptables docker"
# run bootstrap script
apt-get update
apt-get install vim wget curl -y
bash -x /tests/scripts/mirror-image/salt-bootstrap.sh
