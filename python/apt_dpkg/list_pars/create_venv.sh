#!/usr/bin/env bash

set -ex
if [[ ! -d venv ]];then
  virtualenv venv
  source venv/bin/activate
  pip install -U PyYaml gspread oauth2client PyOpenSSL

else
  echo "venv already exist"
fi
