---
title: "ISCC 2018 Misc Writeup"
date: 2018-05-20T00:00:00+08:00
draft: false
author: "X1r0z"

tags: ['ctf']
categories: ['Writeup']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

你们 520 在撩妹 而我却在做题

<!--more-->

# What is that?

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/05/23/1527078386.jpg)

png 格式 应该是手指下面有 flag

拖进 tweakpng

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/05/23/1527078387.jpg)

CRC 报错 可能更改了图片宽度 or 高度

winhex 修改

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/05/23/1527078388.jpg)

查看

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/05/23/1527078390.jpg)

# 数字密文

`69742773206561737921`

hex 编码 解码即可

`it's easy!`

# 秘密电报

`ABAAAABABBABAAAABABAAABAAABAAABAABAAAABAAAABA`

培根密码

`ilikeiscc`

提交注意大写

# 重重谍影

```
Vm0wd2QyVkZOVWRXV0doVlYwZG9WVll3WkRSV2JGbDNXa1JTVjAxWGVGWlZNakExVjBaS2RHVkljRnBXVm5CUVZqQmtTMUl4VG5OaFJtUlhaV3RHTkZkWGRHdFRNVXB6V2toV2FsSnNjRmhhVjNoaFYxWmFjMWt6YUZSTlZtdzBWVEo0YzJGR1NuTlhiR2hYWVd0d2RsUnRlR3RqYkdSMFVteFdUbFp0ZHpCV2EyTXhVekZSZUZkc1ZsZGhlbXhoVm01d1IyTldjRVZTYlVacVZtdHdlbGRyVlRWVk1ERldZMFZ3VjJKR2NIWlpWRXBIVWpGT1dXSkhhRlJTVlhCWFZtMDFkMUl3TlhOVmJGcFlZbGhTV1ZWcVFURlRWbEY0VjIxR2FGWnNjSGxaYWs1clZqSkdjbUo2UWxwV1JWcDZWbXBHVDJNeGNFaGpSazVZVWxWd1dWWnRNVEJXTVUxNFdrVmtWbUpHV2xSWlZFNVRWVVpzYzFadVpGUmlSbHBaVkZaU1ExWlhSalpTYTJSWFlsaENVRll3V21Gak1XUnpZVWRHVTFKV2NGRldha0poV1ZkU1YxWnVTbEJXYldoVVZGUktiMDB4V25OYVJFSm9UVlpXTlZaSE5VOVdiVXB5WTBaYVdtRXhjRE5aTW5oVFZqRmFkRkpzWkU1V2JGa3dWbXhrTUdFeVJraFRiRnBYWVd4d1dGWnFUbE5YUmxsNVRWVmFiRkp0VW5wWlZWcFhZVlpLZFZGdWJGZGlXRUpJV1ZSS1QxWXhTblZWYlhoVFlYcFdWVmRYZUZOamF6RkhWMjVTYWxKWVVrOVZiVEUwVjBaYVNFNVZPVmRXYlZKS1ZWZDRhMWRzV2taWGEzaFhUVlp3V0ZwR1pFOVRSVFZZWlVkc1UyRXpRbHBXYWtvd1lURkplRmR1U2s1V1ZscHdWVzB4VTFac1duUk5WazVPVFZkU1dGZHJWbXRoYXpGeVRsVndWbFl6YUZoV2FrWmhZekpPUjJKR1pGTmxhMVYzVjJ0U1IyRXhUa2RWYmtwb1VtdEtXRmxzWkc5a2JHUllaRVprYTJKV1ducFhhMXB2Vkd4T1NHRklRbFZXTTJoTVZqQmFZVk5GTlZaa1JscFRZbFpLU0ZaSGVGWmxSbHBYVjJ0YVQxWldTbFpaYTFwM1dWWndWMXBHWkZSU2EzQXdXVEJWTVZZeVNuSlRWRUpYWWtad2NsUnJXbHBsUmxweVdrWm9hVkpzY0ZsWFYzUnJWVEZaZUZkdVVtcGxhMHB5VkZaYVMxZEdXbk5oUnpsWVVteHNNMWxyVWxkWlZscFhWbGhvVjFaRldtaFdha3BQVWxaU2MxcEhhRTVpUlc4eVZtdGFWMkV4VVhoYVJXUlVZa2Q0Y1ZWdGRIZGpSbHB4VkcwNVZsWnRVbGhXVjNSclYyeGFjMk5GYUZkaVIyaHlWbTB4UzFaV1duSlBWbkJwVW14d2IxZHNWbUZoTWs1elZtNUtWV0pHV2s5V2JHaERVMVphY1ZKdE9XcE5WbkJaVld4b2IxWXlSbk5UYldoV1lURmFhRlJVUm1GamJIQkhWR3hTVjJFelFqVldSM2hoWVRGU2RGTnJXbXBTVjFKWVZGWmFTMUpHYkhGU2JrNVlVbXR3ZVZkcldtdGhWa2w1WVVjNVYxWkZTbWhhUkVaaFZqRldjMWRzWkZoU01taFFWa1phWVdReFNuTldXR3hyVWpOU2IxVnRkSGRXYkZwMFpVaE9XbFpyY0ZsV1YzQlBWbTFXY2xkdGFGWmlXRTE0Vm0xNGExWkdXbGxqUms1U1ZURldObFZyVGxabGJFcENTbFJPUlVwVVRrVSUzRA==
```

