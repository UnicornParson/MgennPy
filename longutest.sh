#!/bin/bash
set -e
source venv/bin/activate

export MGENN_DEBUG="Y"
export RUN_LONG_TESTS="Y"
python3 -m unittest discover -s tests -p 'test_*.py' 2>&1 | tee -i testrc.txt
deactivate
