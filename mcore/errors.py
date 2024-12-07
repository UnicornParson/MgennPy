class DirtyObjectException(Exception):
    def __init__(self, who:str, oid, message="object is dirty"):
        super().__init__(self.message)
        self.oid = oid
        self.message = message
        self.who = who
    def __str__(self):
        return f"object {self.who}[{self.oid}]: {self.message}"

class NoDataException(ValueError):
    def __init__(self, who:str,  message="object is dirty"):
        super().__init__(self.message)
        self.message = message
        self.who = who
    def __str__(self):
        return f"no data in {self.who}. {self.message}"

class ConnectivityError(Exception):
    def __init__(self, message=""):
        super().__init__(self.message)
        self.message = message
    def __str__(self):
        return f"ConnectivityError: {self.message}"

class BrokenObject(Exception):
    def __init__(self, message=""):
        super().__init__(self.message)
        self.message = message
    def __str__(self):
        return f"BrokenData: {self.message}"