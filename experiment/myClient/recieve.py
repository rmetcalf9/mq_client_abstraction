import Common
import queue
import time

mqClient = Common.getMqClient()

destinationToTest="/queue/test"

def recieveUsingThread():
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


def recieveUsingProcess():
  def msgRecieveFunction(destination, body):
    print("Recieved ", body, " sent to " , destination)

  mqClient.subscribeToDestination(destination=destinationToTest, msgRecieveFunction=msgRecieveFunction)

  try:
      while True:
          time.sleep(10)
  except KeyboardInterrupt:
      print('interrupted - so exiting!')


print("Started")
recieveUsingThread()
print("Finished")

# python3 ./recieve.py