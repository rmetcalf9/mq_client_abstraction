import Common
import queue
import time

mqClient = Common.getMqClient()

recieveQueue = queue.Queue()

mqClient.subscribeDestinationToPythonQueue(destination="/queue/test", queue=recieveQueue)
mqClient.startRecieveThread(sleepTime=0.1)
time.sleep(0.3)
mqClient.close(wait=True)
while not recieveQueue.empty():
  (message) = recieveQueue.get()
  print("Recieved ", message)

# python3 ./recieve.py