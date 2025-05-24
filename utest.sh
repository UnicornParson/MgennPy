#!/bin/bash
set -e
mkdir -p trace
source venv/bin/activate

export MGENN_DEBUG="Y"
export TICKTRACE="Y"
python3 -m unittest discover -s tests -p 'test_*.py' 2>&1 | tee -i testrc.txt
deactivate
