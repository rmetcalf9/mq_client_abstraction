import TestHelperSuperClass
import mq_client_abstraction

class test_mainfunctionality(TestHelperSuperClass.testHelperSuperClass):
  def test_initNoParamFails(self):
    configDict = {}
    with self.assertRaises(Exception) as context:
      mqClient = mq_client_abstraction.createObjectStoreInstance(configDict=configDict)
    self.checkGotRightExceptionType(context,mq_client_abstraction.MqClientExceptionClass)
    self.assertEqual(str(context.exception),"Invalid mq client config - Type Missing")

  def test_initInvalidTypeFails(self):
    configDict = {
      "Type": "invalid"
    }
    with self.assertRaises(Exception) as context:
      mqClient = mq_client_abstraction.createObjectStoreInstance(configDict=configDict)
    self.checkGotRightExceptionType(context,mq_client_abstraction.MqClientExceptionClass)
    self.assertEqual(str(context.exception),"Invalid mq client config Type - invalid")


  def test_initDefaultGivesMemoryStore(self):
    configDict = None
    mqClient = mq_client_abstraction.createObjectStoreInstance(configDict=configDict)
    self.assertEqual(mqClient.getType(),"Memory")

  def test_initInvalidDestinationPrefixFails(self):
    configDict = {
      "Type": "Memory",
      "DestinationPrefix": "fr%$£"
    }
    with self.assertRaises(Exception) as context:
      mqClient = mq_client_abstraction.createObjectStoreInstance(configDict=configDict)
    self.checkGotRightExceptionType(context,mq_client_abstraction.MqClientExceptionClass)
    self.assertEqual(str(context.exception),"Invalid DestinationPrefix")
