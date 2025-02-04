class StorageDataError(Exception):
    def __init__(self, message=""):
        super().__init__(self.message)
        self.message = message
    def __str__(self):
        return f"ConnectivityError: {self.message}"
