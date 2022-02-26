报错：
```python
Traceback (most recent call last):
  File "/Users/wenjiazhai/miniforge3/envs/nlp/lib/python3.8/site-packages/py2neo/client/__init__.py", line 806, in acquire
    cx = self._free_list.popleft()
IndexError: pop from an empty deque

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/Users/wenjiazhai/miniforge3/envs/nlp/lib/python3.8/site-packages/urllib3/connection.py", line 174, in _new_conn
    conn = connection.create_connection(
  File "/Users/wenjiazhai/miniforge3/envs/nlp/lib/python3.8/site-packages/urllib3/util/connection.py", line 95, in create_connection
    raise err
  File "/Users/wenjiazhai/miniforge3/envs/nlp/lib/python3.8/site-packages/urllib3/util/connection.py", line 85, in create_connection
    sock.connect(sa)
ConnectionRefusedError: [Errno 61] Connection refused

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/Users/wenjiazhai/miniforge3/envs/nlp/lib/python3.8/site-packages/urllib3/connectionpool.py", line 703, in urlopen
    httplib_response = self._make_request(
  File "/Users/wenjiazhai/miniforge3/envs/nlp/lib/python3.8/site-packages/urllib3/connectionpool.py", line 398, in _make_request
    conn.request(method, url, **httplib_request_kw)
  File "/Users/wenjiazhai/miniforge3/envs/nlp/lib/python3.8/site-packages/urllib3/connection.py", line 239, in request
    super(HTTPConnection, self).request(method, url, body=body, headers=headers)
  File "/Users/wenjiazhai/miniforge3/envs/nlp/lib/python3.8/http/client.py", line 1256, in request
    self._send_request(method, url, body, headers, encode_chunked)
  File "/Users/wenjiazhai/miniforge3/envs/nlp/lib/python3.8/http/client.py", line 1302, in _send_request
    self.endheaders(body, encode_chunked=encode_chunked)
  File "/Users/wenjiazhai/miniforge3/envs/nlp/lib/python3.8/http/client.py", line 1251, in endheaders
    self._send_output(message_body, encode_chunked=encode_chunked)
  File "/Users/wenjiazhai/miniforge3/envs/nlp/lib/python3.8/http/client.py", line 1011, in _send_output
    self.send(msg)
  File "/Users/wenjiazhai/miniforge3/envs/nlp/lib/python3.8/http/client.py", line 951, in send
    self.connect()
  File "/Users/wenjiazhai/miniforge3/envs/nlp/lib/python3.8/site-packages/urllib3/connection.py", line 205, in connect
    conn = self._new_conn()
  File "/Users/wenjiazhai/miniforge3/envs/nlp/lib/python3.8/site-packages/urllib3/connection.py", line 186, in _new_conn
    raise NewConnectionError(
urllib3.exceptions.NewConnectionError: <urllib3.connection.HTTPConnection object at 0x119eb8b20>: Failed to establish a new connection: [Errno 61] Connection refused

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/Users/wenjiazhai/miniforge3/envs/nlp/lib/python3.8/site-packages/py2neo/client/http.py", line 63, in open
    http._hello(user_agent or http_user_agent())
  File "/Users/wenjiazhai/miniforge3/envs/nlp/lib/python3.8/site-packages/py2neo/client/http.py", line 110, in _hello
    r = self.http_pool.request(method="GET",
  File "/Users/wenjiazhai/miniforge3/envs/nlp/lib/python3.8/site-packages/urllib3/request.py", line 74, in request
    return self.request_encode_url(
  File "/Users/wenjiazhai/miniforge3/envs/nlp/lib/python3.8/site-packages/urllib3/request.py", line 96, in request_encode_url
    return self.urlopen(method, url, **extra_kw)
  File "/Users/wenjiazhai/miniforge3/envs/nlp/lib/python3.8/site-packages/urllib3/connectionpool.py", line 813, in urlopen
    return self.urlopen(
  File "/Users/wenjiazhai/miniforge3/envs/nlp/lib/python3.8/site-packages/urllib3/connectionpool.py", line 813, in urlopen
    return self.urlopen(
  File "/Users/wenjiazhai/miniforge3/envs/nlp/lib/python3.8/site-packages/urllib3/connectionpool.py", line 813, in urlopen
    return self.urlopen(
  File "/Users/wenjiazhai/miniforge3/envs/nlp/lib/python3.8/site-packages/urllib3/connectionpool.py", line 785, in urlopen
    retries = retries.increment(
  File "/Users/wenjiazhai/miniforge3/envs/nlp/lib/python3.8/site-packages/urllib3/util/retry.py", line 592, in increment
    raise MaxRetryError(_pool, url, error or ResponseError(cause))
urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='localhost', port=7474): Max retries exceeded with url: / (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x119eb8b20>: Failed to establish a new connection: [Errno 61] Connection refused'))

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/Users/wenjiazhai/Documents/GitHub/badouai-tujiban/07-翟文嘉-南京/week_13/build_graph.py", line 12, in <module>
    graph = Graph("http://localhost:7474",auth=("neo4j","demo"))
  File "/Users/wenjiazhai/miniforge3/envs/nlp/lib/python3.8/site-packages/py2neo/database.py", line 288, in __init__
    self.service = GraphService(profile, **settings)
  File "/Users/wenjiazhai/miniforge3/envs/nlp/lib/python3.8/site-packages/py2neo/database.py", line 119, in __init__
    self._connector = Connector(profile, **connector_settings)
  File "/Users/wenjiazhai/miniforge3/envs/nlp/lib/python3.8/site-packages/py2neo/client/__init__.py", line 960, in __init__
    self._add_pools(*self._initial_routers)
  File "/Users/wenjiazhai/miniforge3/envs/nlp/lib/python3.8/site-packages/py2neo/client/__init__.py", line 982, in _add_pools
    pool = ConnectionPool.open(
  File "/Users/wenjiazhai/miniforge3/envs/nlp/lib/python3.8/site-packages/py2neo/client/__init__.py", line 649, in open
    seeds = [pool.acquire() for _ in range(init_size or cls.default_init_size)]
  File "/Users/wenjiazhai/miniforge3/envs/nlp/lib/python3.8/site-packages/py2neo/client/__init__.py", line 649, in <listcomp>
    seeds = [pool.acquire() for _ in range(init_size or cls.default_init_size)]
  File "/Users/wenjiazhai/miniforge3/envs/nlp/lib/python3.8/site-packages/py2neo/client/__init__.py", line 813, in acquire
    cx = self._connect()
  File "/Users/wenjiazhai/miniforge3/envs/nlp/lib/python3.8/site-packages/py2neo/client/__init__.py", line 764, in _connect
    cx = Connection.open(self.profile, user_agent=self.user_agent,
  File "/Users/wenjiazhai/miniforge3/envs/nlp/lib/python3.8/site-packages/py2neo/client/__init__.py", line 178, in open
    return HTTP.open(profile, user_agent=user_agent,
  File "/Users/wenjiazhai/miniforge3/envs/nlp/lib/python3.8/site-packages/py2neo/client/http.py", line 66, in open
    raise_from(ConnectionUnavailable("Cannot open connection to %r", profile), error)
  File "<string>", line 3, in raise_from
py2neo.errors.ConnectionUnavailable: ('Cannot open connection to %r', ConnectionProfile('http://localhost:7474'))
```
设置 Java 环境从来没有成功过。。。