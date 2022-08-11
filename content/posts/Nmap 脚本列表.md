---
title: "Nmap 脚本列表"
date: 2018-02-20T00:00:00+08:00
draft: false
author: "X1r0z"

tags: ['windows','linux']
categories: ['内网渗透']

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


The Nmap Scripting Engine (NSE) is one of Nmap’s most powerful and flexible features.

<!--more-->

## 脚本分类

```
auth: 负责处理鉴权证书(绕开鉴权)的脚本
broadcast: 在局域网内探查更多服务开启状况, 如 dhcp/dns/sqlserver 等服务
brute: 提供暴力破解方式, 针对常见的应用如 http/snmp 等
default: 使用 -sC 或 -A 选项扫描时候默认的脚本, 提供基本脚本扫描能力
discovery: 对网络进行行更多的信息, 如 SMB 枚举 SNMP 查询等
dos: 用于进行拒绝服务攻击
exploit: 利用已知的漏洞入侵系统
external: 利用第三方的数据库或资源, 例如进行 whois 解析
fuzzer: 模糊测试的脚本, 发送异常的包到目标机, 探测出潜在漏洞
intrusive: 入侵性的脚本, 此类脚本可能引发对方的 IDS/IPS 的记录或屏蔽
malware: 探测目标机是否感染了病毒 开启了后门等信息
safe: 此类与 intrusive 相反, 属于安全性脚本
version: 负责增强服务与版本扫描 (Version Detection) 功能的脚本
vuln: 负责检查目标机是否有常见的漏洞 (Vulnerability) , 如是否有 MS08-067
```

## 信息收集

```
ip-getlocation-*
whois
http-email-harvest
hostmap-ip2hosts
dns-brute
membase-http-info
smb-check-vulns
http-stored-xss
http-sql-injection
http-headers
http-sitemap-generator
```

## 数据库

```
mysql-databases
mysql-variables
mysql-empty-password
mysql-brute
oracle-brute
ms-sql-brute
ms-sql-empty-password
ms-sql-tables
ms-sql-xp-cmdshell
pgsql-brute
```

## 渗透测试

```
http-brute
ftp-brute
http-wordpress-brute
http-joomla-brute
pop3-brute
smb-brute
vnc-brute
smtp-brute
snmp-netstat
snmp-processes
snmp-brute
```