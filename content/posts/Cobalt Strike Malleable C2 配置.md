---
title: "Cobalt Strike Malleable C2 配置"
date: 2019-08-13T00:00:00+08:00
draft: false
author: "X1r0z"

tags: ['cobalt strike']
categories: ['内网渗透']

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


Malleable C2 是 Cobalt Strike 的一项功能, 意为 "可定制的" 的 C2 服务器. Malleable C2 允许我们仅通过一个简单的配置文件来改变 Beacon 与 C2 通信时的流量特征与行为.

<!--more-->

## 配置示例

一个简单的 HTTP Malleable C2 Profile.

```
set sample_name "my";
set sleeptime "5000";
set tcp_port "7001";
set useragent "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36";

http-get {

	set uri "/jquery.min.js";

	client {

		header "Accept-Language" "zh-CN,zh;q=0.9,en;q=0.8";
		parameter "ver" "1.2.4";

		metadata {

			base64;
			prepend "token=";
			header "Cookie";

		}

	}

	server {

		header "Server" "Apache/2.4.39 (Unix)";
		header "Content-Type" "application/javascript; charset=utf-8";

		output {

			base64;
			prepend "/*! jQuery v2.1.3 | (c) 2005, 2014 jQuery Foundation, Inc. | jquery.org/license */!function(a,b){\"object\"==typeof module&&\"object\"==typeof module.exports?module.exports=a.document?b(a,!0):function(a)";
			append "var nc=a.jQuery,oc=a.$;return n.noConflict=function(b){return a.$===n&&(a.$=oc),b&&a.jQuery===n&&(a.jQuery=nc),n},b||(a.jQuery=a.$=n),n});";
			print;

		}
	}
}

http-post {

	set uri "/wp-admin";

	client {

		header "Accept-Language" "zh-CN,zh;q=0.9,en;q=0.8";
		header "Cookie" "wordpress_test_cookie=WP+Cookie+check";

		id {

			base64;
			prepend "PHPSESSID=";
			header "Cookie";
		
		}

		output {

			base64;
			print;

		}
	}

	server {

		header "Server" "Apache/2.4.39 (Unix)";
		header "Content-Type" "text/html; charset=UTF-8";

		output {

			base64;
			print;

		}
	}
}

http-stager {

	set uri_x86 "/favicon1.ico";
	set uri_x64 "/favicon2.ico";

	client {

		header "Accept-Language" "zh-CN,zh;q=0.9,en;q=0.8";

	}

	server {

		header "Server" "Apache/2.4.39 (Unix)";
		header "Content-Type" "image/x-icon";

		output {

			print;

		}
	}
}
```

下面将会基于这个配置文件依次进行讲解.

但先来看看这个配置文件做了什么. 以 http-get 为例, 该代码块仅对通信过程中的 GET 请求有效.

```
http-get {

	set uri "/jquery.min.js";

	client {

		header "Accept-Language" "zh-CN,zh;q=0.9,en;q=0.8";
    	parameter "ver" "1.2.4";

		metadata {

			base64;
			prepend "token=";
			header "Cookie";

		}

	}

	server {

		header "Server" "Apache/2.4.39 (Unix)";
		header "Content-Type" "application/javascript; charset=utf-8";

		output {

			base64;
			prepend "/*! jQuery v2.1.3 | (c) 2005, 2014 jQuery Foundation, Inc. | jquery.org/license */!function(a,b){\"object\"==typeof module&&\"object\"==typeof module.exports?module.exports=a.document?b(a,!0):function(a)";
			append "var nc=a.jQuery,oc=a.$;return n.noConflict=function(b){return a.$===n&&(a.$=oc),b&&a.jQuery===n&&(a.jQuery=nc),n},b||(a.jQuery=a.$=n),n});"
			print;

		}
	}
}
```

http-get 中分为 client 和 server 两大块, 分别针对 Beacon 发送的请求和 C2 响应的内容进行修改.

首先我们指定了参数 `uri` 为 `/jquery.min.js`, 表示通信时请求的 URL 地址.

