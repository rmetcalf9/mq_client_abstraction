import time
import queue
import threading

class MqClientExceptionClass(Exception):
  pass

class MqClientProcessLoopTimeoutExceptionClass(MqClientExceptionClass):
  pass

class RecieveThread(threading.Thread):
  running = None
  sleepTime = None
  stopped = None
  loopIterationFunction = None
  def __init__(self, sleepTime, loopIterationFunction):
    self.running = True
    self.sleepTime = sleepTime
    self.stopped = False
    self.loopIterationFunction = loopIterationFunction

    super(RecieveThread, self).__init__()

  def run(self):
    self.running = True
    print('MQ Client recieve thread starting')
    while self.running:
      self.loopIterationFunction()
      time.sleep(self.sleepTime)
    print('MQ Client recieve thread terminating')
    self.stopped = True


  def close(self, wait):
    if self.stopped:
      raise MqClientExceptionClass("Closing thread twice")
    self.stopped = False
    self.running = False
    if wait:
      while self.stopped == False:
        time.sleep(self.sleepTime)

class MqClientBaseClass():
  destinationPrefix = None
  subscriptions = None
  recieveThread = None
  def __init__(self, configDict):
    self.configDict = configDict
    self.subscriptions = {} # key is internalDestination
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
    internalDestination = self._mapToInternalDestination(destination)
    self.validateDestination(destination=internalDestination)
    self._sendStringMessage(internalDestination=internalDestination, body=body)

  def subscribeToDestination(self, destination, msgRecieveFunction):
    internalDestination = self._mapToInternalDestination(destination)
    self.validateDestination(destination=internalDestination)
    if internalDestination in self.subscriptions:
      raise MqClientExceptionClass("mq client Only supports onesubscription per destination")
    self.subscriptions[internalDestination] = msgRecieveFunction
    self._registerSubscription(internalDestination=internalDestination)

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

  def close(self, wait=False):
    #if wait is true then hang until threads etc are stopped
    self._close(wait=wait)
    if self.recieveThread is not None:
      self.recieveThread.close(wait=wait)

  def startRecieveThread(self, sleepTime=0.2):
    if self.recieveThread is not None:
      raise MqClientExceptionClass("Trying to start recieve thread twice")
    self.recieveThread = RecieveThread(sleepTime, loopIterationFunction=self.processLoopIteration)
    self.recieveThread.start()

  # Functions called from derived class only
  def processMessageCALLEDFROMDERIVEDONLY(self, internalDestination, body):
    if internalDestination in self.subscriptions:
      self.subscriptions[internalDestination](destination=self._mapFromInternalDestination(internalDestination), body=body)

  # Functions implemented by derived classes

  def _sendStringMessage(self, internalDestination, body):
    raise Exception('_sendStringMessage Not Overridden')

  def _registerSubscription(self, internalDestination):
    pass #overriden by inherited classes incase they have logic

  def _processLoopIteration(self):
    pass #overriden by inherited classes incase they have logic

  def _close(self, wait):
    pass #overriden by inherited classes incase they have logic

  def _mapToInternalDestination(self, destination):
    return destination

  def _mapFromInternalDestination(self, destination):
    return destination
