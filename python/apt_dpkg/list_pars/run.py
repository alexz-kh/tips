#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
import sys
import os
import copy
import pprint as pprint
import logging as LOG

import tempfile
from shutil import copyfile

import lib as ut

LOG.basicConfig(level=LOG.DEBUG, datefmt='%Y-%m-%d %H:%M:%S',
                format='%(asctime)-15s - [%(levelname)s] %(module)s:%(lineno)d: '
                       '%(message)s', )

cfgFile = os.environ.get("CONFIG_FILE", "config_infra.yaml")
SAVE_YAML = os.environ.get("SAVE_YAML", False)

try:
  import ipdb
except ImportError:
  print("no ipdb")


def run_c(command):
  child = subprocess.Popen(command, stderr=subprocess.PIPE,
                           stdout=subprocess.PIPE, shell=True)
  child.wait()
  out, err = child.communicate()
  if DEBUG:
    print '###Command: \n%s\n%s' % (command, out)
  if err:
    print 'ERR:\n%s' % err
  return out, err


def get_current_list(_targets):
  """
  Took all from gerrit-ls
  and parse with target rules
  Return all project for all targets

  """
  current_proj_list = {}
  for t in cfg['targets']:
    new_gitrepo_cfg = []
    reportDump = []
    dst_root = cfg['targets'][t].get('dst_root', None)
    dump_to_file = NewGitrepoYamlMask + '_' + t + '.yaml'
    reportFile = dump_to_file.replace(os.path.basename(dump_to_file),
                                      "report_" + os.path.basename(
                                          dump_to_file))
    oldGitrepoCfgFile = OldGitrepoCfgFile + '_' + t + '.yaml'
    current_proj_list[t] = get_current_one_target(cfg['targets'][t])
  return current_proj_list


def get_current_one_target(_target):
  g_target = copy.deepcopy(_target)
  g_prefixes = g_target.get('prefixes', [])
  target_branches = g_target.get('branches_all', [])
  # Some projects have more then one branch for process.
  extra_branches = g_target.get('project_custom_branches', {}).values()
  resulted_dict = {}

  def _get_list(g_branches, _prefix):
    """
    Gerrit ls-project don't support multiple prefixes :(
    At least, our version.
    :param g_branches:
    :param _prefix:
    :return:
    """
    gerrit_host = cfg['gerrit_host']
    fd, t_path = tempfile.mkstemp()
    branches_string = ""
    clean_result = {}
    for branch in g_branches:
      branches_string += " --show-branch {}".format(branch)
    try:
      with os.fdopen(fd, 'w') as tmp:
        LOG.debug("Attemp to get project list from gerrit...")
        ut.execute(
            'ssh -p 29418', gerrit_host, 'gerrit',
            'ls-projects', branches_string, '--format json', '--prefix',
            _prefix, '--type CODE',
            check_exit_code=[0], logged=False,
            to_filename=t_path)
        result = ut.read_yaml(t_path)
        # Drop unneded info from gerrit
        for k, v in result.iteritems():
          if k in clean_result:
            LOG.eror("Duplicate detected:{}".format(k))
          clean_result[k] = {'branches': v['branches']}
        return clean_result
    finally:
      os.remove(t_path)

  # FIXME somehow make it pretty...
  # Have no idea how its work, some old black-magic.
  if extra_branches:
    extra_branches.sort()
    extra_branches = list(
        b_list for b_list, _ in itertools.groupby(extra_branches))
    for _tBranch in list(itertools.chain(*extra_branches)):
      if _tBranch not in target_branches:
        target_branches.append(_tBranch)
  for g_prefix in g_prefixes:
    resulted_dict.update(_get_list(target_branches, g_prefix))
  return resulted_dict


def parse_list(list_file):
  """
  Those fun parse unpacked Packages.gz text file
  """
  pkgs = {}
  l1 = ut.read_file(list_file)

  def process_one(l_start,l_end):
    priv_spec = 'err'
    priv_code = 'err'
    name      = 'err'
    version   = 'err'
    source    = False
    shift     = 0
    # catch whole pkg data, whole - till next empty line..
    for p in range(l_start, l_end):
      # stop on new section
      if l1[p] in ['\n', '\r\n']:
        shift = p
        break
      else:
        if l1[p].startswith('Package:'):
          name = l1[p].split('Package:')[1].replace(
              ' ', '').replace('\n', '')
        if l1[p].startswith('Private-Mcp-Code-Sha:'):
          priv_code = l1[p].split(
              'Private-Mcp-Code-Sha:')[1].replace(' ', '').replace('\n', '')
        if l1[p].startswith('Private-Mcp-Spec-Sha:'):
          priv_spec = l1[p].split(
              'Private-Mcp-Spec-Sha:')[1].replace(' ', '').replace('\n', '')
        if l1[p].startswith('Source:'):
          source = l1[p].split('Source:')[1].replace(
              ' ', '').replace('\n', '')
        if l1[p].startswith('Version:'):
          version = l1[p].split('Version:')[1].replace(
              ' ', '').replace('\n', '')


    pkg = {'Private-Mcp-Spec-Sha': priv_spec,
           'Private-Mcp-Code-Sha': priv_code,
           'source': source or name,
           'name': name,
           'version': [version] }
    return pkg,shift

  shift = 0
  for i in range(len(l1)):
    if i in range(shift) and not 0:
