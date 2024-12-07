#!/bin/bash
export MGENN_DEBUG="Y"
python3 -m unittest discover -s tests -p 'test_*.py'