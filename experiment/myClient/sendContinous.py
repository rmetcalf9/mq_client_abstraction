import Common


mqClient = Common.getMqClient()

msgNum=0
try:
  while True:
    msgNum = msgNum + 1
    mqClient.sendStringMessage(destination='/queue/test', body="Test Message (continous send) " + str(msgNum).zfill(3))
    time.sleep(10)
except KeyboardInterrupt:
  print('interrupted - so exiting!')

mqClient.close(wait=True)


# python3 ./send.py