FROM ubuntu:16.04

# a few minor docker-specific tweaks
# see https://github.com/docker/docker/blob/master/contrib/mkimage/debootstrap
RUN set -xe \
	\
	&& echo '#!/bin/sh' > /usr/sbin/policy-rc.d \
	&& echo 'exit 101' >> /usr/sbin/policy-rc.d \
	&& chmod +x /usr/sbin/policy-rc.d \
	\
	&& dpkg-divert --local --rename --add /sbin/initctl \
	&& cp -a /usr/sbin/policy-rc.d /sbin/initctl \
	&& sed -i 's/^exit.*/exit 0/' /sbin/initctl \
	\
	&& echo 'force-unsafe-io' > /etc/dpkg/dpkg.cfg.d/docker-apt-speedup \
	\
	&& echo 'DPkg::Post-Invoke { "rm -f /var/cache/apt/archives/*.deb /var/cache/apt/archives/partial/*.deb /var/cache/apt/*.bin || true"; };' > /etc/apt/apt.conf.d/docker-clean \
	&& echo 'APT::Update::Post-Invoke { "rm -f /var/cache/apt/archives/*.deb /var/cache/apt/archives/partial/*.deb /var/cache/apt/*.bin || true"; };' >> /etc/apt/apt.conf.d/docker-clean \
	&& echo 'Dir::Cache::pkgcache ""; Dir::Cache::srcpkgcache "";' >> /etc/apt/apt.conf.d/docker-clean \
# https://github.com/docker/docker/blob/9a9fc01af8fb5d98b8eec0740716226fadb3735c/contrib/mkimage/debootstrap#L134-L151
	&& echo 'Apt::AutoRemove::SuggestsImportant "false";' > /etc/apt/apt.conf.d/docker-autoremove-suggests \
	\
	&& echo 'Acquire::Languages "none";' > /etc/apt/apt.conf.d/docker-no-languages \
	\
	&& echo 'Acquire::GzipIndexes "true"; Acquire::CompressionTypes::Order:: "gz";' > /etc/apt/apt.conf.d/docker-gzip-indexes \
	\
	&& echo 'APT::Get::Install-Recommends "false"; APT::Get::Install-Suggests "false";' > /etc/apt/apt.conf.d/docker-recommends


# delete all the apt list files since they're big and get stale quickly
RUN rm -rf /var/lib/apt/lists/*

# make systemd-detect-virt return "docker"
# See: https://github.com/systemd/systemd/blob/aa0c34279ee40bce2f9681b496922dedbadfca19/src/basic/virt.c#L434
RUN mkdir -p /run/systemd && echo 'docker' > /run/systemd/container

# enable the universe
#RUN sed -i 's/^#\s*\(deb.*universe\)$/\1/g' /etc/apt/sources.list
RUN set -xe ; cd /etc/apt/ && echo > sources.list \
	&& echo "deb http://ua.archive.ubuntu.com/ubuntu/ xenial main restricted universe multiverse" >> sources.list \
	&& echo "deb http://ua.archive.ubuntu.com/ubuntu/ xenial-updates main restricted universe multiverse" >> sources.list \
	&& echo "deb http://ua.archive.ubuntu.com/ubuntu/ xenial-backports main restricted universe multiverse" >> sources.list \
	&& apt update && apt upgrade -y \
	&& apt install screen vim wget curl python-pip python3-pip python-virtualenv python3-virtualenv python-yaml -y \
#https://downloads.chef.io/chefdk
	&& cd /root/ && wget https://packages.chef.io/files/stable/chefdk/2.4.17/ubuntu/16.04/chefdk_2.4.17-1_amd64.deb \
	&& dpkg -i chefdk_2.4.17-1_amd64.deb \
	&& apt clean


# overwrite this with 'CMD []' in a dependent Dockerfile
CMD ["/bin/bash"]


# Build:
# docker build -t ubuntu_16_quick_test .
