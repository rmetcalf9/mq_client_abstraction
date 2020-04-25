import Common

print("Start of reciever")

import time
import sys

import stomp

connectionDetails = Common.getConDetailsFromEnvironment()

conn = Common.StormConnectionClass(connectionDetails)

def messageProcessingFunction(headers, message):
  print('Main recieviecrasdsreceived a message "%s"' % message)

conn.subscribe(destination='/queue/test', messageProcessingFunction=messageProcessingFunction)

##conn.set_listener('', MyListener())
##conn.subscribe(destination='/queue/test', id=1, ack='auto')

try:
    while True:
        time.sleep(10)
except KeyboardInterrupt:
    print('interrupted - so exiting!')


conn.close()

print("Reciever terminated")