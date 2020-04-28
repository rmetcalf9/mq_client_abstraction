from .connection import ConnectionClass

# Currently this will only support a single connection but may be extended in future to support mutiple
#  each connection maintains a list of messages it subscribes to. When a connection is disconnected it
#  will automatically re-establish if it is lisetning for messages, otherwise it will not and restablish
#  only reconect on next subscribe or sendmessage event

class ConnectionPoolClass():
  fullConnectionDetails = None # includes username and password
  recieveFunction = None # function to call when messages are recieved

  connections = None

  def __init__(self, fullConnectionDetails, recieveFunction, skipConnectionCheck):
    self.fullConnectionDetails = fullConnectionDetails
    self.recieveFunction = recieveFunction

    if not skipConnectionCheck:
      # Test connection on creation of pool
      testConnection = ConnectionClass(self.fullConnectionDetails, recieveFunction=self.recieveFunction)
      testConnection.close(wait=True)

    self.connections = []

  def getConnection(self):
    if len(self.connections)==0:
      self.connections.append(ConnectionClass(self.fullConnectionDetails, recieveFunction=self.recieveFunction))
    return self.connections[0]

  def close(self, wait):
    for con in self.connections:
      con.close(wait=wait)
    self.connections = ()