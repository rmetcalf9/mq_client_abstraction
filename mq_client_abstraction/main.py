from .clientBase import MqClientExceptionClass

def createObjectStoreInstance(configDict):
  if configDict is None:
    configDict = {}
    configDict["Type"] = "Memory"

  if not isinstance(configDict, dict):
    raise MqClientExceptionClass('You must pass a dict as config to createObjectStoreInstance (or None)')

  if "Type" not in configDict:
    raise MqClientExceptionClass("Invalid object store config - Type Missing")
  if configDict["Type"] == "Memory":
    raise MqClientExceptionClass("Not Implemented")
    ##return createFN("Memory", objectStoreConfigDict, ObjectStore_Memory, externalFns, detailLogging)

  print("Trying to create object store type " + configDict["Type"])
  raise MqClientExceptionClass("Invalid object store config Type - " + configDict["Type"])
