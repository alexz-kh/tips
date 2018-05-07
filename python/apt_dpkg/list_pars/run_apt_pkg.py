#!/bin/python

"""
https://askubuntu.com/questions/578257/how-to-get-the-package-description-using-python-apt
https://apt.alioth.debian.org/python-apt-doc/library/index.html
"""
import apt
import apt_pkg
import tempfile
import os
from pprint import pprint, pformat
import logging as LOG

#import lib as ut
try:
    import ipdb
except ImportError:
    print("no ipdb")


LOG.basicConfig(level=LOG.DEBUG, datefmt='%Y-%m-%d %H:%M:%S',
                format='%(asctime)-15s - [%(levelname)s] %(module)s:%(lineno)d: '
                       '%(message)s', )


from aptsources.sourceslist import SourcesList


APT_DIRS = [
    "etc/apt/sources.list.d",
    "etc/apt/preferences.d",
    "var/lib/apt/lists",
    "var/lib/dpkg",
]

APT_FILES = [
    "etc/apt/apt.conf",
    "etc/apt/sources.list",
    "var/lib/dpkg/status",
]

APT_CONF_ENTRIES = {
    'Dir': '{rootdir}',
    'Debug::pkgProlemResolver': 'true',
    'APT::Architecture': '{arch}',
    'APT::Install-Recommends': 'false',
    'APT::Get::AllowUnauthenticated': 'true',
}

def setup_apt(rootdir):
    # Create APT structure
    for x in APT_DIRS:
        os.makedirs(os.path.join(rootdir, x))

    # Touch APT files
    for x in APT_FILES:
        open(os.path.join(rootdir, x), "w").close()

    # Generate apt.conf
    apt_conf_path = os.path.join(rootdir, "etc/apt/apt.conf")
    apt_conf_opts = {
        'arch': os.environ.get("ARCH", "amd64"),
        'rootdir': rootdir,
    }
    with open(apt_conf_path, "w") as f:
        for key, value in APT_CONF_ENTRIES.items():
            f.write('{} "{}";'.format(key, value.format(**apt_conf_opts)))

    # Init global config object
    apt_pkg.init_config()
    apt_pkg.read_config_file(apt_pkg.config, apt_conf_path)
    apt_pkg.init_system()

    return apt_conf_path

def process_pkgs(cache):
    """
    cache should contain only one source - unless 'dupicates' check usless
    """
    pkgs = {}
    duplicates = {}
    for pkg in cache:
        if len(pkg.versions) > 1:
            duplicates[pkg.name] = {}
            for v in pkg.versions.keys():
                duplicates[pkg.name][v] = pkg.versions[v].origins
            LOG.error("miltiply versions detected:\n{}".format(pformat(duplicates)))
        all_v = {}
        for v in pkg.versions.keys():
            all_v[v] = { 'source_name' : pkg.versions[v].source_name,
                         'source_version' : pkg.versions[v].source_version,
                         'Private-Mcp-Spec-Sha': pkg.versions[v].record.get('Private-Mcp-Spec-Sha',None),
                         'Private-Mcp-Code-Sha': pkg.versions[v].record.get('Private-Mcp-Code-Sha',None)}
        pkgs[pkg.name] = { 'versions' : all_v }
    return pkgs,duplicates


if __name__ == '__main__':
    rootdir = tempfile.mkdtemp()
    print(rootdir)
    apt_conf_path = setup_apt(rootdir=rootdir)

    sources_list = SourcesList()
    sources_list.add(
        type='deb',
        uri='http://apt.mirantis.com/xenial',
        dist='testing',
        orig_comps=['salt',],
        comment='qwe',
    )
    sources_list.add(
        type='deb',
        uri='http://apt.mirantis.com/xenial/openstack/pike/',
        dist='testing',
        orig_comps=['main',],
        comment='os.pike.testing',
    )
    sources_list.save()

    cache = apt.Cache(rootdir=rootdir)
    cache.update()
    cache.open()

    ipdb.set_trace()
    all_pkgs = process_pkgs(cache)

    ipdb.set_trace()
    LOG.info("ZZ")



