import stomp
import time

stompurl = "127.0.0.1"
stompport = "61613"
stompuser = "admin"
stomppass = "admin"
destination = "/queue/testQueueWithCrash"

conn = stomp.Connection(host_and_ports=[(stompurl, stompport)])
conn.connect(stompuser,stomppass,wait=True)

class StompConnectionListenerClass(stomp.ConnectionListener):
  processMessage = None
  conn = None
  def __init__(self, processMessage, conn):
    self.processMessage = processMessage
    self.conn = conn
  def on_error(self, headers, message):
    print('XX received an error "%s"' % message)
  def on_message(self, headers, message):
    try:
      self.processMessage(headers, message)
    finally:
      self.conn.ack(id=headers["message-id"], subscription=headers["subscription"])

def messageProcessingFunction(headers, message):
  print('Main recieved a message "%s"' % message)
  if (message=="CRASH"):
    print("Message told processor to crash")
    raise Exception("Reached message which crashes reciever")
  time.sleep(1) # simulate processing message taking time

stompConnectionListener = StompConnectionListenerClass(processMessage=messageProcessingFunction, conn=conn)
conn.set_listener('', stompConnectionListener)

print("Subscribing")
conn.subscribe(destination=destination, id=1, ack='client-individual', headers={'activemq.prefetchSize': 1})

print("Terminate loop starting (Press ctrl+c when you want to exit)")
try:
    while True:
        time.sleep(10)
except KeyboardInterrupt:
    print('interrupted - so exiting!')

conn.close()

print("Reciever terminated")