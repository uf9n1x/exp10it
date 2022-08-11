---
title: "Django 快速入门"
date: 2018-08-28T00:00:00+08:00
draft: false
author: "X1r0z"

tags: ['python','django']
categories: ['web']

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


Django 是基于 Python 的 MVC 式 Web 框架.

与其它框架不同的是, Django 为 MVT 设计模式, M 为 Model, 负责对数据库结构的封装, V 为 View, 负责程序的主要操作, T 为 Template, 负责前端内容的输出.

不会讲太多, 文章面向那些想立即用 Django 快速开发一个网站/博客的朋友.

<!--more-->

## 版本

Django 不同的版本的语法和支持的环境几乎都有一些差异,例如路由的写法在 1.x 和 2.x 中就有很大区别.

目前常用的版本如下.

```
1.8.x: 支持 Python 2.7 3.2-3.5 LTS
1.11.x 支持 Python 2.7 3.4-3.6 LTS
2.0.x 支持 Python 3.4-3.7
```

我这里使用的是 1.11.x 版本.

## 开始

创建项目.

`django-admin startproject <PROJECT_NAME>`

如果不出意外的话当前目录下会多出一个文件夹, 结构如下.

```
project
├── manage.py
└── project
    ├── __init__.py
    ├── settings.py
    ├── urls.py
    └── wsgi.py
```

`manage.py` 相当于当前项目下的 `django-admin`

`settings.py` 保存着项目的设置, `urls.py` 为路由规则, `wsgi.py` 在部署项目到生产环境的时候会用到.

再创建应用, 一个项目中会有多个应用存在.

`manage.py startapp proj`

应用结构.

```
proj
├── admin.py
├── apps.py
├── __init__.py
├── migrations
│   └── __init__.py
├── models.py
├── tests.py
└── views.py
```

`admin.py` 配置 Django 后台的功能, `apps.py` 为当前应用的设置, `migrations` 文件夹保存数据库结构更改的记录.

`models.py` 为模型, `views.py` 为视图, `test.py` 一般不会用到.

先在项目的 `settings.py` 中加上当前 app 的名称.

```
INSTALLED_APPS = [
    ......
    'proj',
]
```

在 `views.py` 添加如下代码.

```
from django.shortcuts import HttpResponse

def index(request):
    return HttpResponse('<h1>helloworld</h1>')
```

最后配置路由.

```
from django.conf.urls import url
from django.contrib import admin
from proj import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.index),
]
```

启动服务器.

`manage.py runserver`

helloworld :)

## 视图

视图在 `views.py` 中, 每一个函数对应着一个或多个操作.

```
def index(request):
  return HttpResponse('index')
```

request 相当于 PHP 中的 `$_GET` `$_POST` `$_SESSION` `$_COOKIE` 和 `$_SERVER` 的集合

利用 request 接受各种参数.

```
request.GET.get('arg')
request.POST.get('form')
request.REQUEST.get('all')
```

获取和设置 cookie session.

```
request.COOKIES['a'] = 'b'
request.SESSION['c'] = 'd'
request.COOKIES.get('a')
request.SESSION.get('c')
```

获取客户端信息.

```
request.META.get('HTTP_USERAGENT')
request.META.get('REMOTE_ADDR')
```

其中还有像 `request.GET['arg']` 这种方式获取数据, 不过数据不存在的时候会报错.

`HttpResponse` 返回 response.

`HttpResponseRedirect` 页面跳转.

## 路由

路由在 `urls.py` 中, 1.11.x 使用正则表达式编写路由规则.

```
from django.conf.urls import url
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
]
```

`urlpatterns` 保存 `url` 对象, 实例化时传入正则和视图.

先引入当前 app 的包, 这样才能在路由中添加 app 中的视图函数.

各种路由.

```
url('^index', views.index)
url('^login', views.login)
```

去除末尾的斜杠.

```
url('^user/?', views.user)
url('^cart/?', views.cart)
```

pathinfo 风格传参.

```
url('^add/(.*)?/(.*)?', views.add)
```

视图函数.

```
def add(request,a,b):
    return HttpResponse(a+':'+b)
```

## 模板

直接使用 `HttpResponse` 返回显得丑丑哒, django 使用 `render` 渲染模板.

在 app 目录下新建 `templates` 文件夹和 `index.html`

内容如下.

```
<h1> {{ message }} </h1>
```

`views.py`

```
def index(request):
    return render(request, 'index.html', {'message': 'helloworld'})
```

render 第一个参数默认为 request, 第二个为模板名称, 第三个为字典, 给模板传递内容.

django 的模板语法中, 使用两对大括号输出变量内容, 一对大括号和一对百分号进行 if for 等操作

各种模板.

if

```
{% if a > 5 %}
<strong> {{ a }} </storng>
{% endif %}

{% if islogin %}
<b> Welcome {{ name }} </b>
{% else %}
<b> Login
{% endif %}
```

for

```
<ul>
{% for a in list %}
<li> {{ forloop.counter }}.{{ a }} </li>
{% endfor %}
</ul>

{% for k,v in dict.items %}
<i>{{ k }}<i>: {{ v }}
```

