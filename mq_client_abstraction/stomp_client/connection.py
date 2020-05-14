import stomp
import ssl
from ..clientBase import MqClientExceptionClass, MqClientThreadHealthCheckExceptionClass
from .stompConnectionListener import StompConnectionListenerClass
import time
import threading
import uuid

class registeredSubscriptionClass():
  internalDestination = None
  prefetchSize = None
  id = None
  def __init__(self, internalDestination, prefetchSize):
    self.internalDestination = internalDestination
    self.prefetchSize = prefetchSize
    self.id = str(uuid.uuid4())
  def subscribeToStompConnection(self, stompConnection):
    print("STOMP subscribeToStompDestination - " + self.internalDestination)
    stompConnection.subscribe(destination=self.internalDestination, id=self.id, ack='client-individual', headers={'activemq.prefetchSize': self.prefetchSize})


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

  _connectIfNeededLock = None
  _onDisconnectedInProgress = None

  def __init__(self, fullConnectionDetails, recieveFunction, reconnectMaxRetries, reconectInitialSecondsBetweenTries, reconnectFadeoffFactor, description="Initial"):
    self._connectIfNeededLock = threading.Lock()
    self.closed = False
    self.fullConnectionDetails = fullConnectionDetails
    self.recieveFunction = recieveFunction
    self.registeredSubscriptions = {}
    self.connected = False
    self.thrownException = None
    self.reconnectMaxRetries = reconnectMaxRetries
    self.reconectInitialSecondsBetweenTries = reconectInitialSecondsBetweenTries
    self.reconnectFadeoffFactor = reconnectFadeoffFactor
    self.stompConnection = None
    self._onDisconnectedInProgress = False

    self._connectIfNeeded(description=description)

  def log(self, string):
    print("STOMP connection: " + string)

  def _connectIfNeeded(self, description):
    self.log("connectIfNeeded start (" + description + ")")
    self._connectIfNeededLock.acquire(blocking=True, timeout=-1)
    if self.connected:
      self.log("connectIfNeeded already connected(" + description + ")")
      self._connectIfNeededLock.release()
      return
    self.stompConnection = stomp.Connection(
      host_and_ports=[
        (self.fullConnectionDetails["FormattedConnectionDetails"]["Url"], self.fullConnectionDetails["FormattedConnectionDetails"]["Port"])
      ],
      heartbeats=(4000, 4000) #heartbeats every 4 seconds
    )
    if self.fullConnectionDetails["FormattedConnectionDetails"]["Protocol"] == "stomp":
      pass
    elif self.fullConnectionDetails["FormattedConnectionDetails"]["Protocol"] == "stomp+ssl":
      self.stompConnection.set_ssl(
        for_hosts=[(self.fullConnectionDetails["FormattedConnectionDetails"]["Url"],
                    self.fullConnectionDetails["FormattedConnectionDetails"]["Port"])],
        ssl_version=ssl.PROTOCOL_TLSv1_2)
    else:
      self._connectIfNeededLock.release()
      raise Exception("Unknown protocol")

    self.stompConnection.connect(
      self.fullConnectionDetails["Username"],
      self.fullConnectionDetails["Password"],
      wait=True
    )
    print("STOMP Connection successful " + description)
    self.connected = True
    self._connectIfNeededLock.release()

  def retryWrapperAround_connectIfNeeded(self, description):
    retriesRemaining = self.reconnectMaxRetries
    secondsBetweenTries = self.reconectInitialSecondsBetweenTries
    while not self.connected:
      exeptionRaised = None
      try:
        self._connectIfNeeded(description=description)
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
    if self._onDisconnectedInProgress:
      return
    self._onDisconnectedInProgress = True
    try:
      self.log("onDisconnected")
      if self.closed:
        self.log("onDisconnected - closing so ignored")
        self._onDisconnectedInProgress = False
        return
      self._connectIfNeededLock.acquire(blocking=True, timeout=-1)
      self.connected = False
      self.stompConnection.disconnect()
      self.stompConnection = None
      self._connectIfNeededLock.release()
      # If we have subscribers then we must reconnect and register all the subscriptions again
      #  otherwise we cna wait and only reconnect when sendStringMessage or registerSubscription is called
      if len(self.registeredSubscriptions) == 0:
        self.log("onDisconnected - no subscriptions so not reconnecting at this point")
        self._onDisconnectedInProgress = False
        return

      self.log("onDisconnected - There are subscriptions so re-connection is needed")
      self.retryWrapperAround_connectIfNeeded(description="_onDisconnected")

      #now we have connected re-register all subscriptions on new connection
      self.log("onDisconnected - Resubscribing")
      for internalDestination in self.registeredSubscriptions:
        self.registeredSubscriptions[internalDestination].subscribeToStompConnection(self.stompConnection)
        self._onDisconnectedInProgress = False
    except Exception as excepti:
      self.thrownException = MqClientThreadHealthCheckExceptionClass("Exception thrown in stomp")
      raise excepti
    finally:
      self._onDisconnectedInProgress = False

  def _onMessage(self, headers, message):
    registeredSubscription = None
    if headers["destination"] in self.registeredSubscriptions:
      registeredSubscription =  self.registeredSubscriptions[headers["destination"] ]
    else:
      raise Exception("_onMessage called with destination not registered " + headers["destination"])

    #print("_onMessage", headers, message)

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
    self._connectIfNeeded(description="sendStringMessage")
    #Sometimes stomp.exception.NotConnectedException is thrown in following commnad
    try:
      self.stompConnection.send(body=body, destination=internalDestination)
    except stomp.exception.NotConnectedException:
      print("Got stomp.exception.NotConnectedException but on disconnect was never called - trying one more time")
      self._connectIfNeededLock.acquire(blocking=True, timeout=-1)
      self.connected = False
      self.stompConnection.disconnect()
      self.stompConnection = None
      self._connectIfNeededLock.release()
      self._connectIfNeeded(description="sendStringMessageRETRY")
      self.stompConnection.send(body=body, destination=internalDestination)

  def registerSubscription(self, internalDestination, prefetchSize):
    self._connectIfNeeded(description="registerSubscription")
    if len(self.registeredSubscriptions) == 0:
      ##print("registerSubscription - registeringNEW subscription")
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
    self.stompConnection = None

  def healthCheck(self):
    if self.thrownException is not None:
      raise self.thrownException