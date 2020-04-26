# MQ Client Type Options

## Memory Client

```
{
  "Type": "Memory"
  "destinationPrefix": - defaults to empty string
}
```

or expressed as an environment variable:
```
export APIAPP_OBJECTSTORECONFIG="{\"Type\":\"Memory\"}"
```

## Storm Client

```
{
  "Type": "Storm",
  "destinationPrefix":
  "ConnectionString": "", # like stomp+ssl://aaa.mq.xxx.amazonaws.com:61614
  "usernaame":
  "password":
}
```