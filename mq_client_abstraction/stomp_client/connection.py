import stomp
import ssl

class ConnectionClass():
  fullConnectionDetails = None # includes username and password
  stompConnection = None

  def __init__(self, fullConnectionDetails):
    self.fullConnectionDetails = fullConnectionDetails

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
    raise Exception("TODO")
