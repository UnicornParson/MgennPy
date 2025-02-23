class StorageDataError(Exception):
    def __init__(self, message=""):
        super().__init__(message)
        self.message = message
    def __str__(self):
        return f"DataError: {self.message}"

class StorageNoDataError(Exception):
    def __init__(self, message=""):
        super().__init__(message)
        self.message = message
    def __str__(self):
        return f"No Data: {self.message}"

class StorageIntegrityError(Exception):
    def __init__(self, message=""):
        super().__init__(message)
        self.message = message
    def __str__(self):
        return f"IntegrityError: {self.message}"

class StorageKeyNotFoundError(Exception):
    def __init__(self, key, where):
        super().__init__(f"key {key} not found in storage.{where}")
        self.key = key
        self.where = where
    def __str__(self):
        return f"key {self.key} not found in storage.{self.where}"

class StorageConcurrencyError(Exception):
    def __init__(self, message=""):
        super().__init__(message)
        self.message = message
    def __str__(self):
        return f"ConcurrencyError: {self.message}"
