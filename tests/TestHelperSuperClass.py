import unittest

from nose.plugins.attrib import attr
def wipd(f):
    return attr('wip')(f)

class testHelperSuperClass(unittest.TestCase):
  pass