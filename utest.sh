#!/bin/bash

python3 -m pip install -r requirements.txt
export MGENN_DEBUG="Y"
python3 -m unittest discover -s tests -p 'test_*.py'