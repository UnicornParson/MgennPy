#!/bin/bash
## src https://github.com/ml-tooling/lazydocs
python3 -m pip install -r requirements.txt
export MGENN_DEBUG="Y"
lazydocs --output-path=docs .
grep -rh --include="*.py" --exclude="test_*.py" --exclude="__pycache__" -E 'class|def ' | awk '{$1=$1};1' | awk '{if ($0  ~ /class /) print "# " $0; else print " + " $0}' > content.md