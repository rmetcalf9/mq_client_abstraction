from ..clientBase import MqClientBaseClass, MqClientExceptionClass
from .connectionPool import ConnectionPoolClass

def getFormattedConnectionDetails(connectionString):
  firstSplit = connectionString.split("://")
  if len(firstSplit) != 2:
    raise MqClientExceptionClass("Invalid mq client config - Invalid ConnectionString")
  acceptedProtocols = ["stomp", "stomp+ssl"]
  if firstSplit[0] not in acceptedProtocols:
    raise MqClientExceptionClass("Invalid mq client config - Invalid ConnectionString (Bad Protocol)")

  secondSplit = firstSplit[1].split(":")
  if len(secondSplit) != 2:
    raise MqClientExceptionClass("Invalid mq client config - Invalid ConnectionString (Missing Port)")

  port = -1
  try:
    port = int(secondSplit[1])
  except ValueError:
    raise MqClientExceptionClass("Invalid mq client config - Invalid ConnectionString (Port must be a number)")
  if port < 0:
    raise MqClientExceptionClass("Invalid mq client config - Invalid ConnectionString (Port not in range 0-65535)")
  if port > 65535:
    raise MqClientExceptionClass("Invalid mq client config - Invalid ConnectionString (Port not in range 0-65535)")

  return {
    "Protocol": firstSplit[0],
    "Url": secondSplit[0],
    "Port": port
  }


class mainClass(MqClientBaseClass):
  connectionPool = None
  skipConnectionCheck = None
  clientId = None
  def __init__(self, configDict):
    super(mainClass, self).__init__(configDict=configDict)

    self.skipConnectionCheck = False
    if "skipConnectionCheck" in configDict:
      if configDict["skipConnectionCheck"] == True:
        self.skipConnectionCheck = True

    reconnectMaxRetries = 9
    if "reconnectMaxRetries" in configDict:
      reconnectMaxRetries = configDict["reconnectMaxRetries"]
    reconectInitialSecondsBetweenTries = 2
    if "reconectInitialSecondsBetweenTries" in configDict:
      reconectInitialSecondsBetweenTries = configDict["reconectInitialSecondsBetweenTries"]
    reconnectFadeoffFactor = 1.5
    if "reconnectFadeoffFactor" in configDict:
      reconnectFadeoffFactor = configDict["reconnectFadeoffFactor"]

    if "clientId" in configDict:
      self.clientId = configDict["clientId"]
      print("STOMP using client ID " + self.clientId)

    requiredInDict = ["Username", "Password", "ConnectionString"]
    for x in requiredInDict:
      if x not in configDict:
        raise MqClientExceptionClass("Invalid mq client config - Missing " + x)

    self.connectionPool = ConnectionPoolClass(
      fullConnectionDetails= {
        "FormattedConnectionDetails": getFormattedConnectionDetails(configDict["ConnectionString"]),
        "Username": configDict["Username"],
        "Password": configDict["Password"],
      },
      recieveFunction=self.processMessageCALLEDFROMDERIVEDONLY,
      skipConnectionCheck=self.skipConnectionCheck,
      reconnectMaxRetries=reconnectMaxRetries,
      reconectInitialSecondsBetweenTries=reconectInitialSecondsBetweenTries,
      reconnectFadeoffFactor=reconnectFadeoffFactor,
      clientId=self.clientId
    )

  def _sendStringMessage(self, internalDestination, body):
    self.connectionPool.getConnection().sendStringMessage(internalDestination=internalDestination, body=body)

  def _registerSubscription(self, internalDestination, prefetchSize, durableSubscriptionName):
    self.connectionPool.getConnection().registerSubscription(
      internalDestination=internalDestination,
      prefetchSize=prefetchSize,
      durableSubscriptionName=durableSubscriptionName
    )

  def _close(self, wait):
    self.connectionPool.close(wait=wait)

  def _healthCheck(self):
    self.connectionPool.healthCheck()