#      print("Skip:{}".format(i))
      continue
    if l1[i] in ['\n', '\r\n']:
#      print("Skip: empty")
      continue
    try:
      rez,shift = process_one(i,len(l1))
      if rez['name'] in pkgs.keys():
        # TODO , catch sha's and etc for duplicates
        LOG.warning('Duplicate pkgs:{}'.format(rez['name']))
        pkgs[rez['name']]['version'] = pkgs[rez['name']]['version'] +  rez['version']
      else:
        pkgs[rez['name']] = rez
    except Exception as e:
      LOG.error("Error parse packages section")
      sys.exit(1)
  return pkgs
#          if pkgs.get(name) not in ['err', None]:
#            # Check for value change, which mean inconsistence repo,
#            # aka same packages with diff versions
#            if pkgs[name]['Private-Mcp-Code-Sha'] != priv_spec:
#              print('ERR: priv_spec ' + name)
#              print(' Replacing {} => {}'.format(
#                  pkgs[name]['Private-Mcp-Code-Sha'], priv_spec))
#            if pkgs[name]['Private-Mcp-Code-Sha'] != priv_code:
#              print('ERR: priv_code ' + name)
#              print(' Replacing {} => {}'.format(
#                  pkgs[name]['Private-Mcp-Code-Sha'], priv_code))


if __name__ == '__main__':
  # HOVNOSCRIPT!
  """
  """
  cfg = ut.read_yaml(cfgFile)
  list_file = ut.list_get(sys.argv, 1, 'os.pike.nightly')
  save_mask = os.path.join("rez_" + list_file.replace('/','_') + "_" + cfgFile.replace('.yaml',"") ,"rez_" + list_file.replace('/','_') )
  # save_to configs
  # will be masked like:
  # dump_to_file = NewGitrepoYamlMask + gen_cfgFile['targets'].keys() + '.yaml'
  # new_gitrepoCfgFile_packages.yaml
  NewGitrepoYamlMask = os.path.join(cfg.get('drop', 'w1'),
                                    cfg.get('new_gitrepoCfgFileMask', 'gitrepoCfgFile'))
  OldGitrepoCfgFile = cfg.get(
      "old_gitrepoCfgFileMask", "old_gitrepoCfgFileMask")

  current_git_list = get_current_list(cfg['targets'])

  deb_pkgs = parse_list(list_file)

  # Check that deb exist in git's. KISS
  _specs = []
  for k in current_git_list['specs'].keys(): _specs.append(k.split('/')[-1])
  _openstack = []
  for k in current_git_list['openstack'].keys(): _openstack.append(k.split('/')[-1])
  _src = []
  for p in deb_pkgs.keys(): _src.append((deb_pkgs[p]['source']))
  _unic_src = set(_src)

  pkgs_not_spec = []
  pkgs_not_src = []
  for p in _unic_src:
    if p not in _specs:
      if p in cfg['targets']['specs'].get('project_blacklist',[]):
        LOG.info("Blacklisted from specs:{}".format(p))
        continue
      LOG.error("Not in spec:{}".format(p))
      pkgs_not_spec.append(p)
    if p not in _openstack:
      if p in cfg['targets']['openstack'].get('project_blacklist',[]):
        LOG.info("Blacklisted from openstack src:{}".format(p))
        continue
      LOG.error("Not in ospenstack src:{}".format(p))
      pkgs_not_src.append(p)

  pkgs_not_src.sort()
  pkgs_not_spec.sort()
  ut.save_yaml(pkgs_not_src, "{}_pkgs_not_src.yaml".format(save_mask))
  ut.save_yaml(pkgs_not_spec, "{}_pkgs_not_spec.yaml".format(save_mask))
  ipdb.set_trace()

  ##
  if not SAVE_YAML:
    LOG.info("Not going to save anything,Ciao!")
    sys.exit(0)
  # save all
  ut.save_yaml(deb_pkgs, "{}_all.yaml".format(save_mask))
  # with any err
  pkgs_e = {}
  for pkg in deb_pkgs.keys():
    if 'err' in deb_pkgs[pkg].values():
      pkgs_e[pkg] = deb_pkgs[pkg]
  ut.save_yaml(pkgs_e, "{}_with_any_err.yaml".format(save_mask))

  # with err in priv_spec
  pkgs_priv_spec_e = {}
  for pkg in deb_pkgs.keys():
    if 'err' in deb_pkgs[pkg]['Private-Mcp-Spec-Sha']:
      pkgs_priv_spec_e[pkg] = deb_pkgs[pkg]
  ut.save_yaml(pkgs_priv_spec_e,
               "{}_with_spec_err.yaml".format(save_mask))

  # with err in priv_code
  pkgs_priv_code_e = {}
  for pkg in deb_pkgs.keys():
    if 'err' in deb_pkgs[pkg]['Private-Mcp-Code-Sha']:
      pkgs_priv_code_e[pkg] = deb_pkgs[pkg]
  ut.save_yaml(pkgs_priv_code_e,
               "{}_with_code_err.yaml".format(save_mask))
  #
