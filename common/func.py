import statistics
import torch
import datetime
import humanize
import jsonpickle
from pympler.asizeof import asizeof
import numpy as np

def hit(output, labels):
    if output.shape != labels.shape:
        raise ValueError(f"shapes missmatch {output.shape} != {labels.shape}")
    return int(torch.argmax(output, dim=1)) == int(torch.argmax(labels, dim=1))

def hit_int(output, labels):
    return 1 if hit(output, labels) else 0

def tensor_to_float(t):
    npv = t.detach().numpy()
    if npv.shape == () and npv.size == 1:
            return float(npv)
    raise ValueError(" not a single-float type %s" % str(t))

def trace(msg):
    with open("torch01.log", "a") as log:
            log.write("%s: %s\n" % (str(datetime.datetime.now()), str(msg)))


def sizeof_str(o):
    b = asizeof(o)
    return f"{humanize.naturalsize(b)} ({b}b)"

def np_array_stat(arr)->str:
    return f"arr({arr.dtype}) [{np.min(arr)} -> {np.mean(arr)} -> {np.max(arr)}"

def approximate(lower_bound, upper_bound, n, keep_bounds = True):
    assert n > 0
    l = []
    if keep_bounds:
        l.append(lower_bound)
    step = (upper_bound - lower_bound) / (n + 1)
    l.extend([lower_bound + i * step for i in range(1, n + 1)])
    if keep_bounds:
        l.append(upper_bound)
    return l

def i_approximate(lower_bound, upper_bound, n, keep_bounds = True):
    l = approximate(lower_bound, upper_bound, n, keep_bounds)
    return [ int(x) for x in l ]