#Recieve messages one at a time from a range of queues
import Common
import time
import sys

# Test with 5 queues

print("Start of recieveRangeOneByOne")

mqClient = Common.getMqClient()


def processMessageFromQueue(destination, body):
  print("Queue " + destination + " processing " + body, end="")
  sys.stdout.flush()
  # for a in range(0,6):
  #   print(".", end="")
  #   sys.stdout.flush()
  #   time.sleep(0.3)
  # print(".")
  # sys.stdout.flush()

mqClient.subscribeToDestination(destination="/queue/test01", msgRecieveFunction=processMessageFromQueue)
mqClient.subscribeToDestination(destination="/queue/test02", msgRecieveFunction=processMessageFromQueue)
mqClient.subscribeToDestination(destination="/queue/test03", msgRecieveFunction=processMessageFromQueue)
mqClient.subscribeToDestination(destination="/queue/test04", msgRecieveFunction=processMessageFromQueue)
mqClient.subscribeToDestination(destination="/queue/test05", msgRecieveFunction=processMessageFromQueue)

it = 1
try:
  while True:
    mqClient.processLoopIteration()
    it = it + 1
    print("MAIN LOOP SLEEPING FOR 5 SECONDS - " + str(it))
    time.sleep(5)
except KeyboardInterrupt:
  print('interrupted - so exiting!')

mqClient.close(wait=True)

mqClient.close(wait=True)

print("End of recieveRangeOneByOne")


# export RJMACTIVEMQ_USER=admin
# export RJMACTIVEMQ_PASS=admin
# export RJMACTIVEMQ_CONNSTR=stomp://127.0.0.1:61613
