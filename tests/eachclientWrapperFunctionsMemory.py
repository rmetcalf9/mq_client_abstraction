# These are essentially null wrapper functions as Memory is it's own mock
import mq_client_abstraction

def sendStringMessage(mqClient, testContext, destination, body):
  mqClient.sendStringMessage(destination=destination, body=body)


def subscribeToDestination(mqClient, testContext, destination, msgRecieveFunction):
  mqClient.subscribeToDestination(destination=destination, msgRecieveFunction=msgRecieveFunction)

def close(mqClient, testContext, wait):
  mqClient.close(wait=wait)


def processLoop(mqClient, testContext, exitFunction, timeoutInSeconds):
  mqClient.processLoop(
    exitFunction=exitFunction,
    timeoutInSeconds=timeoutInSeconds
  )

def subscribeDestinationToPythonQueue(mqClient, testContext, destination, queue):
  mqClient.subscribeDestinationToPythonQueue(destination=destination, queue=queue)

def startRecieveThread(mqClient, testContext, sleepTime):
  mqClient.startRecieveThread(sleepTime=sleepTime)

def createMqClientInstance(testContext, configDict):
  return mq_client_abstraction.createMQClientInstance(configDict=configDict)

def get():
  return {
    "sendStringMessage": sendStringMessage,
    "subscribeToDestination": subscribeToDestination,
    "close": close,
    "processLoop": processLoop,
    "subscribeDestinationToPythonQueue": subscribeDestinationToPythonQueue,
    "startRecieveThread": startRecieveThread,
    "createMqClientInstance": createMqClientInstance
  }