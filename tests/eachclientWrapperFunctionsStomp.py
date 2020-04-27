from unittest import mock
import queue

def _setupTextContext(testContext):
  if not "mockConnectionObject" in testContext:
    testContext["mockConnectionObject"] = MockConnectionObjectClass()
  if "messagequeue" not in testContext:
    testContext["messagequeue"] = queue.Queue()
  if "subbedDests" not in testContext:
    testContext["subbedDests"] = []


def _transmitessagesInTextContext(testContext):
  while not testContext["messagequeue"].empty():
    (destination, body) =testContext["messagequeue"].get()
    if destination in testContext["subbedDests"]:
      headers = {
        "destination": destination
      }
      testContext["mockConnectionObject"].getStompListener().on_message(headers=headers, message=body)

class MockConnectionObjectClass():
  stompListener = None
  def set_ssl(self, for_hosts,ssl_version):
    return
  def connect(self, username, password, wait):
    return
  def send(self, body, destination):
    return
  def subscribe(self, destination, id, ack):
    return
  def set_listener(self, unknownParam, stompListener):
    self.stompListener = stompListener
  def disconnect(self):
    return

  def getStompListener(self):
    if self.stompListener is None:
      raise Exception("Trying to get listener but listner never set")
    return self.stompListener


def sendStringMessage(mqClient, testContext, destination, body):
  _setupTextContext(testContext=testContext)
  testContext["messagequeue"].put((destination, body))

  with mock.patch('stomp.Connection', return_value=testContext["mockConnectionObject"]) as stompConnection_function:
    mqClient.sendStringMessage(destination=destination, body=body)


def subscribeToDestination(mqClient, testContext, destination, msgRecieveFunction):
  _setupTextContext(testContext=testContext)
  testContext["subbedDests"].append(destination)

  with mock.patch('stomp.Connection', return_value=testContext["mockConnectionObject"]) as stompConnection_function:
    mqClient.subscribeToDestination(destination=destination, msgRecieveFunction=msgRecieveFunction)

def close(mqClient, testContext, wait):
  mqClient.close(wait=wait)

def processLoop(mqClient, testContext, exitFunction, timeoutInSeconds):
  _transmitessagesInTextContext(testContext=testContext)

  mqClient.processLoop(
    exitFunction=exitFunction,
    timeoutInSeconds=timeoutInSeconds
  )

def subscribeDestinationToPythonQueue(mqClient, testContext, destination, queue):
  if not "mockConnectionObject" in testContext:
    testContext["mockConnectionObject"] = MockConnectionObjectClass()
  if "subbedDests" not in testContext:
    testContext["subbedDests"] = []
  testContext["subbedDests"].append(destination)

  with mock.patch('stomp.Connection', return_value=testContext["mockConnectionObject"]) as stompConnection_function:
    mqClient.subscribeDestinationToPythonQueue(destination=destination, queue=queue)

def startRecieveThread(mqClient, testContext, sleepTime):
  _transmitessagesInTextContext(testContext=testContext)

  mqClient.startRecieveThread(sleepTime=sleepTime)


def get():
  return {
    "sendStringMessage": sendStringMessage,
    "subscribeToDestination": subscribeToDestination,
    "close": close,
    "processLoop": processLoop,
    "subscribeDestinationToPythonQueue": subscribeDestinationToPythonQueue,
    "startRecieveThread": startRecieveThread
  }