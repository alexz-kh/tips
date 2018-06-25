#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
https://askubuntu.com/questions/578257/how-to-get-the-package-description-using-python-apt
https://apt.alioth.debian.org/python-apt-doc/library/index.html
"""
import apt
import apt_pkg
from aptsources.sourceslist import SourcesList
import tempfile,os,sys
import six
import copy
from pprint import pprint, pformat
import logging as LOG

import lib as ut
import old_run as old

try:
    import ipdb
except ImportError:
    print("no ipdb")


LOG.basicConfig(level=LOG.DEBUG, datefmt='%Y-%m-%d %H:%M:%S',
                format='%(asctime)-15s - [%(levelname)s] %(module)s:%(lineno)d: '
                       '%(message)s', )


cfgFile = os.environ.get("CONFIG_FILE", "config_infra.yaml")
SAVE_YAML = ut.str2bool(os.environ.get("SAVE_YAML", True))
GERRIT_CACHE = ut.str2bool((os.environ.get("GERRIT_CACHE", False)))

#########
repos= {
    'apt_xenial_testing_salt' : {
        "type" : 'deb',
        "uri" : 'http://apt.mirantis.com/xenial',
        "dist" : 'testing',
        "orig_comps" : ['salt',],
        "comment" : 'qwe',
    },
    'apt_os_pike_nightly_main' : {
        "type" : 'deb',
        "uri"  : 'http://apt.mirantis.com/xenial/openstack/pike/',
        "dist"  : 'nightly',
        "orig_comps" : ['main',],
        "comment" : 'os.pike.nightly'
    },
    'apt_os_pike_testing_main' : {
        "type" : 'deb',
        "uri"  : 'http://apt.mirantis.com/xenial/openstack/pike/',
        "dist"  : 'testing',
        "orig_comps" : ['main',],
        "comment" : 'os.pike.testing'
    },
    'apt_os_pike_proposed_main' : {
        "type" : 'deb',
        "uri"  : 'http://apt.mirantis.com/xenial/openstack/pike/',
        "dist"  : 'proposed',
        "orig_comps" : ['main',],
        "comment" : 'os.pike.proposed'
    },
    'uca_queens_xenial_upd_main' : {
        "type" : 'deb',
        "uri"  : 'http://ubuntu-cloud.archive.canonical.com/ubuntu',
        "dist"  : 'xenial-updates/queens',
        "orig_comps" : ['main',],
        "comment" : 'uca_queens_main'
    },
    'uca_queens_xenial_main' : {
        "type" : 'deb',
        "uri"  : 'http://ubuntu-cloud.archive.canonical.com/ubuntu',
        "dist"  : 'xenial-updates/queens',
        "orig_comps" : ['main',],
        "comment" : 'uca_queens_main'
    },
    'apt_xenial_nightly_extra' : {
        "type" : 'deb',
        "uri"  : 'http://apt.mirantis.com/xenial/',
        "dist"  : 'nightly',
        "orig_comps" : ['extra',],
        "comment" : 'extra_main'
    }

}
#########

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

def get_pkgs(cache,return_all_v=False):
    """
    cache should contain only one source - unless 'dupicates' check usless.
    Return: always 'candidate' version will be.
    """
    pkgs = {}
    duplicates = {}
    for pkg in cache:
        if len(pkg.versions) > 1:
            duplicates[pkg.name] = {}
            for v in pkg.versions.keys():
                duplicates[pkg.name][v] = pkg.versions[v].origins
            LOG.error("miltiply versions detected:\n{}".format(pformat(duplicates)))
        if return_all_v:
          all_v = {}
          for v in pkg.versions.keys():
              all_v[v] = { 'source_name' : pkg.versions[v].source_name,
                           'archive' : pkg.versions[v].origins[0].archive,
                           'Private-Mcp-Spec-Sha': pkg.versions[v].record.get('Private-Mcp-Spec-Sha',None),
                           'Private-Mcp-Code-Sha': pkg.versions[v].record.get('Private-Mcp-Code-Sha',None)}
          pkgs[pkg.name] = { 'versions' : all_v }
        # Candidate, might not always be 'latest' - its depends on apt priorit.
        latest_v = pkg.candidate
        pkgs[pkg.name] = { 'source_name' : latest_v.source_name,
                           'archive' : latest_v.origins[0].archive,
                           'version' : latest_v.version,
                           'Private-Mcp-Spec-Sha': latest_v.record.get('Private-Mcp-Spec-Sha',None),
                           'Private-Mcp-Code-Sha': latest_v.record.get('Private-Mcp-Code-Sha',None)
                          }
    return pkgs,duplicates


def sort_by_source(pkgs):
    """
    Always guessing from one version, so work only over 'version' key
    """
    _pkgs = copy.deepcopy(pkgs)
    rez = {}
    k = ""
    for pkg in _pkgs.keys():
      # Always for 1st version
      src = _pkgs[pkg]['source_name']
      k = ""
      rez[src] = {"pkgs" : [k for k in _pkgs.keys() if _pkgs[k]['source_name'] == src ],
                  'archive' : _pkgs[pkg]['archive'],
                  'version' : _pkgs[pkg]['version'],
                  'Private-Mcp-Spec-Sha': _pkgs[pkg]['Private-Mcp-Spec-Sha'],
                  'Private-Mcp-Code-Sha': _pkgs[pkg]['Private-Mcp-Code-Sha'],
                  'source_name': src }
    return rez

def get_one_list(listnames,private=True):
    '''
    listnames=['zz1']
    '''
    import shutil

    rootdir = tempfile.mkdtemp()
    apt_conf_path = setup_apt(rootdir=rootdir)
    sources_list = SourcesList()
    for l_name in listnames:
        sources_list.add(**repos[l_name])
    sources_list.save()
    cache = apt.Cache(rootdir=rootdir)
    cache.update()
    cache.open()
    pkgs, duplicates = get_pkgs(cache)
    s_source = sort_by_source(pkgs)
    try:
        shutil.rmtree(rootdir)
        LOG.debug("Directory removed: {}".format(rootdir))
    except(OSError, e):
        LOG.warning("Error: %s - %s." % (e.filename,e.strerror))
        pass
    cache.close()
    if not private:
        for i in s_source.keys():
            s_source[i].pop('Private-Mcp-Spec-Sha',None)
            s_source[i].pop('Private-Mcp-Code-Sha',None)
    return s_source

if __name__ == '__main__':
    rootdir = tempfile.mkdtemp()
    print(rootdir)
    ipdb.set_trace()
    extra = get_one_list(['apt_xenial_nightly_extra'])
    os_pike = get_one_list(['apt_os_pike_proposed_main'])
    notin = []
    for k in extra.keys():
        if k not in os_pike.keys():
            notin.append(k)
    ipdb.set_trace()
    ####
    apt_conf_path = setup_apt(rootdir=rootdir)
    sources_list = SourcesList()
#    sources_list.add(**repos['apt_os_pike_testing_main'])
#    sources_list.add(**repos['apt_xenial_testing_salt'])
#    sources_list.add(**repos['uca_queens_xenial_upd_main'])
#    sources_list.add(**repos['uca_queens_xenial_main'])
    sources_list.add(**repos['apt_xenial_nightly_extra'])
    sources_list.add(**repos['apt_os_pike_proposed_main'])
    sources_list.save()
    cache = apt.Cache(rootdir=rootdir)
    cache.update()
    cache.open()

    pkgs_os_pike_testing, duplicates = get_pkgs(cache)

    s_source = sort_by_source(pkgs_os_pike_testing)
    zz = {}
    for i in s_source.keys(): zz[i] = { 'pkgs' : s_source[i]['pkgs'], 'version': s_source[i]['version']}
    ipdb.set_trace()
    ###############

    # HOVNOSCRIPT!
    """
    GERRIT_CACHE=True
    SAVE_YAML=True
    CONFIG_FILE=config_infra.yaml
    ./run.py "apt_os_pike_testing_main"
    """
    cfg = ut.read_yaml(cfgFile)
    reponame = ut.list_get(sys.argv, 1, 'apt_os_pike_testing_main')

    save_mask = os.path.join(
        "rez_" + reponame.replace('/', '_') + "_" + cfgFile.replace('.yaml',
                                                                     ""),
        "rez_" + reponame.replace('/', '_'))

    _git_listfile = "{}_git_list.yaml".format(save_mask)

    if GERRIT_CACHE and os.path.isfile(_git_listfile):
        current_git_list = ut.read_yaml(_git_listfile)
        LOG.warning("Cache used :{}".format(_git_listfile))
    else:
        current_git_list = old.get_current_list(cfg)
        ut.save_yaml(current_git_list, _git_listfile)

    ipdb.set_trace()
    LOG.info("ZZ")
    if SAVE_YAML:
      ut.save_yaml(pkgs_os_pike_testing, "{}_pkgs_all.yaml".format(save_mask))
      ut.save_yaml(s_source, "{}_pkgs_by_source.yaml".format(save_mask))
      ut.save_yaml(duplicates, "{}_pkgs_duplicates.yaml".format(save_mask))