base64 一直解

注意 url 编码

```
U2FsdGVkX183BPnBd50ynIRM3o8YLmwHaoi8b8QvfVdFHCEwG9iwp4hJHznrl7d4
B5rKClEyYVtx6uZFIKtCXo71fR9Mcf6b0EzejhZ4pnhnJOl+zrZVlV0T9NUA+u1z
iN+jkpb6ERH86j7t45v4Mpe+j1gCpvaQgoKC0Oaa5kc=
```

AES key 为空

`缽娑遠呐者若奢顛悉呐集梵提梵蒙夢怯倒耶哆般究有栗`

[tudoucode](http://www.keyfc.net/bbs/tools/tudoucode.aspx)

解密

`把我复制走`

# 有趣的 ISCC

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/05/23/1527078391.jpg)

winhex 末尾

```
&#92;&#117;&#48;&#48;&#54;&#54;&#92;&#117;&#48;&#48;&#54;&#99;&#92;&#117;&#48;&#48;&#54;&#49;&#92;&#117;&#48;&#48;&#54;&#55;&#92;&#117;&#48;&#48;&#55;&#98;&#92;&#117;&#48;&#48;&#54;&#57;&#92;&#117;&#48;&#48;&#55;&#51;&#92;&#117;&#48;&#48;&#54;&#51;&#92;&#117;&#48;&#48;&#54;&#51;&#92;&#117;&#48;&#48;&#50;&#48;&#92;&#117;&#48;&#48;&#54;&#57;&#92;&#117;&#48;&#48;&#55;&#51;&#92;&#117;&#48;&#48;&#50;&#48;&#92;&#117;&#48;&#48;&#54;&#54;&#92;&#117;&#48;&#48;&#55;&#53;&#92;&#117;&#48;&#48;&#54;&#101;&#92;&#117;&#48;&#48;&#55;&#100;
```

unicode 解码

```
\u0066\u006c\u0061\u0067\u007b\u0069\u0073\u0063\u0063\u0020\u0069\u0073\u0020\u0066\u0075\u006e\u007d
```

再解一次

`flag{iscc is fun}`

# Where is the FLAG?

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/05/23/1527078393.jpg)

拖进 tweakpng 看到 Adobe Photoshop

打开后拼接图层

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/05/23/1527078394.jpg)

扫描即可得到 flag

# 凯撒十三世

`ebdgc697g95w3`

13 次移位

`roqtp697t95j3`

提交发现不对 后来想想 flag 开头应该是 flag{} 之类的

`r -> f o -> l q -> a t -> g`

以此类推

`flag:yougotme`

# 一只猫的心思

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/05/23/1527078395.jpg)

foremost 分离出 doc

```
名西三陵帝焰数诵诸山众參哈瑟倒陰捨劫奉惜逝定雙月奉倒放足即闍重号貧老诵夷經友利普过孕北至花令藐灯害蒙能羅福羅夢开雙禮琉德护慈積寫阿璃度戏便通故西故敬于瑟行雙知宇信在礙哈数及息闍殺陵游盧槃药諦慈灯究幽灯豆急彌貧豆親诵梭量树琉敬精者楞来西陰根五消夢众羅持造彌六师彌怖精僧璃夫薩竟祖方夢訶橋經文路困如牟憐急尼念忧戏輸教乾楞能敬告树来楞殊倒哈在紛除亿茶涅根輸持麼阿空瑟稳住濟号他方牟月息盡即来通貧竟怖如槃精老盡恤及游薩戏师毒兄宝下行普鄉释下告劫惜进施盡豆告心蒙紛信胜东蒙求帝金量礙故弟帝普劫夜利除積众老陀告沙師尊尼捨惜三依老蒙守精于排族祖在师利寫首念凉梭妙經栗穆愛憐孝粟尊醯造解住時刚槃宗解牟息在量下恐教众智焰便醯除寂想虚中顛老弥诸持山諦月真羅陵普槃下遠涅能开息灯和楞族根羅宝戒药印困求及想月涅能进至贤金難殊毘瑟六毘捨薩槃族施帝遠念众胜夜夢各万息尊薩山哈多皂诵盡药北及雙栗师幽持牟尼隸姪遠住孕寂以舍精花羅界去住勒排困多閦呼皂難于焰以栗婦愛闍多安逝告槃藐矜竟孕彌弟多者精师寡寫故璃舍各亦方特路茶豆積梭求号栗怖夷凉在顛豆胜住虚解鄉姪利琉三槃以舍劫鄉陀室普焰于鄉依朋故能劫通
```

