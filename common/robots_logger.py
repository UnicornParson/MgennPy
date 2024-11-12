
import time
import json

class RobotsLogger():
    default = None


    def __init__(self) -> None:
        self.log = []

    def onEvent(self, msg:str, args:dict, src:str):
        msg = {
            "t":float(time.time()),
            "e": msg,
            "src": src,
            'args':args
        }
        self.log.append(msg)

    def __str__(self):
        msg = ""
        for m in self.log:
            msg += f"{json.dumps(m)}\n"
        return msg