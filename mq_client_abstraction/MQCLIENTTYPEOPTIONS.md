# MQ Client Type Options

## Memory Client

```
{
  "Type": "Memory"
  "DestinationPrefix": - defaults to empty string
}
```

or expressed as an environment variable:
```
export APIAPP_OBJECTSTORECONFIG="{\"Type\":\"Memory\"}"
```

## Stomp Client

```
{
  "Type": "Stomp",
  "DestinationPrefix":
  "ConnectionString": "", # like stomp+ssl://aaa.mq.xxx.amazonaws.com:61614
  "Usernaame":
  "Password":
  "skipConnectionCheck": defaults to false
  "reconectInitialSecondsBetweenTries" : defaults to 2
  "reconnectFadeoffFactor" defaults to 1.5
  "reconnectMaxRetries": defaults to 9

}
```