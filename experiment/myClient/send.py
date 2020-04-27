import Common


mqClient = Common.getMqClient()

for x in range(0,10):
  mqClient.sendStringMessage(destination='/queue/test', body="Test Message " + str(x).zfill(3))

mqClient.close()


# python3 ./send.py