import stomp

stompurl = "127.0.0.1"
stompport = "61613"
stompuser = "admin"
stomppass = "admin"
destination = "/queue/testQueueWithCrash"

conn = stomp.Connection(host_and_ports=[(stompurl, stompport)])
conn.connect(stompuser,stomppass,wait=True)

for x in range(0,5):
  conn.send(body="OK-BEFORE-CRASH", destination=destination)

conn.send(body="CRASH", destination=destination)

for x in range(0,50):
  conn.send(body="OK-AFTER-CRASH", destination=destination)
