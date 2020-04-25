import Common

connectionDetails = Common.getConDetailsFromEnvironment()
conn = Common.StormConnectionClass(connectionDetails)

conn.sendMessage(body="ABC", destination='/queue/test')

conn.close()
