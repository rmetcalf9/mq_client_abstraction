# These are essentially null wrapper functions as Memory is it's own mock


def sendStringMessage(mqClient, destination, body):
  mqClient.sendStringMessage(destination=destination, body=body)


def subscribeToDestination(mqClient, destination, msgRecieveFunction):
  mqClient.subscribeToDestination(destination=destination, msgRecieveFunction=msgRecieveFunction)

def close(mqClient, wait):
  mqClient.close(wait=wait)


def processLoop(mqClient, exitFunction, timeoutInSeconds):
  mqClient.processLoop(
    exitFunction=exitFunction,
    timeoutInSeconds=timeoutInSeconds
  )

def subscribeDestinationToPythonQueue(mqClient, destination, queue):
  mqClient.subscribeDestinationToPythonQueue(destination=destination, queue=queue)

def startRecieveThread(mqClient, sleepTime):
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