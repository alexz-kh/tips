#!/bin/bash
mkdir -p lists
pushd lists/
curl http://apt.mirantis.com.s3.amazonaws.com/xenial/openstack/pike/dists/nightly/main/binary-amd64/Packages.gz | zcat > apt.os.pike.nightly
curl http://apt.mirantis.com.s3.amazonaws.com/xenial/openstack/pike/dists/proposed/main/binary-amd64/Packages.gz | zcat > apt.os.pike.proposed
curl http://apt.mirantis.com.s3.amazonaws.com/xenial/openstack/pike/dists/testing/main/binary-amd64/Packages.gz | zcat > apt.os.pike.testing
curl https://mirror.mirantis.com/proposed/openstack-pike/xenial/dists/xenial/main/binary-amd64/Packages.gz | zcat > mirror.os.pike.proposed
#
curl http://apt.mirantis.com.s3.amazonaws.com/xenial/dists/nightly/salt/binary-amd64/Packages.gz | zcat > apt.salt.nightly
curl http://apt.mirantis.com.s3.amazonaws.com/xenial/dists/testing/salt/binary-amd64/Packages.gz | zcat > apt.salt.testing
curl http://apt.mirantis.com.s3.amazonaws.com/xenial/dists/proposed/salt/binary-amd64/Packages.gz | zcat > apt.salt.proposed
#
curl http://apt.mirantis.com.s3.amazonaws.com/xenial/dists/nightly/extra/binary-amd64/Packages.gz | zcat > apt.extra.nightly


popd

