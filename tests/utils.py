import os

class TestUtils:
    @staticmethod
    def run_long_tests() -> bool:
        rlt_var = "RUN_LONG_TESTS"
        if rlt_var not in os.environ:
            return False
        e_debug = os.environ[rlt_var]
        if e_debug != 1 and e_debug != "Y":
            return False
        return True