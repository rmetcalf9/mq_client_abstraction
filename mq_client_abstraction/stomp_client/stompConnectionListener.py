import stomp

class StompConnectionListenerClass(stomp.ConnectionListener):
  recieveFunction = None
  disconnectedFunction = None

  def __init__(self, recieveFunction, disconnectedFunction):
    self.recieveFunction = recieveFunction
    self.disconnectedFunction = disconnectedFunction

  def on_error(self, headers, message):
    raise Exception("Error", message)
  def on_message(self, headers, message):
    self.recieveFunction(internalDestination=headers["destination"], body=message)
  def on_disconnected(self):
      self.disconnectedFunction()
