---
title: "Typecho Writeup"
date: 2018-03-17T00:00:00+08:00
draft: false
tags: ['php','ctf']
categories: ['web']
author: "X1r0z"

# weight: 1  # Top page

# You can also close(false) or open(true) something for this content.
# P.S. comment can only be closed
comment: false
toc: false
autoCollapseToc: false
---

之前无聊搭的靶机 挺好玩的

也有人拿到了 flag

<!--more-->

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/03/17/1521252538.jpg)

这里有两个切入点 社工 和 vim

## 社工

关于界面

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/03/17/1521252540.jpg)

这里我特地写出 xiaoming 和 vim 两个关键字

主页也有关于 vim 的文章

密码组合一下 xiaominglovevim

## vim

提示已经很明显了

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/03/17/1521252542.jpg)

vim 意外退出会产生 `.[文件名].swp` 的缓存文件

typecho 配置文件 config.inc.php

访问 .config.inc.php.swp 直接下载

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/03/17/1521252544.jpg)

之后就是登录 phpmyadmin insert 或者 update 管理员表

## getshell

后台拿 shell 并没有那么难

我把 编辑主题 插件管理 文件管理 相关的文件都删掉了

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/03/17/1521252546.jpg)

后台能添加上传后缀

php php5 添加后都不能上传成功

而 phtml 可以

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/03/17/1521252548.jpg)

但上传也是有坑的

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/03/17/1521252550.jpg)

这里的代码 让你即使上传了 phtml 文件也不知道路径

但能上传图片并返回路径

思路就有了

`上传图片 –> 上传 phtml –> 再上传图片`

通过两个图片的文件名可以爆破出 phtml 的路径

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/03/17/1521252552.jpg)

拿到 shell 后 flag.php

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/03/17/1521252556.jpg)

AES 加密

密钥

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/03/17/1521252554.jpg)

base64 解密后为 fuckyouflag

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/03/17/1521252558.jpg)