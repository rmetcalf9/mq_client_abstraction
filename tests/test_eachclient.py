import TestHelperSuperClass
import mq_client_abstraction
import copy

clientTypesToTest = []
clientTypesToTest.append({"Type": "Memory"})


class test_memoryclient(TestHelperSuperClass.testHelperSuperClass):

  def test_sendMessage(self):
    for configDict in clientTypesToTest:
      mqClient = mq_client_abstraction.createObjectStoreInstance(configDict=configDict)
      self.assertEqual(mqClient.getType(),"Memory")

      testMessage="asf435tyhbred3wvbr"
      testDestination="aa"

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
      mqClient.subscribeToDestination(destination=testDestination, msgRecieveFunction=msgRecieveFunction)

      mqClient.sendStringMessage(destination=testDestination, body=testMessage)

      #Run the process loop
      # for recieving messages
      mqClient.processLoop(
        exitFunction=exitFunction,
        timeoutInSeconds=1
      )
      mqClient.close()

      self.assertEqual(context.waitingForResult,False, msg="Subscribed function never called")

  def test_sendMessagesToThreeDistenations(self):
    for configDict in clientTypesToTest:
      mqClient = mq_client_abstraction.createObjectStoreInstance(configDict=configDict)
      self.assertEqual(mqClient.getType(),"Memory")

      testDestinations = {}
      testDestinations["dest001"] = {"testMEssage001", "testMEssage002", "testMEssage003"}
      testDestinations["dest002"] = {"testMEssage001", "testMEssage002", "testMEssage003"}
      testDestinations["dest003"] = {"testMEssage001", "testMEssage002", "testMEssage003"}

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
        self.assertEqual(destination,"dest001", msg="Wrong recieve function called")
        context.registerRecieved(destination=destination, body=body)
      def msgRecieveFunctionDest002(destination, body):
        self.assertEqual(destination,"dest002", msg="Wrong recieve function called")
        context.registerRecieved(destination=destination, body=body)
      def msgRecieveFunctionDest003(destination, body):
        self.assertEqual(destination,"dest003", msg="Wrong recieve function called")
        context.registerRecieved(destination=destination, body=body)

      mqClient.subscribeToDestination(destination="dest001", msgRecieveFunction=msgRecieveFunctionDest001)
      mqClient.subscribeToDestination(destination="dest002", msgRecieveFunction=msgRecieveFunctionDest002)
      mqClient.subscribeToDestination(destination="dest003", msgRecieveFunction=msgRecieveFunctionDest003)


      for destination in testDestinations:
        for message in testDestinations[destination]:
          mqClient.sendStringMessage(destination=destination, body=message)

      def exitFunction():
        return context.getNumRemaingMessages() == 0

      mqClient.processLoop(
        exitFunction=exitFunction,
        timeoutInSeconds=1
      )
      mqClient.close()


      for destination in context.unrecievedMessages:
        self.assertEqual(len(context.unrecievedMessages[destination]),0,msg="Messeges not recieved for " + destination)