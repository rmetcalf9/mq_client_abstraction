from .connection import ConnectionClass
import threading

# Currently this will only support a single connection but may be extended in future to support mutiple
#  each connection maintains a list of messages it subscribes to. When a connection is disconnected it
#  will automatically re-establish if it is lisetning for messages, otherwise it will not and restablish
#  only reconect on next subscribe or sendmessage event

# When using a clientID then there can not be a connection pool so the current implementation of only one connection
#  in the pool is required

class ConnectionPoolClass():
  fullConnectionDetails = None # includes username and password
  recieveFunction = None # function to call when messages are recieved
  reconnectMaxRetries = None
  reconectInitialSecondsBetweenTries = None
  reconnectFadeoffFactor = None
  clientId = None

  connections = None

  poolLock = None

  def __init__(self, fullConnectionDetails, recieveFunction, skipConnectionCheck, reconnectMaxRetries, reconectInitialSecondsBetweenTries, reconnectFadeoffFactor, clientId):
    self.clientId = clientId
    self.poolLock = threading.Lock()
    self.fullConnectionDetails = fullConnectionDetails
    self.recieveFunction = recieveFunction
    self.reconnectMaxRetries = reconnectMaxRetries
    self.reconectInitialSecondsBetweenTries = reconectInitialSecondsBetweenTries
    self.reconnectFadeoffFactor = reconnectFadeoffFactor

    self.connections = []

    if not skipConnectionCheck:
      # Test connection on creation of pool
      #  and leave connection open
      testConnection = self.getConnection()


  def getConnection(self):
    if len(self.connections)==0:
      self.poolLock.acquire(blocking=True, timeout=-1)
      self.connections.append(
        ConnectionClass(
          self.fullConnectionDetails,
          recieveFunction=self.recieveFunction,
          reconnectMaxRetries=self.reconnectMaxRetries,
          reconectInitialSecondsBetweenTries=self.reconectInitialSecondsBetweenTries,
          reconnectFadeoffFactor=self.reconnectFadeoffFactor,
          clientId=self.clientId
        )
      )
      self.poolLock.release()
    return self.connections[0]

  def close(self, wait):
    self.poolLock.acquire(blocking=True, timeout=-1)
    for con in self.connections:
      con.close(wait=wait)
    self.connections = ()
    self.poolLock.release()

  def healthCheck(self):
    for con in self.connections:
      con.healthCheck()
