#!/bin/bash
set -e

source venv/bin/activate
export MGENN_DEBUG="Y"
pip3 install -r examples_requirements.txt
echo "======================================================" >> tester.log
echo " Start " >> tester.log
date >> tester.log
echo "======================================================" >> tester.log
python3 tester.py 2>&1 | tee -a -i tester.log
deactivate
