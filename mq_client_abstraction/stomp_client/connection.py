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
  connected = None

  def __init__(self, fullConnectionDetails, recieveFunction):
    self.closed = False
    self.fullConnectionDetails = fullConnectionDetails
    self.recieveFunction = recieveFunction
    self.registeredSubscriptions = []
    self.connected = False

    self.stompConnection = stomp.Connection(
      host_and_ports=[(self.fullConnectionDetails["FormattedConnectionDetails"]["Url"], self.fullConnectionDetails["FormattedConnectionDetails"]["Port"])])

    self._connectIfNeeded()

  def _connectIfNeeded(self):
    if self.connected:
      return
    if self.fullConnectionDetails["FormattedConnectionDetails"]["Protocol"] == "stomp":
      pass
    elif self.fullConnectionDetails["FormattedConnectionDetails"]["Protocol"] == "stomp+ssl":
      self.stompConnection.set_ssl(
        for_hosts=[(self.fullConnectionDetails["FormattedConnectionDetails"]["Url"],
                    self.fullConnectionDetails["FormattedConnectionDetails"]["Port"])],
        ssl_version=ssl.PROTOCOL_TLSv1_2)
    else:
      raise Exception("Unknown protocol")

    self.stompConnection.connect(
      self.fullConnectionDetails["Username"],
      self.fullConnectionDetails["Password"],
      wait=True
    )
    self.connected = True

  def _onDisconnected(self):
    self.connected = False
    # If we have subscribers then we must reconnect and register all the subscriptions again
    #  otherwise we cna wait and only reconnect when sendStringMessage or registerSubscription is called
    if len(self.registeredSubscriptions) == 0:
      return
    self._connectIfNeeded()
    for internalDestination in self.registeredSubscriptions():
      self.stompConnection.subscribe(destination=internalDestination, id=1, ack='auto')

  def sendStringMessage(self, internalDestination, body):
    if self.closed:
      raise MqClientExceptionClass("Trying to send message on closed STOMP connection")
    self._connectIfNeeded()
    self.stompConnection.send(body=body, destination=internalDestination)

  def registerSubscription(self, internalDestination):
    self._connectIfNeeded()
    if len(self.registeredSubscriptions) == 0:
      self.stompConnection.set_listener('', StompConnectionListenerClass(recieveFunction=self.recieveFunction, disconnectedFunciton=self._onDisconnected))
    self.registeredSubscriptions.append(internalDestination)
    self.stompConnection.subscribe(destination=internalDestination, id=1, ack='auto')


  def close(self, wait):
    self.closed = True
    self.stompConnection.disconnect()
