#!/bin/bash
set -e
# should be installed by apt
# apt install python3.10-venv
# python3 -m pip install virtualenv
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
export MGENN_DEBUG="Y"
python3 -m unittest discover -s tests -p 'test_*.py' 2>&1 | tee -i testrc.txt
deactivate
