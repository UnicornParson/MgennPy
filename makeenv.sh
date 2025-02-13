#!/bin/bash
set -e
# should be installed by apt
# apt install python3.10-venv
# python3 -m pip install virtualenv
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
deactivate