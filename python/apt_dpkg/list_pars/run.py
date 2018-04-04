#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
import sys,os, copy
import pprint as pprint
import logging as LOG

import tempfile
from shutil import copyfile

import lib as ut

LOG.basicConfig(level=LOG.DEBUG, datefmt='%Y-%m-%d %H:%M:%S',
                format='%(asctime)-15s - [%(levelname)s] %(module)s:%(lineno)d: '
                       '%(message)s', )

cfgFile = os.environ.get("GEN_CONFIG_FILE", "config.yaml")

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
    dst_root = cfg['targets'][t].get('dst_root',None)
    dump_to_file = NewGitrepoYamlMask + '_' + t + '.yaml'
    reportFile = dump_to_file.replace(os.path.basename(dump_to_file),
                                      "report_" + os.path.basename(
                                          dump_to_file))
    oldGitrepoCfgFile = OldGitrepoCfgFile + '_' + t + '.yaml'
    current_proj_list[t] = get_current_one_target(cfg['targets'][t])
  return current_proj_list

def get_current_one_target(_target):
    g_target = copy.deepcopy(_target)
    g_prefixes = g_target.get('prefixes',[])
    target_branches = g_target.get('branches_all',[])
    # Some projects have more then one branch for process.
    extra_branches = g_target.get('project_custom_branches', {}).values()
    gerrit_host = "review.fuel-infra.org"
    resulted_dict = {}
    def _get_list(g_branches, _prefix):
        """
        Gerrit ls-project don't support multiple prefixes :(
        At least, our version.
        :param g_branches:
        :param _prefix:
        :return:
        """
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
                  clean_result[k] = {'branches' : v['branches'] }
                return clean_result
        finally:
            os.remove(t_path)

    # FIXME somehow make it pretty...
    # Have no idea how its work, some old black-magic.
    if extra_branches:
        extra_branches.sort()
        extra_branches = list(b_list for b_list, _ in itertools.groupby(extra_branches))
        for _tBranch in list(itertools.chain(*extra_branches)):
            if _tBranch not in target_branches:
                target_branches.append(_tBranch)
    for g_prefix in g_prefixes:
        resulted_dict.update(_get_list(target_branches, g_prefix))
    return resulted_dict


def main():
  pkgs = {}
  z1 = ''.join(read_file(pkgs_list_file))
  l1 = read_file()
  for i in range(len(l1)):
    # Start of pkg section
    if l1[i] in ['\n', '\r\n']:
      try:
        name = "err"
        priv_spec = 'err'
        priv_code = 'err'
        source = 'err'
        # catch whole pkg data, whole- till next empty line..
        for p in range(i + 1, len(l1)):
          if l1[p] in ['\n', '\r\n']:
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
        #name = source
        if pkgs.get(name) not in ['err', None]:
          # Check for value change, which mean inconsistence repo,
          # aka same packages with diff versions
          if pkgs[name]['priv_spec'] != priv_spec:
            print('ERR: priv_spec ' + name)
            print(' Replacing {} => {}'.format(
                pkgs[name]['priv_spec'], priv_spec))
          if pkgs[name]['priv_code'] != priv_code:
            print('ERR: priv_code ' + name)
            print(' Replacing {} => {}'.format(
                pkgs[name]['priv_code'], priv_code))
        # Drop last line issue FIXME should be catched somewhere before
        if name not in ['err', None]:
          # , 'source' : source }
          pkgs[name] = {'priv_spec': priv_spec, 'priv_code': priv_code}
      except:
        print("ERR")
        sys.exit(1)
        pass

  # save all
  save_yaml(pkgs, "{}_all.yaml".format(pkgs_list_file))
  # with any err
  pkgs_e = {}
 # ipdb.set_trace()
  for pkg in pkgs.keys():
    if 'err' in pkgs[pkg].values():
      pkgs_e[pkg] = pkgs[pkg]
  ut.save_yaml(pkgs_e, "{}_with_any_err.yaml".format(pkgs_list_file))
  # with err in priv_spec
  pkgs_priv_spec_e = {}
  for pkg in pkgs.keys():
    if 'err' in pkgs[pkg]['priv_spec']:
      pkgs_priv_spec_e[pkg] = pkgs[pkg]
  ut.save_yaml(pkgs_priv_spec_e, "{}_with_priv_spec_err.yaml".format(pkgs_list_file))
  # with err in priv_code
  pkgs_priv_code_e = {}
  for pkg in pkgs.keys():
    if 'err' in pkgs[pkg]['priv_code']:
      pkgs_priv_code_e[pkg] = pkgs[pkg]
  ut.save_yaml(pkgs_priv_code_e, "{}_with_priv_code_err.yaml".format(pkgs_list_file))
  #

if __name__ == '__main__':
  # HOVNOSCRIPT!
  """
  curl http://apt.mirantis.com.s3.amazonaws.com/xenial/openstack/pike/dists/nightly/main/binary-amd64/Packages.gz | zcat > os.pike.nightly
  curl http://apt.mirantis.com.s3.amazonaws.com/xenial/openstack/pike/dists/proposed/main/binary-amd64/Packages.gz | zcat > os.pike.proposed
  curl http://apt.mirantis.com.s3.amazonaws.com/xenial/openstack/pike/dists/testing/main/binary-amd64/Packages.gz | zcat > os.pike.testing
  curl https://mirror.mirantis.com/proposed/openstack-pike/xenial/dists/xenial/main/binary-amd64/Packages.gz | zcat > mirror.proposed
  #
  curl http://apt.mirantis.com.s3.amazonaws.com/xenial/dists/nightly/salt/binary-amd64/Packages.gz | zcat > salt.nightly
  curl http://apt.mirantis.com.s3.amazonaws.com/xenial/dists/testing/salt/binary-amd64/Packages.gz | zcat > salt.testing
  curl http://apt.mirantis.com.s3.amazonaws.com/xenial/dists/proposed/salt/binary-amd64/Packages.gz | zcat > salt.proposed
  #
  curl http://apt.mirantis.com.s3.amazonaws.com/xenial/dists/nightly/extra/binary-amd64/Packages.bz2 | zcat > extra.nightly
  """
  cfg = ut.read_yaml(cfgFile)
  # save_to configs
  # will be masked like:
  # dump_to_file = NewGitrepoYamlMask + gen_cfgFile['targets'].keys() + '.yaml'
  # new_gitrepoCfgFile_packages.yaml
  NewGitrepoYamlMask = os.path.join(cfg.get('drop','w1'),
                                    cfg.get('new_gitrepoCfgFileMask','gitrepoCfgFile'))
  OldGitrepoCfgFile = cfg.get("old_gitrepoCfgFileMask", "old_gitrepoCfgFileMask")

  ipdb.set_trace()
  get_current_git_list = get_current_list(cfg['targets'])

  ipdb.set_trace()
  pkgs_list_file = ut.list_get(sys.argv,1)

  main()