模板还有过滤器, 如获取列表长度 `list|length`, 具体请到 Django 官方文档中查询.

## 模型

模型在 `models.py` 中, 每一个 Class 对应着数据中的一张表, Class 的属性则为表中的字段.

```
from django.db import models

class User(models.Model):
    age = models.IntegerField()
    username = models.CharField(max_length=16)
    password = models.CharField(max_length=32)
    email = models.EmailField(max_length=32)
    blog = models.UrlField(max_length=32,blank=True)
    isguy = models.BooleanField(default=True)
    regtime = models.DateTimeField(auto_now_add=True)
    info = models.TextField(blank=True)
```

不同的 Field 存放不同类型的数据, `IntegerField` 为数字, `CharField` 为字符串, `EmailField` 为邮箱地址, `UrlField` 为 url, `BooleanField` 为布尔值, `DateTimeField` 为日期, `TextField` 为长文本.

Field 中还有不同的参数, `max_length` 为最大长度, `blank` 是否为空, `default` 指定默认值.

全部的 Field 以及可用的参数请到 Django 官方文档中查询.

操作数据的几种方式, 首先在 `views.py` 中引入 model.

`from proj.models import User`

推荐在 shell 中进行数据操作.

`manage.py shell`

查询.

```
Uer.objects.get(username='admin').age
res = Uer.objects.get(username='admin')
res.username

User.objects.filter(username='admin')
res = User.objects.filter(username='test')
res.filter(isguy=True)

res = User.objects.filter(username='123').first()
res.email
```

get 获取到的结果在一条以上时会报错, 而 filter 不会, 但 filter 获取只有一条数据的时候结构仍为 QuerySet (类似于 list), 需要指定 `.first()` 或者 `.last()` 才能像 get 一样进行操作.

插入.

```
User.objects.create(username='abc',password='abc')

user = User(username='abc',password='abc')
user.save()

user = User()
user.username = 'abc'
user.password = 'abc'
user.save()
```

更新.

```
User.objects.filter(username='admin').update(isguy=True)

res = User.objects.filter(username='admin')
res.update(isguy=True)

user = User.objects.get(username='admin')
user.isguy = True
user.save()

User.objects.all().update(isguy=True)
```

删除.

```
User.objects.filter(username='admin').delete()

res = User.objects.filter(username='admin')
res.delete()

User.objects.all().delete()
```

切片.

```
User.objects.filter(age=1)[:10]

User.objects.all()[:5]
```

还有一些字段名加双下划线的表示特定条件的字段, 如 `age__lt` 和 `age__gt` 表示 age 小于某数和 age 大于某数.

具体请到 Django 官方文档中查询.

## 后台

后台在 `admin.py` 中, 路由默认为 `^admin/`

创建后台用户.

`mange.py createsuperuser`

密码需大于 8 位.

默认的后台全是 `Query Object` 而且只显示一个字段, 需要手动修改下.

先在 models 中每一个 class 中加入如下内容.

```
def __unicode__(self):
  return self.username
```

3.x 为 `__str__`, 主要修改原在后台中显示的 `Quert Object`

修改 `admin.py`

```
from django.contrib import admin
from proj.models import User

class adminUser(admin.ModelAdmin):
	list_display = ('username', 'email', 'age', 'isguy', 'regtime')

admin.site.register(User, adminUser)
```

`adminUser` 类修改后台中显示的字段, 最后需要把 model 注册到 admin 中.

还有美化 添加功能等方面, 不过听说 django 默认的后台并不安全.

## 部署

django 默认的项目 DEBUG 模式为 True, 这将导致路由 源码 异常等信息都会出现在客户端, 而且在生产环境下 django 的 runserver 的性能差的一批.

这里使用的是 `nginx + uwsgi` 方式进行项目的部署.

先在 `settings.py` 中设置 `DEBUG = False`

在项目目录下添加 uwsgi.ini

```
[uwsgi]
socket = :8000
chdir = /home/exp10it/project
wsgi-file = /project/wsgi.py
module =bugscan.wsgi
master = true
processes = 4
vacuum = true
pidfile=uwsgi.pid
daemonize=uwsgi.log
```

启动.

`uwsgi --ini uwsgi.ini`

在 nginx 配置文件的 http 中加入如下内容.

```
upstream django {
    server 127.0.0.1:8000;
}

server {
    listen  8082;

    location /static {
        alias /home/exp10it/project/static;
    }

    location / {
        uwsgi_pass django;
        include uwsgi_params;
    }
}
```

最后启动 nginx, 访问本机 8082 端口即可.

## 其它

关于静态文件, 最好的方法就是像部署时 nginx 配置文件中的那样 alias.

至于用户的媒体文件, 在 app 目录中添加 media 文件并修改 `settings.py` 文件, 最后 nginx alias 即可.

django 默认的 csrf 防护需要在模板中添加 `csrf_token`, 不想使用的话可在 `setting.py` 的 `MIDDLEWARE` 中注释掉 `django.middleware.csrf.CsrfViewMiddleware`

django 的 cookie 默认 httponly.

django 的模板自带 xss filter.