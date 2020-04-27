import os
import stomp
import ssl

def getFromEnvironment(envVariableName):
  if envVariableName not in os.environ:
    print("Error environment variable " + envVariableName + " not set")
    raise Exception("Error environment variable " + envVariableName + " not set")
  return os.environ[envVariableName]


def getConDetailsFromEnvironment():
  return {
    "stompConnectionString": getFromEnvironment("RJMACTIVEMQ_CONNSTR"),

    "username": getFromEnvironment("RJMACTIVEMQ_USER"),
    "password": getFromEnvironment("RJMACTIVEMQ_PASS")
  }

class StormConnectionListenerClass(stomp.ConnectionListener):
  subscriptions = None

  def registerSubscription(self, destination, messageProcessingFunction):
    self.subscriptions[destination] = messageProcessingFunction

  def __init__(self, conn):
    conn.set_listener('', self)
    self.subscriptions = {}
  def on_error(self, headers, message):
    print('XX received an error "%s"' % message)
  def on_message(self, headers, message):
    if headers["destination"] in self.subscriptions:
      self.subscriptions[headers["destination"]](headers, message)

class StormConnectionClass():
  connectionDetails = None
  conn = None
  messageProcessingFunction = None
  stormConnectionListener = None

  def __init__(self, connectionDetails):
    self.connectionDetails = connectionDetails
    self.subscriptions = {}
    self.stormConnectionListener = None


    tmp = connectionDetails["stompConnectionString"].split("://")
    protocol = tmp[0]
    connectionString = tmp[1]
    usessl=True
    stompurl=""
    stompport=0
    connectionStringSeperated = connectionString.split(":")
    if protocol=="stomp":
      usessl = False
      stompurl = connectionStringSeperated[0]
      stompport = connectionStringSeperated[1]
    elif protocol=="stomp+ssl":
      stompurl = connectionStringSeperated[0]
      stompport = connectionStringSeperated[1]
    else:
      raise Exception("Invlaid protocol")

    #print("url", stompurl)
    #print("port", stompport)
    self.conn = stomp.Connection(
      host_and_ports=[(stompurl, stompport)])
    if usessl:
      self.conn.set_ssl(
        for_hosts=[(stompurl, stompport)],
        ssl_version=ssl.PROTOCOL_TLSv1_2)

    self.conn.connect(
      connectionDetails["username"],
      connectionDetails["password"],
      wait=True
    )

  def subscribe(self, destination, messageProcessingFunction):
    if destination in self.subscriptions:
      raise Exception("Two subscribers for same destination")
    if self.stormConnectionListener is None:
      self.stormConnectionListener = StormConnectionListenerClass(self.conn)
    self.stormConnectionListener.registerSubscription(destination, messageProcessingFunction)
    self.conn.subscribe(destination=destination, id=1, ack='auto')

  def sendMessage(self, body, destination):
    self.conn.send(body=body, destination=destination)

  def close(self):
    self.conn.disconnect()
