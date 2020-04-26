

class MqClientExceptionClass(Exception):
  configDict = None

class MqClientBaseClass():
  def __init__(self, configDict):
    self.configDict = configDict

  def getType(self):
    return self.configDict["Type"]
