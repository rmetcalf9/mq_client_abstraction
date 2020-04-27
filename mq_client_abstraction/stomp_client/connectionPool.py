from .connection import ConnectionClass

# Currently this will only support a single connection but may be extended in future to support mutiple
#  each connection maintains a list of messages it subscribes to. When a connection is disconnected it
#  will automatically re-establish if it is lisetning for messages, otherwise it will not and restablish
#  only reconect on next subscribe or sendmessage event

class ConnectionPoolClass():
  fullConnectionDetails = None # includes username and password

  connections = None

  def __init__(self, fullConnectionDetails):
    self.fullConnectionDetails = fullConnectionDetails

    self.connections = []

  def getConnection(self):
    if len(self.connections)==0:
      self.connections.append(ConnectionClass(self.fullConnectionDetails))
    return self.connections[0]