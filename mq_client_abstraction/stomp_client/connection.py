import stomp
import ssl
from ..clientBase import MqClientExceptionClass, MqClientThreadHealthCheckExceptionClass
from .stompConnectionListener import StompConnectionListenerClass
import time

class registeredSubscriptionClass():
  internalDestination = None
  prefetchSize = None
  def __init__(self, internalDestination, prefetchSize):
    self.internalDestination = internalDestination
    self.prefetchSize = prefetchSize
  def subscribeToStompConnection(self, stompConnection):
    stompConnection.subscribe(destination=self.internalDestination, id=1, ack='client-individual', headers={'activemq.prefetchSize': self.prefetchSize})


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
    self.registeredSubscriptions = {}
    self.connected = False
    self.thrownException = None
    self.reconnectMaxRetries = reconnectMaxRetries
    self.reconectInitialSecondsBetweenTries = reconectInitialSecondsBetweenTries
    self.reconnectFadeoffFactor = reconnectFadeoffFactor

    self.stompConnection = stomp.Connection(
      host_and_ports=[(self.fullConnectionDetails["FormattedConnectionDetails"]["Url"], self.fullConnectionDetails["FormattedConnectionDetails"]["Port"])]
    )

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
    print("Connection successful")
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
        print("Waiting", secondsBetweenTries, "seconds before next connection attempt (attempts left", retriesRemaining + 1, ")")
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

      #now we have connected re-register all subscriptions on new connection
      for internalDestination in self.registeredSubscriptions:
        self.registeredSubscriptions[internalDestination].subscribeToStompConnection(self.stompConnection)
    except Exception as excepti:
      self.thrownException = MqClientThreadHealthCheckExceptionClass("Exception thrown in stomp")
      raise excepti

  def _onMessage(self, headers, message):
    registeredSubscription = None
    if headers["destination"] in self.registeredSubscriptions:
      registeredSubscription =  self.registeredSubscriptions[headers["destination"] ]
    else:
      raise Exception("_onMessage called with destination not registered " + headers["destination"])

    exceptionRaisedInRecieveFunction = None
    try:
      # Ack the message BEFORE processing
      #  reduces the chance of connection being reset while message is being processed
      self.stompConnection.ack(id=headers["message-id"], subscription=headers["subscription"])
      self.recieveFunction(internalDestination=headers["destination"], body=message)
    except Exception as excepti:
      self.thrownException = MqClientThreadHealthCheckExceptionClass("Exception thrown in stomp recieve function")
      raise excepti

  def sendStringMessage(self, internalDestination, body):
    if self.closed:
      raise MqClientExceptionClass("Trying to send message on closed STOMP connection")
    self._connectIfNeeded()
    self.stompConnection.send(body=body, destination=internalDestination)

  def registerSubscription(self, internalDestination, prefetchSize):
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
    registeredSubscription = registeredSubscriptionClass(internalDestination, prefetchSize)
    self.registeredSubscriptions[internalDestination] = registeredSubscription
    registeredSubscription.subscribeToStompConnection(self.stompConnection)


  def close(self, wait):
    self.closed = True
    self.stompConnection.disconnect()

  def healthCheck(self):
    if self.thrownException is not None:
      raise self.thrownException