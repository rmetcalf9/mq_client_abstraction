from .clientBase import MqClientExceptionClass

from .memory_client import mainClass as memoryMainClass
from .stomp_client import mainClass as stompMainClass

def createMQClientInstance(configDict):
  if configDict is None:
    configDict = {}
    configDict["Type"] = "Memory"

  if not isinstance(configDict, dict):
    raise MqClientExceptionClass('You must pass a dict as config to createObjectStoreInstance (or None)')

  if "Type" not in configDict:
    raise MqClientExceptionClass("Invalid mq client config - Type Missing")

  constructors = {}
  constructors["Memory"] = memoryMainClass
  constructors["Stomp"] = stompMainClass

  if configDict["Type"] not in constructors:
    print("Trying to create object store type " + configDict["Type"])
    raise MqClientExceptionClass("Invalid mq client config Type - " + configDict["Type"])

  return constructors[configDict["Type"]](configDict)


