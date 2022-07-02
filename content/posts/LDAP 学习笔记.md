---
title: "LDAP 学习笔记"
date: 2018-05-14T00:00:00+08:00
draft: false
tags: ['ldap','note']
categories: ['note']
author: "X1r0z"

# weight: 1  # Top page

# You can also close(false) or open(true) something for this content.
# P.S. comment can only be closed
comment: false
toc: false
autoCollapseToc: false
---

LDAP: Lightweight Directory Access Protocol 轻量级目录访问协议.

<!--more-->

ldap 用树状结构存储数据, 类似于电话簿, 也能作为类似于 windows 的域环境.

Microsoft Active Directory 为 LDAP 的具体实现.

# 概念

在 ldap 中, 每一条数据都是由 dn 组成的.

**dn: 数据唯一标识符**

由于树状结构, 排在最上面的根就叫 基准 dn.

**基准 dn: 树状结构的最顶部**

```
dc=domain,dc=com
ou=hr,dc=domain,dc=com
uid=Alice,ou=hr,dc=domain,dc=com
```

其中 `dc=domain,dc=com` 为基准 dn.

像 `dc ou uid` 这些叫作 dn 的属性.

```
cn - 常用名称
dc - 域名成分
o - 组织名称
ou - 组织单位
uid - 用户标识
sn - 用户姓名
```

dc 为公司域名, o 可作为公司名称, ou 则为公司里的部门, cn 为一些管理账户的名称 (例如 ldap manager 的登录名).

其他属性

```
C - 国家名称
ST - 州/省名
L - 地名
STREET - 街道地址
givenName - 用户名
mail - 邮箱地址
telephoneNumber - 电话号码
```

*在 ldap 中 属性不区分大小写*

# objectClass

objectClass 可理解为 dn 的模板, 如 person 类包含 telephoneName sn givenName 等属性.

分类

**结构型: 如 person organizationUnit**
**辅助型: 如 extensibeObject**
**抽象型: 如 top**

```
account
alias
dcobject
domain
ipHost
organization
organizationalRole
organizationalUnit
person
organizationalPerson
inetOrgPerson
residentialPerson
posixAccount
posixGroup
```

其中每个类必需设置的属性

```
account: userid
organization: o
person: cn sn
organizationalPerson: same person
organizationalRole: cn
organizationUnit: ou
posixGroup: cn gidNumber
posixAccount: cn gidNumber homeDirectory uid uidNumber
```

openldap 官网上没找到详细的资料, 不过 classObject 的详细内容可以在 ApacheDirectoryStudio 中看到.

# openldap

常用命令

```
ldapadd
ldapsearch
ldapmodify
ldapdelete
slapcat
```

## ldapadd

添加数据

```
-x 进行简单认证
-D 服务器 dn
-h 目录服务的地址
-w  dn 密码
-f 使用 LDIF 添加条目
```

`ldapadd -x -D "cn=root,dc=domain,dc=com" -w root`

## ldapsearch

查找数据

```
-x 进行简单认证
-D 服务器 dn
-w dn 密码
-b 要查询的根节点
-H 要查询的服务器
```

`ldapsearch -x -D "cn=root,dc=domain,dc=com" -w root -b "dc=domain,dc=com"`

## ldapmodify

修改数据

```
-x 进行简单认证
-D 服务器 dn
-h 目录服务的地址
-w  dn 密码
-f 使用 LDIF 修改条目
```

格式

```
dn: cn=test, ou=managers, dc=dlw, dc=com 
changetype: modify
replace: sn
sn: Test User Modify
```

## ldapdelete

```
-x 进行简单认证
-D 服务器 dn
-h 目录服务的地址
-w  dn 密码
```

`ldapdelete -x -D "cn=root,dc=domain,dc=com" -w root "uid=Alice,ou=hr,dc=domain,dc=com"`

## slapcat

导出数据

```
slapcat -l export.ldif
```

# Other

当使用 ldap 交互式操作时, 需通过 Ctrl+D 提交数据.