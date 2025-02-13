class StorageDataError(Exception):
    def __init__(self, message=""):
        super().__init__(message)
        self.message = message
    def __str__(self):
        return f"DataError: {self.message}"

class StorageIntegrityError(Exception):
    def __init__(self, message=""):
        super().__init__(message)
        self.message = message
    def __str__(self):
        return f"IntegrityError: {self.message}"