在 client 块里, 我们在请求头中添加了 `Accept-Language` 字段, 对要发送的 Metadata 进行 base64 编码并拼接字符串, 然后将数据存放在 HTTP 头中, 其内容为 `Cookie: token=BASE64_ENCODED_DATA` , 最终发送至 C2.

在 server 块里, 我们在响应头中添加了 `Server` 和 `Content-Type` 字段, 在响应内容的前后加上 jQuery 代码, 最后进行 base64 编码并响应在 HTTP Body 里.

## 通信过程

在此之前. 我觉得有必要了解一下 Beacon 与 C2 的通信过程.

当 Beacon 被执行后, 会在 C2 上下载载荷执行, 即 Stage 过程, Stageless 则省去了这一步.

之后, Beacon 根据设置的睡眠时间进入睡眠状态, 结束后向 C2 发送有关 Beacon 的信息如系统类型, 版本, 当前用户, 称之为 Metadata.

如果存在待执行的任务, C2 就会响应发送 Metadata 的请求, Beacon 将会收到有关 Task 的具体内容和唯一的 Task ID, 并依次执行任务.

执行完毕后, Beacon 将各 Task 回显的数据与对应的 Task ID 依次上传至 C2, 然后再次进入睡眠状态.

其中 Beacon 发送 Metadata 时一般使用 GET, 上传回显数据时使用 POST.

## 代码结构

我们对于流量特征的修改都是在指定的代码块中进行的, 以下是上文中的代码块.

```
http-get {

	client {

		metadata {

		}

	}

	server {

		output {

		}
	}
}


http-post {

	client {

		id {
		
		}

		output {

		}
	}

	server {

		output {

		}
	}
}


http-stager {

	client {

	}

	server {

		output {

		}
	}
}

```

可以看到, 代码块按 HTTP 请求分为 http-get http-post 两种, 以及被单独列出来的 http-stager 用于 stage 过程.

按照对象分为 client 和 server, 按照不同的通信步骤分为 metadata id 和 output.

这里 client 和 server 恰好都有 output 块, 可能会有点不理解. 简要说明一下, Beacon 在上传 Task 数据时是需要对应的 Task ID 的, id 块正好是针对 Task ID 的修改, output 块则是修改通过 POST 发送的数据, 而 server 中的 output 块仅仅是用于修改响应内容的, 不要弄混了.

## 语句与参数

### 自定义参数

在之前的代码中, 我们在开头指定了一些自定义参数.

```
set sample_name "my";
set sleeptime "5000";
set tcp_port "7001";
set useragent "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36";
```

这些是作用于全局的参数, 统一的语法为 `set key "value"` 且后面需要加上分号, 字符串仅能使用双引号表示.

另外可以通过反斜杠来表示特殊字符, 例如 `\n`, `\r`, `\t`, `\"`, `\\`, Unicode 字符 `\u123` 和Hex 字符 `\x123`.

参数很简单, 就不再细说了, `sleeptime` 的单位是毫秒. 需要注意的是 `tcp_port`. 还记得之前的 Bind TCP Beacon 吗? 通过 `tcp_port` 我们就能够更改目标 Beacon 监听的端口.

而对于这些参数.

```
set uri "/jquery.min.js";
set uri_x86 "/favicon1.ico";
set uri_x64 "/favicon2.ico";
```

则只能放在 http-get http-post 和 http-stager 中.

其中 `uri` 可在 http-get http-post 中指定, 表示通信时请求的 URL, 例如 `/wp-admin`.

`uri_x86` 和 `uri_x64` 是指在不同位数的系统上 stage 过程中所请求的 URL, 两者不能重复. 个人建议在写的的时候也尽量使用二进制文件的路径, 例如 JPG PNG GIF.

### 语句

在 Malleable C2 中, 语句可分为数据转换语句, 终止语句, 额外语句 (Header and Parameter) 三种类型.

数据转换语句有 base64 base64url mask netbios netbiosu prepend append.

终止语句有 print uri-append header parameter.

额外语句有 header parameter.

### 输出位置

首先来讲一下终止语句, 也就是指定传输数据的存放位置. Malleable C2 提供了 4 种方法: print uri-append header parameter, 分别为存放在 HTTP Body, URL, HTTP 头和 GET 参数中.