拿之前的网址解密

```
523156615245644E536C564856544E565130354B553064524D6C524E546B4A56535655795645644F5530524857544A4553553943566B644A4D6C524E546C7052523155795645744F536C5248515670555330354452456456576B524854554A585231457956554E4F51305A4855544E4553303153566B64424D6C524A546B7058527A525A5245744F576C5A4854544A5554553554513063304E46524C54564A5652316B795255744F51305A4856544E5554564661566B6C464D6B5252546B70595231557A5245394E516C5A4856544A555355354B566B644E5756524E5455705752316B7A5255564F55305248566B465553564A4356306C4E4D6C524E546B4A565231557952453152556C564A56544A455555354B5530644E5756525054554A56523030795645314F516C5A4857544A4553303143566B64464D305648546B744352314A425645744F576C5A4855544A4651303543566B64564D6B524854554A555230557A52454E4F536C644855544A5554553543566B645A4D6B564A546C4E445231566152456C52576C5A4855544A5553303544516B64564D6C524C54564A55523045795245314F556C4A4856544E455355354B56556C564D6B564E546B70535230315A52457452536C564951544A555455354B565564535156524A54564A575230457956456C4E576C46485454525553303143566B6446576C564A54544A46
```

hex

```
R1VaREdNSlVHVTNVQ05KU0dRMlRNTkJVSVUyVEdOU0RHWTJESU9CVkdJMlRNTlpRR1UyVEtOSlRHQVpUS05DREdVWkRHTUJXR1EyVUNOQ0ZHUTNES01SVkdBMlRJTkpXRzRZREtOWlZHTTJUTU5TQ0c0NFRLTVJVR1kyRUtOQ0ZHVTNUTVFaVklFMkRRTkpYR1UzRE9NQlZHVTJUSU5KVkdNWVRNTUpWR1kzRUVOU0RHVkFUSVJCV0lNMlRNTkJVR1UyRE1RUlVJVTJEUU5KU0dNWVRPTUJVR00yVE1OQlZHWTJES01CVkdFM0VHTktCR1JBVEtOWlZHUTJFQ05CVkdVMkRHTUJUR0UzRENOSldHUTJUTU5CVkdZMkVJTlNDR1VaRElRWlZHUTJUS05DQkdVMlRLTVJUR0EyRE1OUlJHVTNESU5KVUlVMkVNTkpSR01ZREtRSlVIQTJUTU5KVUdSQVRJTVJWR0EyVElNWlFHTTRUS01CVkdFWlVJTTJF
```

base64

```
GUZDGMJUGU3UCNJSGQ2TMNBUIU2TGNSDGY2DIOBVGI2TMNZQGU2TKNJTGAZTKNCDGUZDGMBWGQ2UCNCFGQ3DKMRVGA2TINJWG4YDKNZVGM2TMNSCG44TKMRUGY2EKNCFGU3TMQZVIE2DQNJXGU3DOMBVGU2TINJVGMYTMMJVGY3EENSDGVATIRBWIM2TMNBUGU2DMQRUIU2DQNJSGMYTOMBUGM2TMNBVGY2DKMBVGE3EGNKBGRATKNZVGQ2ECNBVGU2DGMBTGE3DCNJWGQ2TMNBVGY2EINSCGUZDIQZVGQ2TKNCBGU2TKMRTGA2DMNRRGU3DINJUIU2EMNJRGMYDKQJUHA2TMNJUGRATIMRVGA2TIMZQGM4TKMBVGEZUIM2E
```

base32

```
5231457A5245644E536C6448525670555530354C5230645A4E4652505456705753566B7952464E4E576C5A485756705554553161566B6C5A4D6C5644546B4E485231704356456450516C5A4A57544A4554303161564564564D6B524C54554A555230466156454E4F51305A4856544A425054303950513D3D
```

hex

```
R1EzREdNSldHRVpUU05LR0dZNFRPTVpWSVkyRFNNWlZHWVpUTU1aVklZMlVDTkNHR1pCVEdPQlZJWTJET01aVEdVMkRLTUJUR0FaVENOQ0ZHVTJBPT09PQ==
```

base64

```
GQ3DGMJWGEZTSNKGGY4TOMZVIY2DSMZVGYZTMMZVIY2UCNCGGZBTGOBVIY2DOMZTGU2DKMBTGAZTCNCFGU2A====
```

base32

```
463161395F69735F493563635F5A4F6C385F4733545030314E54
```

hex

`F1a9_is_I5cc_ZOl8_G3TP01NT`

# 暴力XX不可取

zip 文件 猜测为伪加密

ZipCenOp.jar

解压后打开 flag.txt

`vfppjrnerpbzvat`

凯撒移位 每一对都试一遍

`isccwearecoming`

13 次移位