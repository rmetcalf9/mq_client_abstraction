import Common
import queue
import time
import sys

mqClient = Common.getMqClient()

destinationToTest="/queue/test"

def receiveUsingThread():
  print("receiveUsingThread")
  recieveQueue = queue.Queue()
  mqClient.subscribeDestinationToPythonQueue(destination=destinationToTest, queue=recieveQueue)
  mqClient.startReceiveThread(sleepTime=0.1)

  it = 1

  try:
    while True:
      print("loop receiveUsingThread", it)
      it = it + 1
      mqClient.threadHealthCheck()
      while not recieveQueue.empty():
        (message) = recieveQueue.get()
        print("Received ", message)
      time.sleep(1)
  except KeyboardInterrupt:
    print('interrupted - so exiting!')

  mqClient.close(wait=True)


def receiveUsingApplicationProvidedProcessLoop():
  print("receiveUsingApplicationProvidedProcessLoop")
  def msgReceiveFunction(destination, body):
    print("Received ", body, " sent to " , destination)
  mqClient.subscribeToDestination(destination=destinationToTest, msgRecieveFunction=msgRecieveFunction)

  it = 1
  try:
      while True:
        print("process loop (receiveUsingApplicationProvidedProcessLoop) ", it)
        mqClient.processLoopIteration()
        it = it + 1
        time.sleep(1)
  except KeyboardInterrupt:
      print('interrupted - so exiting!')

  mqClient.close(wait=True)

def receiveUsingProcessLoop():
  print("receiveUsingProcessLoop")
  def msgReceiveFunction(destination, body):
    print("Received " + destination + " processing " + body, end="")
    sys.stdout.flush()
    for a in range(0,6):
      print(".", end="")
      sys.stdout.flush()
      time.sleep(0.3)
    print(".")
    sys.stdout.flush()
    sys.stdout.flush()

  mqClient.subscribeToDestination(destination=destinationToTest, msgRecieveFunction=msgRecieveFunction)
  mqClient.subscribeToDestination(destination=destinationToTest + "2", msgRecieveFunction=msgRecieveFunction)

  class Counter():
    num = None
    def __init__(self):
      self.num = 0
    def plusplus(self):
      self.num = self.num + 1
      return self.num
  counter = Counter()

  def functionToRunOnEachIteration():
    print("Loop iteration function (receiveUsingProcessLoop)", counter.plusplus())
  mqClient.processLoop(
    exitFunction=None,
    timeoutInSeconds=None,
    sleepDurationInSeconds=1,
    functionToRunOnEachIteration=functionToRunOnEachIteration
  )

  mqClient.close(wait=True)

print("Started")

if (len(sys.argv)==1):
  recieveUsingThread()
elif (len(sys.argv)==2):
  if sys.argv[1]=='A':
    recieveUsingThread()
  elif sys.argv[1]=='B':
    recieveUsingApplicationProvidedProcessLoop()
  elif sys.argv[1]=='C':
    recieveUsingProcessLoop()
  else:
    print("Arg must be A, B, or C")
else:
  print("Only one arg")


print("Finished")

# python3 ./recieve.py
