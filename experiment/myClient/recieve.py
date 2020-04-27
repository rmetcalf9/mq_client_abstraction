import Common
import queue
import time

mqClient = Common.getMqClient()

destinationToTest="/queue/test"

#recieveQueue = queue.Queue()
#mqClient.subscribeDestinationToPythonQueue(destination=destination, queue=recieveQueue)
# mqClient.startRecieveThread(sleepTime=0.1)
# time.sleep(0.3)
# mqClient.close(wait=True)
# while not recieveQueue.empty():
#   (message) = recieveQueue.get()
#   print("Recieved ", message)

def msgRecieveFunction(destination, body):
  print("Recieved ", body, " sent to " , destination)

mqClient.subscribeToDestination(destination=destinationToTest, msgRecieveFunction=msgRecieveFunction)

try:
    while True:
        time.sleep(10)
except KeyboardInterrupt:
    print('interrupted - so exiting!')



# python3 ./recieve.py