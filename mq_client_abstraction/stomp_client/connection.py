import stomp
import ssl
from ..clientBase import MqClientExceptionClass
from .stompConnectionListener import StompConnectionListenerClass

class ConnectionClass():
  fullConnectionDetails = None # includes username and password
  stompConnection = None
  closed = None
  recieveFunction = None
  registeredSubscriptions = None

  def __init__(self, fullConnectionDetails, recieveFunction):
    self.closed = False
    self.fullConnectionDetails = fullConnectionDetails
    self.recieveFunction = recieveFunction
    self.registeredSubscriptions = []

    self.stompConnection = stomp.Connection(
      host_and_ports=[(fullConnectionDetails["FormattedConnectionDetails"]["Url"], fullConnectionDetails["FormattedConnectionDetails"]["Port"])])

    if fullConnectionDetails["FormattedConnectionDetails"]["Protocol"] == "stomp":
      pass
    elif fullConnectionDetails["FormattedConnectionDetails"]["Protocol"] == "stomp+ssl":
        self.stompConnection.set_ssl(
        for_hosts=[(fullConnectionDetails["FormattedConnectionDetails"]["Url"], fullConnectionDetails["FormattedConnectionDetails"]["Port"])],
        ssl_version=ssl.PROTOCOL_TLSv1_2)
    else:
      raise Exception("Unknown protocol")

    self.stompConnection.connect(
      fullConnectionDetails["Username"],
      fullConnectionDetails["Password"],
      wait=True
    )

  def sendStringMessage(self, internalDestination, body):
    if self.closed:
      raise MqClientExceptionClass("Trying to send message on closed STOMP connection")
    self.stompConnection.sendMessage(body=body, destination=internalDestination)

  def registerSubscription(self, internalDestination):
    if len(self.registeredSubscriptions) == 0:
      self.stompConnection.set_listener('', StompConnectionListenerClass(self.recieveFunction))
    self.registeredSubscriptions.append(internalDestination)
    self.stompConnection.subscribe(destination=internalDestination, id=1, ack='auto')


  def close(self, wait):
    self.closed = True
    self.stompConnection.close()
