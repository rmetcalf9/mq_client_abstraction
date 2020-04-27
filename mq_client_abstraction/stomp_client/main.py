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
  def __init__(self, configDict):
    super(mainClass, self).__init__(configDict=configDict)

    requiredInDict = ["Username", "Password", "ConnectionString"]
    for x in requiredInDict:
      if x not in configDict:
        raise MqClientExceptionClass("Invalid mq client config - Missing " + x)

    self.connectionPool = ConnectionPoolClass({
      "FormattedConnectionDetails": getFormattedConnectionDetails(configDict["ConnectionString"]),
      "Username": configDict["Username"],
      "Password": configDict["Password"]
    })

  def _sendStringMessage(self, internalDestination, body):
    self.connectionPool.getConnection().sendStringMessage(internalDestination=internalDestination, body=body)
