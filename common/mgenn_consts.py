from enum import Enum

class MgennConsts:
	NULL_NAME = "NULL"
	NULL_ID = 0
	User_Agent = "MgennPy_0.1"
	Calc_accuracy = 4

class ObjectIdType(Enum):
	Unknown = 'U'
	Link = 'L'
	Timer = 'T'
	Event = 'E'
	Core = 'C'
	Branch = 'B'
	Other = 'O'
	File = 'F'
	Neuron = 'N'