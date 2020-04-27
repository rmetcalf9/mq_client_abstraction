import stomp

class StompConnectionListenerClass(stomp.ConnectionListener):
  recieveFunction = None
  disconnectedFunciton = None

  def __init__(self, recieveFunction, disconnectedFunciton):
    self.recieveFunction = recieveFunction
    self.onDisconnectedFunciton = disconnectedFunciton

  def on_error(self, headers, message):
    raise Exception("Error", message)
  def on_message(self, headers, message):
    self.recieveFunction(internalDestination=headers["destination"], body=message)
  def on_disconnected(self):
      self.disconnectedFunciton()
