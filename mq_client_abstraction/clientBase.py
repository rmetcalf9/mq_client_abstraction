

class MqClientExceptionClass(Exception):
  configDict = None

class MqClientBaseClass():
  destinationPrefix = None
  def __init__(self, configDict):
    self.configDict = configDict
    if "DestinationPrefix" in configDict:
      self.destinationPrefix = configDict["DestinationPrefix"]
    else:
      self.destinationPrefix = ""

    self.validateDestination(destination=self.destinationPrefix, msg="Invalid DestinationPrefix")

  def getType(self):
    return self.configDict["Type"]

  def validateDestination(self, destination, msg="Invalid Destination"):
    invalidChars = ['_', ':', '/', '\\', '$', '%']
    for c in invalidChars:
      if c in destination:
        raise MqClientExceptionClass(msg)
