import mcore as mc
from common import *
from common import storage as mstorage
import os
import random
import socket
import inspect
import pandas as pd
from examples import *






example_core_life_cycle()
example_labels()
example_save_pkg()
example_analyzer_checkout()
stats_only()
#example_use_AR_top()

F.set_print_token("")

"""
TODO:
- [ ] Examples: make mnist classifier example.
   - [ ] downloaders
   - [ ] add snapshot labels 


"""

print("tester done!")
W.print_timeit_stats()