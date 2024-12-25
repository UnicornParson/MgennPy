#!/bin/bash
## src https://github.com/ml-tooling/lazydocs
python3 -m pip install -r requirements.txt
export MGENN_DEBUG="Y"
lazydocs --output-path=docs .