# Tests spercific to stomp client

import TestHelperSuperClass
import mq_client_abstraction
import copy

class test_stompClient(TestHelperSuperClass.testHelperSuperClass):
  def test_initInvalidDestinationPrefixFails(self):
    configDict = {
      "Type": "Memory",
      "DestinationPrefix": "fr%$£"
    }
    with self.assertRaises(Exception) as context:
      mqClient = mq_client_abstraction.createObjectStoreInstance(configDict=configDict)
    self.checkGotRightExceptionType(context,mq_client_abstraction.MqClientExceptionClass)
    self.assertEqual(str(context.exception),"Invalid DestinationPrefix")

  def test_initWithMissingUsername(self):
    configDict = {
      "Type": "Stomp"
    }
    with self.assertRaises(Exception) as context:
      mqClient = mq_client_abstraction.createObjectStoreInstance(configDict=configDict)
    self.checkGotRightExceptionType(context,mq_client_abstraction.MqClientExceptionClass)
    self.assertEqual(str(context.exception),"Invalid mq client config - Missing Username")

  def test_initWithMissingPassword(self):
    configDict = {
      "Type": "Stomp",
      "Username": "TestUsername"
    }
    with self.assertRaises(Exception) as context:
      mqClient = mq_client_abstraction.createObjectStoreInstance(configDict=configDict)
    self.checkGotRightExceptionType(context,mq_client_abstraction.MqClientExceptionClass)
    self.assertEqual(str(context.exception),"Invalid mq client config - Missing Password")

  def test_initWithMissingConnectionString(self):
    configDict = {
      "Type": "Stomp",
      "Username": "TestUsername",
      "Password": "TestPassword"
    }
    with self.assertRaises(Exception) as context:
      mqClient = mq_client_abstraction.createObjectStoreInstance(configDict=configDict)
    self.checkGotRightExceptionType(context,mq_client_abstraction.MqClientExceptionClass)
    self.assertEqual(str(context.exception),"Invalid mq client config - Missing ConnectionString")

  def test_initWithInvalidConnectionString(self):
    configDict = {
      "Type": "Stomp",
      "Username": "TestUsername",
      "Password": "TestPassword",
      "ConnectionString": "InvalidConnectionString"
    }
    with self.assertRaises(Exception) as context:
      mqClient = mq_client_abstraction.createObjectStoreInstance(configDict=configDict)
    self.checkGotRightExceptionType(context,mq_client_abstraction.MqClientExceptionClass)
    self.assertEqual(str(context.exception),"Invalid mq client config - Invalid ConnectionString")

  def test_initWithInvalidProtocol(self):
    configDict = {
      "Type": "Stomp",
      "Username": "TestUsername",
      "Password": "TestPassword",
      "ConnectionString": "badstomp+ssl://aaa.mq.xxx.amazonaws.com:61614"
    }
    with self.assertRaises(Exception) as context:
      mqClient = mq_client_abstraction.createObjectStoreInstance(configDict=configDict)
    self.checkGotRightExceptionType(context,mq_client_abstraction.MqClientExceptionClass)
    self.assertEqual(str(context.exception),"Invalid mq client config - Invalid ConnectionString (Bad Protocol)")

  def test_initWithMissingPort(self):
    configDict = {
      "Type": "Stomp",
      "Username": "TestUsername",
      "Password": "TestPassword",
      "ConnectionString": "stomp+ssl://aaa.mq.xxx.amazonaws.com"
    }
    with self.assertRaises(Exception) as context:
      mqClient = mq_client_abstraction.createObjectStoreInstance(configDict=configDict)
    self.checkGotRightExceptionType(context,mq_client_abstraction.MqClientExceptionClass)
    self.assertEqual(str(context.exception),"Invalid mq client config - Invalid ConnectionString (Missing Port)")

  def test_initWithPortNotNumber(self):
    configDict = {
      "Type": "Stomp",
      "Username": "TestUsername",
      "Password": "TestPassword",
      "ConnectionString": "stomp+ssl://aaa.mq.xxx.amazonaws.com:abc"
    }
    with self.assertRaises(Exception) as context:
      mqClient = mq_client_abstraction.createObjectStoreInstance(configDict=configDict)
    self.checkGotRightExceptionType(context,mq_client_abstraction.MqClientExceptionClass)
    self.assertEqual(str(context.exception),"Invalid mq client config - Invalid ConnectionString (Port must be a number)")

  def test_initWithNegativePort(self):
    configDict = {
      "Type": "Stomp",
      "Username": "TestUsername",
      "Password": "TestPassword",
      "ConnectionString": "stomp+ssl://aaa.mq.xxx.amazonaws.com:-123"
    }
    with self.assertRaises(Exception) as context:
      mqClient = mq_client_abstraction.createObjectStoreInstance(configDict=configDict)
    self.checkGotRightExceptionType(context,mq_client_abstraction.MqClientExceptionClass)
    self.assertEqual(str(context.exception),"Invalid mq client config - Invalid ConnectionString (Port not in range 0-65535)")

  def test_initWithTooHgihPort(self):
    configDict = {
      "Type": "Stomp",
      "Username": "TestUsername",
      "Password": "TestPassword",
      "ConnectionString": "stomp+ssl://aaa.mq.xxx.amazonaws.com:65536"
    }
    with self.assertRaises(Exception) as context:
      mqClient = mq_client_abstraction.createObjectStoreInstance(configDict=configDict)
    self.checkGotRightExceptionType(context,mq_client_abstraction.MqClientExceptionClass)
    self.assertEqual(str(context.exception),"Invalid mq client config - Invalid ConnectionString (Port not in range 0-65535)")

  def test_destinationValidMappings(self):
    validMappings = []
    validMappings.append( {
      "prefix": "",
      "destination": "/queue/test",
      "internaldestination": "/queue/test"
    })
    validMappings.append( {
      "prefix": "AABBXX",
      "destination": "/queue/test",
      "internaldestination": "/queue/AABBXXtest"
    })

    configDict = {
      "Type": "Stomp",
      "Username": "TestUsername",
      "Password": "TestPassword",
      "ConnectionString": "stomp+ssl://aa:1234",
      "skipConnectionCheck": True
    }
    for x in validMappings:
      configDict2 = copy.deepcopy(configDict)
      configDict2["DestinationPrefix"] = x["prefix"]
      mqClient = mq_client_abstraction.createObjectStoreInstance(configDict=configDict2)
      self.assertEqual(mqClient._mapToInternalDestination(x["destination"]), x["internaldestination"], msg="Map to destination failed")
      self.assertEqual(mqClient._mapFromInternalDestination(x["internaldestination"]), x["destination"], msg="Map from destination failed")

  def test_initWithAmazonListConnectionString(self):
    configDict = {
      "Type": "Stomp",
      "Username": "TestUsername",
      "Password": "TestPassword",
      "ConnectionString": "stomp+ssl://b-xx-xx-xx-xx-xx-1.mq.eu-west-2.amazonaws.com:61614",
      "skipConnectionCheck": True
    }
    mqClient = mq_client_abstraction.createObjectStoreInstance(configDict=configDict)


