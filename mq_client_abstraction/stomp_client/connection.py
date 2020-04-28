import stomp
import ssl
from ..clientBase import MqClientExceptionClass, MqClientThreadHealthCheckExceptionClass
from .stompConnectionListener import StompConnectionListenerClass
import time

class ConnectionClass():
  fullConnectionDetails = None # includes username and password
  stompConnection = None
  closed = None
  recieveFunction = None
  registeredSubscriptions = None
  connected = None
  thrownException = None
  reconnectMaxRetries = None
  reconectInitialSecondsBetweenTries = None
  reconnectFadeoffFactor = None

  def __init__(self, fullConnectionDetails, recieveFunction, reconnectMaxRetries, reconectInitialSecondsBetweenTries, reconnectFadeoffFactor):
    self.closed = False
    self.fullConnectionDetails = fullConnectionDetails
    self.recieveFunction = recieveFunction
    self.registeredSubscriptions = []
    self.connected = False
    self.thrownException = None
    self.reconnectMaxRetries = reconnectMaxRetries
    self.reconectInitialSecondsBetweenTries = reconectInitialSecondsBetweenTries
    self.reconnectFadeoffFactor = reconnectFadeoffFactor

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

  def retryWrapperAround_connectIfNeeded(self):
    retriesRemaining = self.reconnectMaxRetries
    secondsBetweenTries = self.reconectInitialSecondsBetweenTries
    while not self.connected:
      exeptionRaised = None
      try:
        self._connectIfNeeded()
      except stomp.exception.ConnectFailedException as excpi:
        exeptionRaised = excpi
      except Exception as excpi:
        raise excpi
      if not self.connected:
        if retriesRemaining==0:
          print("Connection retry limit reached")
          raise exeptionRaised
        retriesRemaining = retriesRemaining - 1
        print("Waiting ", secondsBetweenTries, " seconds before next connection attempt")
        time.sleep(secondsBetweenTries)
        secondsBetweenTries = secondsBetweenTries * self.reconnectFadeoffFactor

  def _onError(self, headers, message):
    self.thrownException = MqClientThreadHealthCheckExceptionClass("STOMP onError called - " + message)
    raise Exception(message)

  def _onDisconnected(self):
    try:
      if self.closed:
        return
      self.connected = False
      # If we have subscribers then we must reconnect and register all the subscriptions again
      #  otherwise we cna wait and only reconnect when sendStringMessage or registerSubscription is called
      if len(self.registeredSubscriptions) == 0:
        return
      self.retryWrapperAround_connectIfNeeded()
      for internalDestination in self.registeredSubscriptions:
        self.stompConnection.subscribe(destination=internalDestination, id=1, ack='auto')
    except Exception as excepti:
      self.thrownException = MqClientThreadHealthCheckExceptionClass("Exception thrown in stomp")
      raise excepti

  def _onMessage(self, headers, message):
    try:
      self.recieveFunction(internalDestination=headers["destination"], body=message)
    except Exception as excepti:
      self.thrownException = MqClientThreadHealthCheckExceptionClass("Exception thrown in stomp")
      raise excepti

  def sendStringMessage(self, internalDestination, body):
    if self.closed:
      raise MqClientExceptionClass("Trying to send message on closed STOMP connection")
    self._connectIfNeeded()
    self.stompConnection.send(body=body, destination=internalDestination)

  def registerSubscription(self, internalDestination):
    self._connectIfNeeded()
    if len(self.registeredSubscriptions) == 0:
      self.stompConnection.set_listener(
        '',
        StompConnectionListenerClass(
          messageFunction=self._onMessage,
          disconnectedFunction=self._onDisconnected,
          errorFunction = self._onError
        )
      )
    self.registeredSubscriptions.append(internalDestination)
    self.stompConnection.subscribe(destination=internalDestination, id=1, ack='auto')


  def close(self, wait):
    self.closed = True
    self.stompConnection.disconnect()

  def healthCheck(self):
    if self.thrownException is not None:
      raise self.thrownException