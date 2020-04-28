import Common
import queue
import time
import sys

mqClient = Common.getMqClient()

destinationToTest="/queue/test"

def recieveUsingThread():
  print("recieveUsingThread")
  recieveQueue = queue.Queue()
  mqClient.subscribeDestinationToPythonQueue(destination=destinationToTest, queue=recieveQueue)
  mqClient.startRecieveThread(sleepTime=0.1)

  try:
    while True:
      print("loop")
      mqClient.threadHealthCheck()
      while not recieveQueue.empty():
        (message) = recieveQueue.get()
        print("Recieved ", message)
      time.sleep(1)
  except KeyboardInterrupt:
    print('interrupted - so exiting!')

  mqClient.close(wait=True)


def recieveUsingApplicationProvidedProcessLoop():
  print("recieveUsingApplicationProvidedProcessLoop")
  def msgRecieveFunction(destination, body):
    print("Recieved ", body, " sent to " , destination)

  mqClient.subscribeToDestination(destination=destinationToTest, msgRecieveFunction=msgRecieveFunction)

  it = 1
  try:
      while True:
        print("process loop", it)
        mqClient.processLoopHealthCheck()
        it = it + 1
        time.sleep(1)
  except KeyboardInterrupt:
      print('interrupted - so exiting!')

  mqClient.close(wait=True)

def recieveUsingProcessLoop():
  print("recieveUsingProcessLoop")
  def msgRecieveFunction(destination, body):
    print("Recieved ", body, " sent to " , destination)

  mqClient.subscribeToDestination(destination=destinationToTest, msgRecieveFunction=msgRecieveFunction)

  def functionToRunOnEachIteration():
    print("Loop iteration function")

  mqClient.processLoop(
    exitFunction=None,
    timeoutInSeconds=None,
    sleepDurationInSeconds=0.1,
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
    print("Arge must be A, B, or C")
else:
  print("Only one arg")


print("Finished")

# python3 ./recieve.py