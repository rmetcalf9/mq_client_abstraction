import time
import queue
import threading

# 3 ways or running:

# Thread based
# process loop function provided by mq_client
# process loop provided by caller

validDestinationPrefixes = ["/queue/", "/topic/" ]


class MqClientExceptionClass(Exception):
  pass

class MqClientProcessLoopTimeoutExceptionClass(MqClientExceptionClass):
  pass

class MqClientThreadHealthCheckExceptionClass(MqClientExceptionClass):
  pass

class RecieveThread(threading.Thread):
  running = None
  sleepTime = None
  stopped = None
  loopIterationFunction = None
  thrownException = None
  def __init__(self, sleepTime, loopIterationFunction):
    self.running = True
    self.sleepTime = sleepTime
    self.stopped = False
    self.loopIterationFunction = loopIterationFunction
    self.thrownException = None

    super(RecieveThread, self).__init__()

  def run(self):
    try:
      self.running = True
      print('MQ Client recieve thread starting')
      while self.running:
        self.loopIterationFunction()
        time.sleep(self.sleepTime)
      print('MQ Client recieve thread terminating')
      self.stopped = True
    except Exception as Excep:
      print("MQ CLient recieve thread throwing an Exception")
      self.thrownException = MqClientThreadHealthCheckExceptionClass("MQ Client recieve thread threw an exception - " +  str(self.selfthrownException))
      raise Excep

  def close(self, wait):
    #Run in controller thread to stop subthread
    if self.stopped:
      raise MqClientExceptionClass("Closing thread twice")
    self.stopped = False
    self.running = False
    if wait:
      while self.stopped == False:
        time.sleep(self.sleepTime)

  def healthCheck(self):
    #Run in controller thread to raise any exceptions
    if self.running:
      if not self.isAlive():
        raise MqClientThreadHealthCheckExceptionClass("MQ Client thread is no longer alive")
    if self.thrownException is not None:
      raise self.thrownException

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
    invalidChars = ['_', ':', '\\', '$', '%']
    for c in invalidChars:
      if c in destination:
        raise MqClientExceptionClass(msg)

  def sendStringMessage(self, destination, body):
    internalDestination = self._mapToInternalDestination(destination)
    self.validateDestination(destination=internalDestination)
    self._sendStringMessage(internalDestination=internalDestination, body=body)

  def subscribeToDestination(self, destination, msgRecieveFunction, prefetchSize=1, durableSubscriptionName=None):
    internalDestination = self._mapToInternalDestination(destination)
    self.validateDestination(destination=internalDestination)
    if internalDestination in self.subscriptions:
      raise MqClientExceptionClass("This mq client Only supports one subscription per destination")
    self.subscriptions[internalDestination] = msgRecieveFunction
    self._registerSubscription(internalDestination=internalDestination, prefetchSize=prefetchSize,durableSubscriptionName=durableSubscriptionName)

  def subscribeDestinationToPythonQueue(self, destination, queue, durableSubscriptionName=None):
    def msgRecieveFunction(destination, body):
      queue.put(body)
    # when going to a queue client is responsible for processing that queue
    self.subscribeToDestination(destination, msgRecieveFunction, prefetchSize=50, durableSubscriptionName=durableSubscriptionName)

  # The process loop is for recievers that need to keep a loop running. It is not required for some types of
  #  client (Stomp) but is requried for others (Memory)
  # It can be used in two ways, "processLoop" will run and call an exit function on each iteration
  # "processLoopIteration" is for apps which already have a process loop and it will just do it's checks then terminate.
  def processLoop(
    self,
    exitFunction,
    timeoutInSeconds=None,
    sleepDurationInSeconds=0.1,
    functionToRunOnEachIteration=None
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
        if functionToRunOnEachIteration is not None:
          functionToRunOnEachIteration()
        time.sleep(sleepDurationInSeconds)
        if timeoutInSeconds is not None:
          timeoutInSeconds -= sleepDurationInSeconds
          if timeoutInSeconds < 0:
            raise MqClientProcessLoopTimeoutExceptionClass("Process loop timeout reached")

  def processLoopIteration(self):
    self.processLoopHealthCheck()
    self._processLoopIteration()

  # Used for when application provides health check
  def processLoopHealthCheck(self):
    self._healthCheck()

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

  def threadHealthCheck(self):
    #Check the health of the thread and raise an exception if there is a problem
    if self.recieveThread is None:
      raise MqClientThreadHealthCheckExceptionClass("MQ Client thread was never started")
    self.recieveThread.healthCheck()
    try:
      self._healthCheck()
    except Exception as excpi:
      # Adapter health check has failed.
      #  if clientBase thread is still running it needs to be stopped or the application will not terminate
      self.recieveThread.close(wait=True)
      raise excpi

  #********************************************************
  # Functions called from derived class only
  #********************************************************
  def processMessageCALLEDFROMDERIVEDONLY(self, internalDestination, body):
    if internalDestination in self.subscriptions:
      self.subscriptions[internalDestination](destination=self._mapFromInternalDestination(internalDestination), body=body)

  #********************************************************
  # Functions implemented by derived classes
  #********************************************************

  def _sendStringMessage(self, internalDestination, body):
    raise Exception('_sendStringMessage Not Overridden')

  def _registerSubscription(self, internalDestination, prefetchSize, durableSubscriptionName):
    pass #overriden by inherited classes incase they have logic

  def _processLoopIteration(self):
    pass #overriden by inherited classes incase they have logic

  def _close(self, wait):
    pass #overriden by inherited classes incase they have logic

  def ___getUsedPrefix(self, destination):
    for x in validDestinationPrefixes:
      if destination.startswith(x):
        return x
    return None

  def _mapToInternalDestination(self, destination):
    usedPrefix = self.___getUsedPrefix(destination=destination)
    if usedPrefix is None:
      raise MqClientExceptionClass("Invalid Destination - Must start /queue/ or /topic/ (" + str(destination) + ")")
    return usedPrefix + self.destinationPrefix + destination[len(usedPrefix):]

  def _mapFromInternalDestination(self, destination):
    usedPrefix = self.___getUsedPrefix(destination=destination)
    if usedPrefix is None:
      raise MqClientExceptionClass("Invalid Destination")
    return usedPrefix + destination[len(usedPrefix) + len(self.destinationPrefix):]

  def _healthCheck(self):
    pass #Overridden for derived classes with threads to allow them to bubble exceptions to main thread
