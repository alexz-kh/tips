#!/usr/bin/python
# -*- coding: utf-8 -*-
import subprocess,sys
import pprint as pprint
import json

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
  with open('list.txt', 'r') as f:
    x = f.readlines()
  return x


def main():
  pkgs = {}
  z1 = ''.join(read_file())
  l1 = read_file()
  import ipdb
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
              #ipdb.set_trace()
              priv_code = l1[p].split('Private-Mcp-Code-Sha:')[1].replace(' ','').replace('\n','')
            if l1[p].startswith('Private-Mcp-Spec-Sha:'):
              priv_spec = l1[p].split('Private-Mcp-Spec-Sha:')[1].replace(' ','').replace('\n','')
            if l1[p].startswith('Source:'):
              #ipdb.set_trace()
              source = l1[p].split('Source:')[1].replace(' ','').replace('\n','')
        #name = source
        if pkgs.get(name):
          #ipdb.set_trace()
          if pkgs[name]['priv_spec'] != priv_spec or pkgs[name]['priv_code'] != priv_code:
            print('ERR:\n' + name)
            print('Replace {} => {}\n{} => {}'.format(pkgs[name]['priv_spec'],priv_spec,pkgs[name]['priv_code'],priv_code) )
        pkgs[name] = { 'priv_spec': priv_spec, 'priv_code': priv_code} #, 'source' : source }
      except:
        print("ERR")
        sys.exit(1)
        pass

  ppr = pprint.PrettyPrinter(indent=3)
  print("===All====")
  ppr.pprint(pkgs)
  pkgs_e = {}
  for pkg in pkgs.keys():
    if 'err' in pkgs[pkg].values():
      pkgs_e[pkg] = pkgs[pkg]
  print("===With err====")
  ppr.pprint(pkgs_e)

if __name__ == '__main__':
  # HOVNOSCRIPT!
   # curl http://apt.mirantis.com.s3.amazonaws.com/xenial/openstack/pike/dists/nightly/main/binary-amd64/Packages.gz | zcat > list
 main()
