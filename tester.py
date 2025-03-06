import mcore as mc
from common import *
from common import storage as mstorage
import os
import socket
import inspect
import pandas as pd

def make_in_df():
    return pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})

@W.timeit
def push_new_exec_done(storage):
    pkg = mc.Package()
    pkg.loadFile(f"{os.getcwd()}/tests/test_data/namespacetest_rev0.pkg")
    cid = pkg.renew_id()
    sid = pkg.id()
    storage.erase_snapshot(sid)
    storage.on_exec_done(pkg, 33, make_in_df())
    return cid, pkg

@W.timeit
def push_new_exec_ready(storage):
    pkg = mc.Package()
    pkg.loadFile(f"{os.getcwd()}/tests/test_data/namespacetest_rev0.pkg")
    cid = pkg.renew_id()
    sid = pkg.id()
    storage.erase_snapshot(sid)
    storage.on_ready_for_exec(pkg, 33)
    return cid, pkg

@W.timeit
def example_save_pkg():
    F.set_print_token(inspect.currentframe().f_code.co_name)
    db_conf = mstorage.PG_Pool.db_conf_from_env()
    pool = mstorage.PG_Pool(db_conf)
    storage = mstorage.MgennStorage(pool)
    storage.pedantic_validation = True
    storage.init()
    pkg_path = f"{os.getcwd()}/tests/test_data/namespacetest_rev0.pkg"
    pkg = mc.Package()
    pkg.loadFile(pkg_path)
    df = make_in_df()
    sid = pkg.id()
    storage.erase_snapshot(sid)
    storage.on_exec_done(pkg, 33, df)
    F.set_print_token("")

@W.timeit
def example_analyzer_checkout():
    F.set_print_token(inspect.currentframe().f_code.co_name)
    db_conf = mstorage.PG_Pool.db_conf_from_env()
    pool = mstorage.PG_Pool(db_conf)
    storage = mstorage.MgennStorage(pool)
    storage.pedantic_validation = True
    storage.init()

    # make new unic snapshot and save
    pkg = PackageUtils.makeRandomContent(mc.Package.make_empty(), PkgSizePreset.Small)
    df = make_in_df()
    sid = pkg.id()
    storage.erase_snapshot(sid)
    storage.on_exec_done(pkg, 33, df)

    # checkout it
    print(f"db stats (before_co) {storage.stats()}")
    job, pkg = storage.checkout_analizer_job(sid)
    if not job or not isinstance(job, mstorage.AnalizerJob) or not job.isValid():
        raise ValueError("no job!")
    if not pkg or not pkg.isValid():
        raise ValueError("no pkg!")
    pkg.pretty_print()
    print(f"#1 has a job! {job}. sid in {storage.find_snapshot(job.snapshot_id).value}")
    print(f"#2 has a pkg! sz:{len(pkg)}")
    print(f"db stats (after co){storage.stats()}")
    storage.undo_analyzer_checkout(job.snapshot_id)
    print(f"#3 undo ok sid in {storage.find_snapshot(job.snapshot_id).value}")
    print(f"db stats {storage.stats()}")
    F.set_print_token("")

@W.timeit
def stats_only():
    F.set_print_token(inspect.currentframe().f_code.co_name)
    db_conf = mstorage.PG_Pool.db_conf_from_env()
    pool = mstorage.PG_Pool(db_conf)
    storage = mstorage.MgennStorage(pool)
    storage.pedantic_validation = True
    storage.init()
    print(f"stats: {storage.stats()}")
    F.set_print_token("")

class MockInputSource:
    def __init__(self) -> None:
        self.headers = []
    def setHeaders(self, headers:list):
        self.headers = headers
    def getIRow(self, tick):
        raise NotImplementedError("implementation missed ")
    def ready(self):
        return True


