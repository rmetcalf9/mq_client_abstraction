from .connection import ConnectionClass

# Currently this will only support a single connection but may be extended in future to support mutiple
#  each connection maintains a list of messages it subscribes to. When a connection is disconnected it
#  will automatically re-establish if it is lisetning for messages, otherwise it will not and restablish
#  only reconect on next subscribe or sendmessage event

class ConnectionPoolClass():
  fullConnectionDetails = None # includes username and password
  recieveFunction = None # function to call when messages are recieved
  reconnectMaxRetries = None
  reconectInitialSecondsBetweenTries = None
  reconnectFadeoffFactor = None

  connections = None

  def __init__(self, fullConnectionDetails, recieveFunction, skipConnectionCheck, reconnectMaxRetries, reconectInitialSecondsBetweenTries, reconnectFadeoffFactor):
    self.fullConnectionDetails = fullConnectionDetails
    self.recieveFunction = recieveFunction
    self.reconnectMaxRetries = reconnectMaxRetries
    self.reconectInitialSecondsBetweenTries = reconectInitialSecondsBetweenTries
    self.reconnectFadeoffFactor = reconnectFadeoffFactor

    if not skipConnectionCheck:
      # Test connection on creation of pool
      testConnection = ConnectionClass(
        self.fullConnectionDetails,
        recieveFunction=self.recieveFunction,
        reconnectMaxRetries=self.reconnectMaxRetries,
        reconectInitialSecondsBetweenTries=self.reconectInitialSecondsBetweenTries,
        reconnectFadeoffFactor=self.reconnectFadeoffFactor
      )
      testConnection.close(wait=True)

    self.connections = []

  def getConnection(self):
    if len(self.connections)==0:
      self.connections.append(
        ConnectionClass(
          self.fullConnectionDetails,
          recieveFunction=self.recieveFunction,
          reconnectMaxRetries=self.reconnectMaxRetries,
          reconectInitialSecondsBetweenTries=self.reconectInitialSecondsBetweenTries,
          reconnectFadeoffFactor=self.reconnectFadeoffFactor
        )
      )
    return self.connections[0]

  def close(self, wait):
    for con in self.connections:
      con.close(wait=wait)
    self.connections = ()

  def healthCheck(self):
    for con in self.connections:
      con.healthCheck()
