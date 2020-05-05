import stomp

stompurl = "127.0.0.1"
stompport = "61613"
stompuser = "admin"
stomppass = "admin"
destination = "/queue/testQueueWithCrash"

conn = stomp.Connection(host_and_ports=[(stompurl, stompport)])
conn.connect(stompuser,stomppass,wait=True)

i = 1

for x in range(0,5):
  msg = "OK-BEFORE-CRASH" + str(i)
  conn.send(body=msg, destination=destination)
  print("Sending ", msg)
  i = i + 1

msg = "CRASH" + str(i)
conn.send(body=msg, destination=destination)
print("Sending ", msg)
i = i + 1

for x in range(0,20):
  msg = "OK-AFTER-CRASH" + str(i)
  conn.send(body=msg, destination=destination)
  i = i + 1
  print("Sending ", msg)
