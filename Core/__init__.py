class CoreObject:
    def deserialize(data):
		raise NotImplementedError("implementation missed ")

	def serialize(data):
		raise NotImplementedError("implementation missed ")

class Neuron(CoreObject):
	def __init__(self):
        super().__init__()
		self.localId = MgennConsts.NULL_ID;
		self.currentEnergy = 0.0
		self.energyLeak = 0.0
		self.peakEnergy = 0.0
		self.mode = ""
		self.receivers = 0

	def deserialize(data):
		raise NotImplementedError("implementation missed ")

	def serialize(data):
		raise NotImplementedError("implementation missed ")