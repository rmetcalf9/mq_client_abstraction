import Common


mqClient = Common.getMqClient()
queues = ["DUMMY", "/queue/test01","/queue/test02","/queue/test03","/queue/test04","/queue/test05"]

it = 1
try:
  running = True
  while running:
    strr = input("Queue[1..5] NumMessages:").strip()
    if strr.lower() == "exit":
      running = False
    else:
      x = strr.split(" ")
      if len(x) != 2:
        print("Not understood")
      else:
        try:
          queueNum = int(x[0])
          if queueNum < 1:
            print("Queue num to low")
          elif queueNum > len(queues):
            print("Queue num to high")
          else:
            try:
              numMessages = int(x[1])
              for x in range(0, numMessages):
                msg = "Test Message " + str(it).zfill(3)
                print ("Sending " + msg + " to " + queues[queueNum])
                mqClient.sendStringMessage(destination=queues[queueNum], body=msg)
                it = it + 1
            except ValueError as err:
              print("Bad number or messages")
        except ValueError as err:
          print("Bad queue number")

except KeyboardInterrupt:
  print('interrupted - so exiting!')

mqClient.close(wait=True)


mqClient.close(wait=True)