@W.timeit
def fill_ar(storage):
    
    # Создание нового пакета
    pkg = Package.make_empty()
    
    # Создание экземпляра mc.StructsBuilder
    struct_builder = mc.StructsBuilder()
    
    try:
        # Проверка валидности пакета
        if not pkg.isValid():
            raise ValueError("invalid pkg")
        
        def neuron_builder(l_index):
            leak = 0.1
            peak = 5.
            return (leak, peak)
        def link_builder(from_id, to_id):
            apt = 1.
            length = 1
            return (apt, length)

        # Создание первого слоя из 3 нейронов
        layer1_name, layer1_ids, pkg = struct_builder.make_layer(
            pkg,
            size=3,
            config_builder=neuron_builder
        )
        
        # Создание второго слоя из 3 нейронов
        layer2_name, layer2_ids, pkg = struct_builder.make_layer(pkg, size=3,
            config_builder=neuron_builder
        )
        
        # Соединение двух слоев 1-к-1
        links, pkg = struct_builder.connect_layers_1_1(
            pkg,
            l=layer1_ids,
            r=layer2_ids,
            link_builder=link_builder
        )
        
        # Создание сетки 2x2 нейронов
        grid_shape = (2, 2)
        grid_layer_name, grid_inexes, pkg = struct_builder.make_ngrid(
            pkg,
            shape=grid_shape,
            config_builder=neuron_builder
        )
        
        # Добавление информации о структурах в пакет
        structure_hints = {
            layer1_name: layer1_ids,
            layer2_name: layer2_ids,
            grid_layer_name: grid_inexes
        }
        pkg.addStructureHints(structure_hints)
        
        # Проверка успешности операций
        if not pkg.isValid():
            raise ValueError("package building error")
        
        # Сохранение пакета в хранилище
        storage.on_exec_done(pkg, rank=1, outputs=make_in_df(), label="TEST_GRP", telemetry = {}, ex = {})
        
    except ValueError as ve:
        F.print(f"ValueError: {ve}")
        raise
    except Exception as e:
        F.print(f"unknown error: {e}")
        raise
    
    # Возврат идентификатора пакета
    return pkg.id()

@W.timeit
def example_core_life_cycle():
    F.set_print_token(inspect.currentframe().f_code.co_name)
    db_conf = mstorage.PG_Pool.db_conf_from_env()
    pool = mstorage.PG_Pool(db_conf)
    storage = mstorage.MgennStorage(pool)
    storage.pedantic_validation = True
    storage.init()
    fill_ar(storage)
    cycle = mc.CoreLifeCycle()
    cycle.i_source = MockInputSource()
    cid, o_pkg = push_new_exec_ready(storage)
    job, pkg = storage.checkout_executor_job(cid)
    if not job or not isinstance(job, mstorage.ExecutorJob) or not job.isValid():
        raise ValueError("no exec job!")
    if not pkg or not pkg.isValid():
        raise ValueError("no pkg!")
    storage.undo_exec_checkout(cid)
    F.set_print_token("")


@W.timeit
def example_use_top():
    F.set_print_token(inspect.currentframe().f_code.co_name)
    F.print("init storage")
    db_conf = mstorage.PG_Pool.db_conf_from_env()
    pool = mstorage.PG_Pool(db_conf)
    storage = mstorage.MgennStorage(pool)
    storage.pedantic_validation = True
    storage.init()
    F.print("init storage - OK")

    F.table_print(storage.top_ar(10), ["snapshot_id", "rank"], title="TOP AR")
    F.table_print(storage.top_er(10), ["snapshot_id", "rank"], title="TOP ER")
    job, pkg = storage.checkout_some_AR()
    F.set_print_token("")
    if not job or not isinstance(job, mstorage.ExecutorJob) or not job.isValid():
        raise ValueError("no exec job!")
    if not pkg or not pkg.isValid():
        raise ValueError("no pkg!")
    F.print("found some job {job} with")
    F.set_print_token("")


example_core_life_cycle()

example_save_pkg()
example_analyzer_checkout()
stats_only()
#example_use_top()

F.set_print_token("")

"""
TODO:
- [ ] Examples: make mnist classifier example.
   - [ ] downloaders
   - [ ] add snapshot labels 


"""

print("tester done!")