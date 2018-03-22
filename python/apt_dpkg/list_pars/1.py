#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess,sys
import pprint as pprint
import json
import yaml


try:
  import ipdb 
except ImportError:
  print("no ipdb")
list_file = sys.argv[1]

def run_c(command):
  child = subprocess.Popen(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
  child.wait()
  out,err = child.communicate()
  if DEBUG:
    print '###Command: \n%s\n%s' % (command, out)
  if err:
    print 'ERR:\n%s' % err
  return out,err


def read_file():
  with open(list_file, 'r') as f:
    x = f.readlines()
  return x

def save_yaml(save_yaml,to_file):
  with open(to_file, 'w') as f2:
    f2.write(yaml.dump(save_yaml, default_flow_style=False))
  print("{} file saved".format(to_file))


def main():
  pkgs = {}
  z1 = ''.join(read_file())
  l1 = read_file()
  for i in range(len(l1)):
    # Start of pkg section
    if l1[i] in ['\n', '\r\n']:
      try:
        name = "err"
        priv_spec = 'err'
        priv_code = 'err'
        source = 'err'
        #catch whole pkg data, whole- till next empty line..
        for p in range(i+1, len(l1)):
          if l1[p] in ['\n', '\r\n']:
            break
          else:
            if l1[p].startswith('Package:'):
              name = l1[p].split('Package:')[1].replace(' ','').replace('\n','')
            if l1[p].startswith('Private-Mcp-Code-Sha:'):
              priv_code = l1[p].split('Private-Mcp-Code-Sha:')[1].replace(' ','').replace('\n','')
            if l1[p].startswith('Private-Mcp-Spec-Sha:'):
              priv_spec = l1[p].split('Private-Mcp-Spec-Sha:')[1].replace(' ','').replace('\n','')
            if l1[p].startswith('Source:'):
              source = l1[p].split('Source:')[1].replace(' ','').replace('\n','')
        #name = source
        if pkgs.get(name) not in ['err',None]:
          if pkgs[name]['priv_spec'] != priv_spec or pkgs[name]['priv_code'] != priv_code:
            print('ERR:\n' + name)
            print('Replace {} => {}\n{} => {}'.format(pkgs[name]['priv_spec'],priv_spec,pkgs[name]['priv_code'],priv_code) )
        # Drop last line issue FIXME should be catched somewhere before
        if name not in ['err',None]:
          pkgs[name] = { 'priv_spec': priv_spec, 'priv_code': priv_code} #, 'source' : source }
      except:
        print("ERR")
        sys.exit(1)
        pass

  # save all
  save_yaml(pkgs,"{}_all.yaml".format(list_file))
  # with any err
  pkgs_e = {}
 # ipdb.set_trace()
  for pkg in pkgs.keys():
    if 'err' in pkgs[pkg].values():
      pkgs_e[pkg] = pkgs[pkg]
  save_yaml(pkgs_e,"{}_with_any_err.yaml".format(list_file))
  # with err in priv_spec
  pkgs_priv_spec_e = {}
  for pkg in pkgs.keys():
    if 'err' in pkgs[pkg]['priv_spec']:
      pkgs_priv_spec_e[pkg] = pkgs[pkg]
  save_yaml(pkgs_priv_spec_e,"{}_with_priv_spec_err.yaml".format(list_file))
  # with err in priv_code
  pkgs_priv_code_e = {}
  for pkg in pkgs.keys():
    if 'err' in pkgs[pkg]['priv_code']:
      pkgs_priv_code_e[pkg] = pkgs[pkg]
  save_yaml(pkgs_priv_code_e,"{}_with_priv_code_err.yaml".format(list_file))
  #

if __name__ == '__main__':
  # HOVNOSCRIPT!
  """
  curl http://apt.mirantis.com.s3.amazonaws.com/xenial/openstack/pike/dists/nightly/main/binary-amd64/Packages.gz | zcat > nigtly
  curl http://apt.mirantis.com.s3.amazonaws.com/xenial/openstack/pike/dists/proposed/main/binary-amd64/Packages.gz | zcat > proposed
  curl http://apt.mirantis.com.s3.amazonaws.com/xenial/openstack/pike/dists/testing/main/binary-amd64/Packages.gz | zcat > testing
  """
  main()
