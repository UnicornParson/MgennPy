import pandas as pd
import random
from common import *
from common import storage as mstorage
import mcore as mc

def make_in_df():
    return pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})


@W.timeit
def cleanup(sids_to_remove, storage):
    for sid in sids_to_remove:
        storage.erase_snapshot(sid)


@W.timeit
def fill_ar(storage, count = 10, randomize_labels = True):
    def neuron_builder(l_index):
        leak = random.uniform(0.1, 1.1)
        peak = random.uniform(5.0, 10.0)
        return (leak, peak)
    def link_builder(from_id, to_id):
        apt = random.uniform(0.2, 1.1)
        length = 1
        return (apt, length)
    
    
    struct_builder = mc.StructsBuilder()
    
    sids = []
    labels = []
    default_label="TEST_GRP"
    try:
        for _ in range(count):
            pkg = Package.make_empty()
            if not pkg.isValid():
                raise ValueError("invalid pkg")
            layer1_name, layer1_ids, pkg = struct_builder.make_layer(
                pkg,
                size=3,
                config_builder=neuron_builder
            )
            
            # Creating the second layer with 3 neurons
            layer2_name, layer2_ids, pkg = struct_builder.make_layer(pkg, size=3,
                config_builder=neuron_builder
            )
            
            # Connecting two layers 1-to-1
            _, pkg = struct_builder.connect_layers_1_1(
                pkg,
                l=layer1_ids,
                r=layer2_ids,
                link_builder=link_builder
            )
            
            # Creating a grid of 2x2 neurons
            grid_shape = (2, 2)
            grid_layer_name, grid_inexes, pkg = struct_builder.make_ngrid(
                pkg,
                shape=grid_shape,
                config_builder=neuron_builder
            )
            
            # Adding structure information to the package
            structure_hints = {
                layer1_name: layer1_ids,
                layer2_name: layer2_ids,
                grid_layer_name: grid_inexes
            }
            pkg.addStructureHints(structure_hints)
            
            # Checking operation success
            if not pkg.isValid():
                raise ValueError("package building error")
            
            # Saving the package to storage
            label = default_label
            if randomize_labels:
                label=f"GROUP_{F.generateToken()}"
            labels.append(label)
            sids.append(pkg.id())
            storage.on_exec_done(pkg, rank=1, outputs=make_in_df(), label=label, telemetry = {}, ex = {})
        
    except ValueError as ve:
        F.print(f"ValueError: {ve}")
        raise ve
    except Exception as e:
        F.print(f"unknown error: {e}")
        raise e
    
    return sids, labels
