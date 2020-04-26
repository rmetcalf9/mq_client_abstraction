import TestHelperSuperClass
import mq_client_abstraction

class test_mainfunctionality(TestHelperSuperClass.testHelperSuperClass):
  def test_initNoParamFails(self):
    configDict = {}
    with self.assertRaises(Exception) as context:
      mqClient = mq_client_abstraction.createObjectStoreInstance(configDict=configDict)
    self.checkGotRightExceptionType(context,mq_client_abstraction.MqClientExceptionClass)
    self.assertEqual(str(context.exception),"Invalid object store config - Type Missing")

  def test_initInvalidTypeFails(self):
    configDict = {
      "Type": "invalid"
    }
    with self.assertRaises(Exception) as context:
      mqClient = mq_client_abstraction.createObjectStoreInstance(configDict=configDict)
    self.checkGotRightExceptionType(context,mq_client_abstraction.MqClientExceptionClass)
    self.assertEqual(str(context.exception),"Invalid object store config Type - invalid")

