import stomp

class StompConnectionListenerClass(stomp.ConnectionListener):
  recieveFunction = None

  def __init__(self, recieveFunction):
    self.recieveFunction = recieveFunction

  def on_error(self, headers, message):
    raise Exception("Error", message)
  def on_message(self, headers, message):
    self.recieveFunction(internalDestination=headers["destination"], body=message)
