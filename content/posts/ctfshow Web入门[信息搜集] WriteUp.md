---
title: "ctfshow Web入门[信息搜集] WriteUp"
date: 2022-07-20T22:07:23+08:00
draft: false
tags: ['ctf','php']
categories: ['web']
author: "X1r0z"

# weight: 1  # Top page

# You can also close(false) or open(true) something for this content.
# P.S. comment can only be closed
comment: false
toc: false
autoCollapseToc: false
---

信息搜集类别, 题目挺简单的, 但是延申的方向很多

<!--more-->

## web1

查看源代码

## web2

js 屏蔽了右键

浏览器 `view-source:` 即可

## web3

抓包

## web4

查看 robots.txt

访问 flagishere.txt

## web5

源代码泄露 `.phps`

网上查了一下, 如果服务器配置正确的话, 访问`.phps` 会显示出代码高亮的 PHP 源码

## web6

目录扫描出来 `www.zip`

下载解压打开得到 flag

## web7

git 源码泄露

访问 `url/.git` 得到 flag

## web8

svn 源码泄露

访问 `url/.svn` 得到 flag

## web9

vim 缓存 格式是 `.filename.swp`

访问 `url/.index.php.swp`

## web10

cookie 抓包得到 flag

## web11

DNS 的 txt 纪录, 一般用来做备注(联系方式) 或者做 SPF (反垃圾邮件)

![20220720210801](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220720210801.png)

也可以用阿里云的在线网站查询 (https://zijian.aliyun.com/)[https://zijian.aliyun.com/]

## web12

需要一点社工的思想

根据之前所学, 查看 robots.txt 得到管理员后台

页面最底下联系电话 372619038 尝试后登录成功

## web13

开发文档泄露

右键查看源码

![20220720211851](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220720211851.png)

发现 document.pdf

![20220720211904](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220720211904.png)

登录得到 flag

## web14

右键源码

![20220720212608](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220720212608.png)

估计有编辑器

访问 /editor 目录

![20220720212637](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220720212637.png)

根据题目说明是存在目录遍历

找到上传附件的功能

![20220720212711](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220720212711.png)

![20220720212720](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220720212720.png)

Linux 下网站目录一般是 /var/www/

![20220720212749](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220720212749.png)

`/nothinghere/fl000g.txt`

访问得到 flag

## web15

邮箱泄露

主页最底下

![20220720213452](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220720213452.png)

1156631961@qq.com

手工尝试 得到后台页面 /admin

![20220720213511](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220720213511.png)

点击忘记密码

![20220720213527](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220720213527.png)

qq 查找好友

![20220720213559](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220720213559.png)

所在地是 西安

重置密码后登录得到 flag

## web16

探针泄露

手头上的扫描器一直没扫出来 (还没怎么更新...)

查看 hint 后才发现是 tz.php

![20220720214300](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220720214300.png)

查看 phpinfo()

![20220720214459](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220720214459.png)

搜索 flag

![20220720214531](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220720214531.png)

## web17

sql 备份泄露

手工得到 `http://1978ef57-62e8-4d10-984f-11b67d9bbbc2.challenge.ctf.show/backup.sql`

![20220720214826](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220720214826.png)

## web18

前端泄露

题目要求游戏达到100分, 但右键查看是 js

![20220720215204](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220720215204.png)

这就是说游戏完全是本地化的

查看 Flappy_js.js, 拉到最底下

![20220720215255](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220720215255.png)

F12 控制台执行

![20220720215316](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220720215316.png)

![20220720215323](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220720215323.png)

访问 110.php 得到 flag

## web19

右键查看源码

![20220720215650](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220720215650.png)

账号 admin 密文 a599ac85a73384ee3219fa684296eaa62667238d608efa81837030bd1ce1bf04

js 前端进行了 AES 加密

密钥 0000000372619038 偏移量 ilove36dverymuch CBC ZeroPadding

注意编码形式是 hex

![20220720215944](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220720215944.png)

登录得到 flag

## web20

access mdb 泄露

访问 /db/db.mdb 打开得到 flag

![20220720220604](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220720220604.png)

## 总结

查看源代码, 抓包, robots.txt, .phps, 备份文件(如www.zip backup.sql)

git svn 泄露, vim 缓存, cookie 修改, DNS TXT 纪录

手机号, 邮箱, 开发文档, 编辑器, 探针, 前端 js 和注释, access mdb