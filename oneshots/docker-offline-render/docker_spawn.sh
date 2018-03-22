#!/bin/bash

code_tag=testing

volumes=" -v $(pwd):/test1 -v $(pwd)/mcp-offline-model:/srv/salt/reclass -v $(pwd)/salt-formulas-scripts:/srv/salt/scripts "
docker_image="ubuntu_16_quick_test"
opts=" ${volumes} -u root:root --hostname=apt01 --ulimit nofile=4096:8192 --cpus=2"

offline_model="https://github.com/Mirantis/mcp-offline-model"

function _prepare(){
  if [[ ! -d mcp-offline-model ]]; then
    git clone --recursive ${offline_model} mcp-offline-model
    pushd mcp-offline-model
      git checkout $code_tag
      git submodule update --init --recursive
    popd
  fi

  if [[ ! -d mcp-common-scripts ]]; then
    git clone https://github.com/Mirantis/mcp-common-scripts.git mcp-common-scripts
    pushd mcp-common-scripts
      git checkout ${code_tag}
    popd
  fi
  # used by scripts/salt_bootstrap.sh
  if [[ ! -d salt-formulas-scripts ]]; then
    git clone https://github.com/salt-formulas/salt-formulas-scripts salt-formulas-scripts
  #  pushd salt-formulas-scripts
  #    git checkout ${code_tag}
  #  popd
  fi
  if [[ ! -d packer-templates ]]; then
    git clone ssh://azvyagintsev@gerrit.mcp.mirantis.net:29418/mk/packer-templates packer-templates
  fi
}

function docker_run(){
  #docker run --rm ${opts} -it docker-offline-render:2018.1 /bin/bash
  docker run --rm ${opts} -it ${docker_image} /bin/bash
}



function run_in_docker(){
  set -x
  # https://raw.githubusercontent.com/Mirantis/mcp-common-scripts/master/mirror-image/salt-bootstrap.sh
  #

  pushd /test1/
  cp -rav packer-templates/mirror-image/files/* /
  rm -vf salt-formulas-scripts/.salt-master-setup.sh.passed
  # 
  export CLUSTER_NAME="mcp-offline"
  export FORMULA_VERSION=testing # from where install salt-formulas
  export PACKER_OFFLINE_BUILD=true
  bash -x packer-templates/mirror-image/scripts/salt_bootstrap.sh || true
}
# apt01.mcp-offline.local
# reclass -n apt01.mcp-offline.local -o json  | jq '.parameters.aptly.server.mirror | .[] | .source'
# reclass -n apt01.mcp-offline.local -o json  | jq '.parameters.docker.client.registry.image |.[] | .registry '



#docker pull ubuntu:16.04
#git clone git clone ssh://azvyagintsev@review.fuel-infra.org:29418/mk/packer-templates
#docker run -v $(pwd):/tests -u root:root --hostname=apt01 --ulimit nofile=4096:8192 --cpus=2 --rm -it  ubuntu:16.04 /bin/bash
## After it, you will be dropped into docker shell
## set env variables
#export CLUSTER_NAME=mcp-offline
#export CLUSTER_MODEL=https://github.com/Mirantis/mcp-offline-model.git
#export MCP_VERSION=testing
#export DISTRIB_REVISION=testing
##
#export CLUSTER_MODEL_REF=master
#export FORMULA_VERSION=testing
#export SALTSTACK_GPG="https://repo.saltstack.com/apt/ubuntu/16.04/amd64/2016.3/SALTSTACK-GPG-KEY.pub"
#export SALTSTACK_REPO="http://repo.saltstack.com/apt/ubuntu/16.04/amd64/2016.3 xenial main"
#export APT_MIRANTIS_GPG="http://apt.mirantis.com/public.gpg"
#export APT_MIRANTIS_SALT_REPO="http://apt.mirantis.com/xenial/ $FORMULA_VERSION salt"
#export GIT_SALT_FORMULAS_SCRIPTS="https://github.com/salt-formulas/salt-formulas-scripts"
#
##
#apt-get update && apt-get install wget curl sudo git-core vim jq -y
#cp -rv /tests/packer-templates/mirror-image/files/* /
## run bootstrap script
#export PACKER_OFFLINE_BUILD=true # push to use local one script, from /tmp/
#bash -x /tests/packer-templates/mirror-image/scripts/salt_bootstrap.sh
## Scripts will install salt-master and all salt-formulas, using offline model.
##Script may fail during installation-those  issue can be ignored. After it will done, you can check rendered output via reclass and jq (still in docker) :
#salt-key -L
## Accepted Keys:
## apt01.mcp-offline.local
## Show full render reclass for offline node:
#reclass -n apt01.mcp-offline.local



