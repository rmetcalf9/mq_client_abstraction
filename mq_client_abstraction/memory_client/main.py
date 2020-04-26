from ..clientBase import MqClientBaseClass
import queue

class mainClass(MqClientBaseClass):
  messageQueue = None
  def __init__(self, configDict):
    super(mainClass, self).__init__(configDict=configDict)

    # Using synchronised queue https://docs.python.org/3.6/library/queue.html
    self.messageQueue = queue.Queue()

  def _sendStringMessage(self, destination, body):
    self.messageQueue.put((destination, body))

  def _processLoopIteration(self):
    while not self.messageQueue.empty():
      (destination, body) = self.messageQueue.get()
      self.processMessageCALLEDFROMDERIVEDONLY(destination, body)
