#!/usr/bin/python

import subprocess
import sys
import os
import yaml
import pprint as pprint
pp = pprint.PrettyPrinter()

'''
Simple EMC availability checks.
for run required:
1)enabled EMV part in /etc/astute.yaml file
Example:
{'emc_password': 'ericsson',
 'emc_pool_name': '',
 'emc_sp_a_ip': '192.168.200.31',
 'emc_sp_b_ip': '192.168.200.30',
 'emc_username': 'admin',}
2)naviseccli tool in system
3)iscsiadm
'''
##########
def which(program):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)
    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file
    return False

def cli_check():
    if os.path.exists('/opt/Navisphere/bin/naviseccli'):
        return '/opt/Navisphere/bin/naviseccli'
    elif which('naviseccli'):
       return which('naviseccli')
    else:
       return False

def emc_check(naviseccli,astute):
    def run_c(command):
        child = subprocess.Popen(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        child.wait()
        out,err = child.communicate()
        print '###Test command: \n%s\n%s' % (command, out)
        if err:
            print 'ERR:\n%s' % err
        print '#' * 30
        return out,err
    run_c(" ".join([naviseccli, '-Help']))
#
    run_c(" ".join([naviseccli, '-h', astute['storage']['emc_sp_a_ip'], '-user', \
    astute['storage']['emc_username'], '-password', \
    astute['storage']['emc_password'], '-scope 0 faults -list' ]))
#
    run_c(" ".join([naviseccli, '-h', astute['storage']['emc_sp_b_ip'], '-user', \
    astute['storage']['emc_username'], '-password', \
    astute['storage']['emc_password'], '-scope 0 faults -list' ]))
#
    run_c(" ".join([naviseccli, '-h', astute['storage']['emc_sp_a_ip'], '-user', \
    astute['storage']['emc_username'], '-password', \
    astute['storage']['emc_password'], '-scope 0 networkadmin -get -sp a' ]))
#
    run_c(" ".join([naviseccli, '-h', astute['storage']['emc_sp_b_ip'], '-user', \
    astute['storage']['emc_username'], '-password', \
    astute['storage']['emc_password'], '-scope 0 networkadmin -get -sp b' ]))
#
    read_ports_a = run_c(" ".join([naviseccli, '-h', astute['storage']['emc_sp_a_ip'], '-user', \
    astute['storage']['emc_username'], '-password', \
    astute['storage']['emc_password'], '-scope 0 connection -getport' ]))
#
    read_ports_b = run_c(" ".join([naviseccli, '-h', astute['storage']['emc_sp_b_ip'], '-user', \
    astute['storage']['emc_username'], '-password', \
    astute['storage']['emc_password'], '-scope 0 connection -getport' ]))
#
    ips = []
    for i in read_ports_a[0].split('\n'):
       s = i.split(':')
       if s[0] == 'IP Address':
           ips.append(s[1].strip())

    for i in read_ports_b[0].split('\n'):
       s = i.split(':')
       if s[0] == 'IP Address':
           ips.append(s[1].strip())

    mp_ips = list(set(ips))
    print '#' * 50
    print '###We found %s iscsi points:\n ' % len(mp_ips), "\n###Lets try ping them:\n"
    for point in mp_ips:
        run_c(" ".join(['ping -c 5', point]))
    print '#' * 50
#
    print '###We found %s iscsi points:\n ' % len(mp_ips), "\n###Lets try discover them:\n"
    for point in mp_ips:
        run_c(" ".join(['iscsiadm -m discovery -t st -p', point]))
    print '#' * 50
    sys.exit(0)


def main():
    astute_file = "astute.yaml"

    if os.path.exists(astute_file):
       print "Astute file found in ", astute_file
       astute = yaml.load(open(astute_file, 'r'))
    else:
       print "Astute file not found.Abort EMC check.."
       sys.exit(0)

    if astute['storage']['volumes_emc'] == True:
        print  "Looks like emc enabled, and have storage config:\n",pp.pprint(astute['storage'])
        if  (cli_check):
            emc_check(cli_check(),astute)
        elif (cli_check):
            print "naviseccli tools not found.Abort EMC check.."
            sys.exit(0)

if __name__ == '__main__':
   main()
