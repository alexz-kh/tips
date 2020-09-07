#!/bin/env python3

import re
import os,sys
from datetime import datetime
import logging as LOG
import yaml

LOG.basicConfig(level=LOG.DEBUG, datefmt='%Y-%m-%d %H:%M:%S',
                format='%(asctime)-15s - [%(levelname)s] %(module)s:%(lineno)d: '
                       '%(message)s', )

def read_file(text_file):
    if not os.path.isfile(text_file):
        LOG.error("File not exist:{}".format(text_file))
        sys.exit(1)
    with open(text_file, 'r') as f:
        x = f.readlines()
    return x

def save_yaml(save_yaml, to_file):
    if not os.path.exists(os.path.dirname(to_file)):
        try:
            os.makedirs(os.path.dirname(to_file))
        except OSError as exc:
            LOG.error("Unable create:{}".format(to_file))
            sys.exit(1)
    with open(to_file, 'w') as f:
        f.write(
            yaml.dump(save_yaml, default_flow_style=False, width=float("inf")))
        LOG.info("{} file saved".format(to_file))

fread = 'tests.log'
if __name__ == '__main__':
    zz = read_file(fread)
    obj = {}
    cnt = 0
    i_s = False
    for line in range(1, len(zz)):
        start = re.match(r'(.*--\ K8S\ API\ Creating.*:\n)', zz[line], re.I | re.M )
        end = re.match(r'(^2020.*DEBUG.*\n)', zz[line], re.I | re.M )
        if start and not i_s:
            cnt+=1
            i_s = line+1
#            print(f"start: {zz[line]}")
        elif end and i_s:
#            print(f"end: {zz[line]}")
            obj[cnt] = zz[i_s:line]
            i_s = False
            k8sobj = yaml.load("".join(obj[cnt]))
            fkind = k8sobj['kind']
            fns = k8sobj['metadata'].get('namespace', 'default')
            fname = k8sobj['metadata'].get('name', k8sobj['metadata'].get('generateName', datetime.now().strftime("%H_%M_%S.%f") ))
            LOG.info(f'process:{fns}/{fkind}/fname')
            save_yaml(k8sobj, f'./{fns}_{fkind}_{fname}.yaml')