终止语句只能写进 metadata id output 块, 不能直接放在 client 和 server 里, 而且终止语句的后面不能有其它语句, 也就是说只能放在代码块末尾.

其中 print 和 uri-append 无须指定参数, 后两者的格式为 `header "Cookie"` 和 `parameter "action"`, 即存放位置为 Cookie 字段和 action 参数. 四种方法中只有 print 能够存放长数据.

举个例子.

```
metadata {

	base64;
	prepend "token=";
	header "Cookie";

}
```

上面我们将数据进行 base64 编码, 并在其前面添加 `token=`, 最后存放在 HTTP 头的 Cookie 字段中, 最后的效果为 `Cookie: token=BASE64_ENC_DATA`.

### 编码与加密

还是上面的代码.

```
metadata {

	base64;
	prepend "token=";
	header "Cookie";

}
```

这里的 base64 叫作数据转换语句, 只能写进 metadata id output 块中. 所有的数据转换语句都不需要传参, 但都不能放在 http-stager 块中 (因为那么点 Payload 长度没空间给你写解码函数).

另外还有 base64url mask netbios netbiosu. base64url 编码后的数据是可以放在 URL 中的, mask 为异或加密, 至于 netbios netbiosu 则是在 SMB 传输过程中针对主机名的编码方式.

最后说一个需要注意的点.

```
metadata {

	prepend "token=";
	base64;
	header "Cookie";

}
```

以这种顺序编码的话, 它就会将 `token=` 字符串与数据一起编码, HTTP 字段就会变成 `Cookie: BASE64_ENC_DATA`.

### 伪造与混淆

prepend 和 append 混用.

```
output {

	base64;
	prepend "/*! jQuery v2.1.3 | (c) 2005, 2014 jQuery Foundation, Inc. | jquery.org/license */!function(a,b){\"object\"==typeof module&&\"object\"==typeof module.exports?module.exports=a.document?b(a,!0):function(a)";
	append "var nc=a.jQuery,oc=a.$;return n.noConflict=function(b){return a.$===n&&(a.$=oc),b&&a.jQuery===n&&(a.jQuery=nc),n},b||(a.jQuery=a.$=n),n});"
	print;

}
```

我们通过 base64 加密数据, 并在其前后添加 jQuery 代码, 最终通过 HTTP Body 输出.

其中的 prepend 和 append 是可以放进 http-stager 块的, 两者合理搭配的话能够达到隐蔽的效果. 例如分别插入图片开头和末尾的 blob, 把数据留给中间.

不过除了 prepend append 就没有别的混淆办法了吗? 答案是有的.

```
client {

	set uri "/jQuery.min.js"
	header "Accept-Language" "zh-CN,zh;q=0.9,en;q=0.8";
	parameter "ver" "1.2.4";

}
```

上述代码通过 header 和 parameter 添加用于混淆的 HTTP 头和 GET 参数, 格式为 `header "key" "value"` 和 `parameter "key "value"`, 最终的效果是请求了 `/jQuery.min.js?ver=1.2.4` 这个地址.

注意这里的 header 和 parameter 我称之为额外语句, 与终止语句的不同在于它们的位置不一样. 额外语句只能写进 client 和 server 块, 而不是 metadata id 和 output 块.

## 调试运行

Cobalt Strike 默认给我们了 `c2lint` 用于检查配置文件的语法错误, 同时还能够预览配置后的 HTTP 请求与响应.

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20190813213215.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20190813213243.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20190813213305.png)

通过 teamserver 命令的第三个参数指定配置文件.

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20190813213456.png)

## 一些话

Github 上的 Malleable C2 Profile.

[rsmudge/Malleable-C2-Profiles](https://github.com/rsmudge/Malleable-C2-Profiles)

[threatexpress/malleable-c2](https://github.com/threatexpress/malleable-c2)

这篇文章也只是给 Malleable C2 开了个头, 并没有涉及到什么太过深入的东西. 例如如何自定义命名管道, DNS 传输, 添加证书, 签名等.

加油吧 :)