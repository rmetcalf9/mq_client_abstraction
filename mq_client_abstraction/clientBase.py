import time
import queue

class MqClientExceptionClass(Exception):
  pass

class MqClientProcessLoopTimeoutExceptionClass(MqClientExceptionClass):
  pass

class MqClientBaseClass():
  destinationPrefix = None
  subscriptions = None
  def __init__(self, configDict):
    self.configDict = configDict
    self.subscriptions = {}
    if "DestinationPrefix" in configDict:
      self.destinationPrefix = configDict["DestinationPrefix"]
    else:
      self.destinationPrefix = ""

    self.validateDestination(destination=self.destinationPrefix, msg="Invalid DestinationPrefix")

  def getType(self):
    return self.configDict["Type"]

  def validateDestination(self, destination, msg="Invalid Destination"):
    invalidChars = ['_', ':', '/', '\\', '$', '%']
    for c in invalidChars:
      if c in destination:
        raise MqClientExceptionClass(msg)

  def sendStringMessage(self, destination, body):
    self.validateDestination(destination=destination)
    self._sendStringMessage(destination=destination, body=body)

  def subscribeToDestination(self, destination, msgRecieveFunction):
    self.validateDestination(destination=destination)
    if destination in self.subscriptions:
      raise MqClientExceptionClass("Only supports single subscription per mq client")
    self.subscriptions[destination] = msgRecieveFunction

  def subscribeDestinationToPythonQueue(self, destination, queue):
    def msgRecieveFunction(destination, body):
      queue.put(body)
    self.subscribeToDestination(destination, msgRecieveFunction)

  # The process loop is for recievers that need to keep a loop running. It is not required for some types of
  #  client (Stomp) but is requried for others (Memory)
  # It can be used in two ways, "processLoop" will run and call an exit function on each iteration
  # "processLoopIteration" is for apps which already have a process loop and it will just do it's checks then terminate.
  def processLoop(
    self,
    exitFunction,
    timeoutInSeconds=None,
    sleepDurationInSeconds=0.1
  ):
    running = True
    def neverExitFunction():
      return False
    if exitFunction is None:
      exitFunction = neverExitFunction
    while running:
      if exitFunction():
        running = False
      else:
        self.processLoopIteration()
        time.sleep(sleepDurationInSeconds)
        if timeoutInSeconds is not None:
          timeoutInSeconds -= sleepDurationInSeconds
          if timeoutInSeconds < 0:
            raise MqClientProcessLoopTimeoutExceptionClass("Process loop timeout reached")

  def processLoopIteration(self):
    self._processLoopIteration()

  def close(self):
    self._close()

  # Functions called from derived class only
  def processMessageCALLEDFROMDERIVEDONLY(self, destination, body):
    if destination in self.subscriptions:
      self.subscriptions[destination](destination=destination, body=body)

  # Functions implemented by derived classes

  def _sendStringMessage(self, destination, body):
    raise Exception('_sendStringMessage Not Overridden')

  def _processLoopIteration(self):
    pass #overriden by inherited classes incase they have logic

  def _close(self):
    pass #overriden by inherited classes incase they have logic
