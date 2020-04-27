import TestHelperSuperClass
import mq_client_abstraction
import copy
import queue
import time

from eachclientWrapperFunctionsMemory import get as MemoryWraperFnsGet

clientTypesToTest = []
clientTypesToTest.append({
  "config": {"Type": "Memory"},
  "wrapperFunctions": MemoryWraperFnsGet()
})
# clientTypesToTest.append({"config": {
#   "Type": "Stomp",
#   "Username": "TestUsername",
#   "Password": "TestPassword",
#   "ConnectionString": "stomp+ssl://aa:1234"
# }})


class test_memoryclient(TestHelperSuperClass.testHelperSuperClass):

  def test_sendMessage(self):
    for clientTypeDict in clientTypesToTest:
      mqClient = mq_client_abstraction.createObjectStoreInstance(configDict=clientTypeDict["config"])
      self.assertEqual(mqClient.getType(),clientTypeDict["config"]["Type"])

      testMessage="asf435tyhbred3wvbr"
      testDestination="/queue/aa"

      class contextClass():
        waitingForResult = None
        def __init__(self):
          self.waitingForResult = True

      context = contextClass()

      def msgRecieveFunction(destination, body):
        context.waitingForResult = False
        self.assertEqual(destination,testDestination)
        self.assertEqual(body,testMessage)

      def exitFunction():
        return not context.waitingForResult
      clientTypeDict["wrapperFunctions"]["subscribeToDestination"](mqClient=mqClient, destination=testDestination, msgRecieveFunction=msgRecieveFunction)

      clientTypeDict["wrapperFunctions"]["sendStringMessage"](mqClient=mqClient, destination=testDestination, body=testMessage)

      #Run the process loop
      # for recieving messages
      clientTypeDict["wrapperFunctions"]["processLoop"](mqClient=mqClient, exitFunction=exitFunction, timeoutInSeconds=1)
      clientTypeDict["wrapperFunctions"]["close"](mqClient=mqClient, wait=True)

      self.assertEqual(context.waitingForResult,False, msg="Subscribed function never called")

  def test_sendMessagesToThreeDistenations(self):
    for clientTypeDict in clientTypesToTest:
      mqClient = mq_client_abstraction.createObjectStoreInstance(configDict=clientTypeDict["config"])

      testDestinations = {}
      testDestinations["/queue/dest001"] = {"testMEssage001", "testMEssage002", "testMEssage003"}
      testDestinations["/queue/dest002"] = {"testMEssage001", "testMEssage002", "testMEssage003"}
      testDestinations["/queue/dest003"] = {"testMEssage001", "testMEssage002", "testMEssage003"}

      class contextClass():
        unrecievedMessages = None
        testClass = None
        def __init__(self, testDestinations, testClass):
          self.unrecievedMessages = copy.deepcopy(testDestinations)
          self.testClass = testClass
        def getNumRemaingMessages(self):
          a = 0
          for x in self.unrecievedMessages:
            a += len(self.unrecievedMessages[x])
          return a
        def registerRecieved(self, destination, body):
          self.testClass.assertTrue( destination in self.unrecievedMessages)
          self.testClass.assertTrue( body in self.unrecievedMessages[destination])
          self.unrecievedMessages[destination].remove(body)

      context = contextClass(testDestinations, testClass=self)

      def msgRecieveFunctionDest001(destination, body):
        self.assertEqual(destination,list(testDestinations.keys())[0], msg="Wrong recieve function called")
        context.registerRecieved(destination=destination, body=body)
      def msgRecieveFunctionDest002(destination, body):
        self.assertEqual(destination,list(testDestinations.keys())[1], msg="Wrong recieve function called")
        context.registerRecieved(destination=destination, body=body)
      def msgRecieveFunctionDest003(destination, body):
        self.assertEqual(destination,list(testDestinations.keys())[2], msg="Wrong recieve function called")
        context.registerRecieved(destination=destination, body=body)

      clientTypeDict["wrapperFunctions"]["subscribeToDestination"](mqClient=mqClient, destination=list(testDestinations.keys())[0], msgRecieveFunction=msgRecieveFunctionDest001)
      clientTypeDict["wrapperFunctions"]["subscribeToDestination"](mqClient=mqClient, destination=list(testDestinations.keys())[1], msgRecieveFunction=msgRecieveFunctionDest002)
      clientTypeDict["wrapperFunctions"]["subscribeToDestination"](mqClient=mqClient, destination=list(testDestinations.keys())[2], msgRecieveFunction=msgRecieveFunctionDest003)

      for destination in testDestinations:
        for message in testDestinations[destination]:
          clientTypeDict["wrapperFunctions"]["sendStringMessage"](mqClient=mqClient, destination=destination,body=message)

      def exitFunction():
        return context.getNumRemaingMessages() == 0

      clientTypeDict["wrapperFunctions"]["processLoop"](mqClient=mqClient, exitFunction=exitFunction, timeoutInSeconds=1)
      clientTypeDict["wrapperFunctions"]["close"](mqClient=mqClient, wait=True)


      for destination in context.unrecievedMessages:
        self.assertEqual(len(context.unrecievedMessages[destination]),0,msg="Messeges not recieved for " + destination)

  def test_sendMessageAndRecieveUsingQueue(self):
    for clientTypeDict in clientTypesToTest:
      mqClient = mq_client_abstraction.createObjectStoreInstance(configDict=clientTypeDict["config"])

      testMessage="asf435tyhbred3wvbr"
      testDestination="/queue/aa"

      recieveQueue = queue.Queue()
      clientTypeDict["wrapperFunctions"]["subscribeDestinationToPythonQueue"](mqClient=mqClient, destination=testDestination, queue=recieveQueue)

      clientTypeDict["wrapperFunctions"]["sendStringMessage"](mqClient=mqClient, destination=testDestination, body=testMessage)

      try:
        clientTypeDict["wrapperFunctions"]["processLoop"](mqClient=mqClient, exitFunction=None,timeoutInSeconds=0.01)
      except mq_client_abstraction.MqClientProcessLoopTimeoutExceptionClass:
        pass #ignore timeout
      clientTypeDict["wrapperFunctions"]["close"](mqClient=mqClient, wait=True)

      self.assertEqual(recieveQueue.qsize(), 1)
      msgRecieved = recieveQueue.get()
      self.assertEqual(msgRecieved, testMessage, msg="Wrong message recieved")


  def test_sendMessageAndRecieveUsingQueueInSeperateThread(self):
    for clientTypeDict in clientTypesToTest:
      mqClient = mq_client_abstraction.createObjectStoreInstance(configDict=clientTypeDict["config"])

      testMessage="asf435tyhbred3wvbr"
      testDestination="/queue/aa"

      recieveQueue = queue.Queue()
      clientTypeDict["wrapperFunctions"]["subscribeDestinationToPythonQueue"](mqClient=mqClient, destination=testDestination, queue=recieveQueue)

      clientTypeDict["wrapperFunctions"]["sendStringMessage"](mqClient=mqClient, destination=testDestination, body=testMessage)

      clientTypeDict["wrapperFunctions"]["startRecieveThread"](mqClient=mqClient, sleepTime=0.1)

      time.sleep(0.3)

      clientTypeDict["wrapperFunctions"]["close"](mqClient=mqClient, wait=True)

      self.assertEqual(recieveQueue.qsize(), 1)
      msgRecieved = recieveQueue.get()
      self.assertEqual(msgRecieved, testMessage, msg="Wrong message recieved")