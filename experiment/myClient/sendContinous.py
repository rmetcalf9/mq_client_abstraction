import Common
import time

mqClient = Common.getMqClient()

msgNum=0
try:
  while True:
    msgNum = msgNum + 1
    msgBody = "Test Message (continous send) " + str(msgNum).zfill(3)
    mqClient.sendStringMessage(destination='/queue/test', body=msgBody)
    print("Sent - ", "Test Message (continous send) " + str(msgNum).zfill(3))
    time.sleep(0.5)
except KeyboardInterrupt:
  print('interrupted - so exiting!')

mqClient.close(wait=True)


# python3 ./send.py