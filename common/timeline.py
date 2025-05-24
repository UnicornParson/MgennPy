if 'SHJYTHON' in globals() and globals()['SHJYTHON']:
    import matplotlib.pyplot as plt

class Timeline:
    def __init__(self) -> None:
        self.__data = {}

    def add(self, key, value):
        if not isinstance(value, (int, float, complex)) or isinstance(value, bool):
            raise ValueError("%s not a number %s" % (str(type(value)), str(value)))

        if key not in self.__data:
            if isinstance(value, list):
                self.__data[key] = value
            else:
                self.__data[key] = []
        if isinstance(value, list):
            self.__data[key].extend(value)
        else:
            self.__data[key].append(value)

    def __getitem__(self, key):
        if key not in self.__data:
            return None
        return self.__data[key].copy()

    def __contains__(self, key):
        return key in self.__data

    def plot(self, key):
        
        if key not in self.__data:
            raise KeyError("no key %s " % str(key))
        if 'SHJYTHON' in globals() and globals()['SHJYTHON']:
            # Jupyter env
            plt.plot(range(len(self.__data[key])),self.__data[key])
            plt.title("%s timeline" % str(key))
            plt.xlabel("I")
            plt.ylabel(key)
            plt.show()