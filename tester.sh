#!/bin/bash
echo "======================================================" >> tester.log
echo " Start " >> tester.log
date >> tester.log
echo "======================================================" >> tester.log
python3 tester.py 2>&1 | tee -a -i tester.log