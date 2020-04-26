import unittest

from nose.plugins.attrib import attr
def wipd(f):
    return attr('wip')(f)

class testHelperSuperClass(unittest.TestCase):
  def checkGotRightExceptionType(self, context, ExpectedException, msg=""):
    if (context.exception != None):
      if (context.exception != ExpectedException):
        if (not isinstance(context.exception,ExpectedException)):
          print("**** Wrong exception TYPE raised:")
          print("      expected: " + type(ExpectedException).__name__ + ' - ' + str(ExpectedException));
          print("           got: " + type(context.exception).__name__ + ' - ' + str(context.exception));
          print("")
          if context.exception.__traceback__ is None:
            print("No traceback data in origional exception")
          else:
            print("Origional exception Traceback: ", context.exception.__traceback__)
          raise context.exception
