import os
import mq_client_abstraction

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

def getMqClient():
  configDict = {
    "Type": "Stomp",
    "Username": getFromEnvironment("RJMACTIVEMQ_USER"),
    "Password": getFromEnvironment("RJMACTIVEMQ_PASS"),
    "ConnectionString": getFromEnvironment("RJMACTIVEMQ_CONNSTR")
  }
  return mq_client_abstraction.createMQClientInstance(configDict=configDict)