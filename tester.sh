#!/bin/bash
set -e
# should be installed by apt
# apt install python3.10-venv
# python3 -m pip install virtualenv
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
export MGENN_DEBUG="Y"
echo "======================================================" >> tester.log
echo " Start " >> tester.log
date >> tester.log
echo "======================================================" >> tester.log
python3 tester.py 2>&1 | tee -a -i tester.log
deactivate
