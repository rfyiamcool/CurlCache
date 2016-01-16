# curlcache

用途很简单，就是针对respone进行cache，暂时是放在本地文件做缓存.

```
from curlcache import QueryCache
url = "http://xiaorui.cc/loction/api"
res = QueryCache()
res.json_query(url)
```
