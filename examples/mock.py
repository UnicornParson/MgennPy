class MockInputSource:
    def __init__(self) -> None:
        self.headers = []
    def setHeaders(self, headers:list):
        self.headers = headers
    def getIRow(self, tick):
        raise NotImplementedError("implementation missed ")
    def ready(self):
        return True