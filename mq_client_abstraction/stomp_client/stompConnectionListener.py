import stomp

class StompConnectionListenerClass(stomp.ConnectionListener):
  messageFunction = None
  disconnectedFunction = None
  errorFunction = None

  def __init__(self, messageFunction, disconnectedFunction, errorFunction):
    self.messageFunction = messageFunction
    self.disconnectedFunction = disconnectedFunction
    self.errorFunction = errorFunction

  def on_error(self, headers, message):
    self.errorFunction(headers=headers, message=message)
  def on_message(self, headers, message):
    self.messageFunction(headers=headers, message=message)
  def on_disconnected(self):
    self.disconnectedFunction()
