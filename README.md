# Motivation 

Recently I came across such a requirement: I have a Celery program running as background worker, where some of the tasks need to spawn an external process and downgrade to a restricted system account.

Multiple workers are preforked to serve concurrency requests. Most of the tasks do not need such a restricted system account, while only some of them do need. A simple solution is to assign the accounts manually to the workers, where I have to launch the workers one by one with additional parameters in this situation.

This is awful. I want a server to give out these accounts to the workers, only on the demands of the tasks, and get back the accounts when no longer needed.

That's why I created this package, `idserver`. Now it can run an id server, manage a collection of pre-defined ids, and give out them on client requests. The clients must request the ids with an expiration time, after which the ids will be reused. The clients may give back the ids before expiration.

# Restrictions

If the server has no free id, it will not go into blocking, instead it will give the failure to the clients. So it's your duty to retry in a client program.

# Examples

## UDP Server

```python
from idserver import IdPool, UdpIdServer

idp = IdPool('name-%d' % x for x in xrange(10))
svr = UdpIdServer(idp, '127.0.0.1', 9777)
svr.run_forever()
```

## UDP Client

```python
import os
import time
from idserver import UdpIdClient

idc = UdpIdClient('127.0.0.1', 9777)
print idc.acquire('client-%d' % os.getpid(), 10)
time.sleep(1)
idc.release('client-%d' % os.getpid())
```


## TCP Server

TCP Server is available only if `~tornado` is installed.

```python
from idserver import IdPool, TcpIdServer

idp = IdPool('name-%d' % x for x in xrange(10))
svr = TcpIdServer(idp, '127.0.0.1', 9777)
svr.run_forever()
```

## TCP Client

```python
import os
import time
from idserver import TcpIdClient

idc = TcpIdClient('127.0.0.1', 9777)
print idc.acquire('client-%d' % os.getpid(), 10)
time.sleep(1)
idc.release('client-%d' % os.getpid())
```
