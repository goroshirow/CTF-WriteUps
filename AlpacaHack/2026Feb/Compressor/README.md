---
title: "Daily Alpacahack Compressor Writeup"
tags: ["gzip", "deflate", "LZSS", "Misc"]
---

# Compressor

## / Overview

符号化方式LZSSによる挙動の違いを用いた総当り

## / Writeup

まず問題で使われている`Deflate`アルゴリズムとはどの様な符号化方式なのかを、以下の記事を参考に調べました。

> ゼロから始めるDeflate圧縮
>
> https://qiita.com/ajinadai/items/9c02dc750bc017c93c8f

`Deflate`アルゴリズムは`LZSS`→`ハフマン符号`という順番でデータを圧縮しているようです。この前半の`LZSS`というのは、**データ中の連続する文字列をまとめる**ためのアルゴリズムです。これは、今見ている長さmの文字列がn文字前にあれば、その部分は`(m,n)`のように変えてしまえば良いという発想です。例えば`AlpacaAlpaca`という文字列があれば`Alpaca(6,6)`になります。もし`AlpacaAlpaco`なら`Alpaca(5,6)o`と書き換わるはずです。つまり一致率が高いほど圧縮率も高くなります。

### server.pyの仕様

チャレンジサーバーに何か文字を送ると、フラグの後に結合されてから圧縮されます。つまり`hoge`と送ると`Alpaca{...}hoge`が圧縮されます。

圧縮後のバイト数がサーバーから返ってくるので、ここからフラグを予想しなければなりません。

### 実験

一致率が高いと圧縮率が高くなるということは先程も述べた通り`Alpaca{`の後に正解の文字を結合したときだけ、バイト長が短くなるんじゃないか。ということで`abcdefghijklmnopqrstuvwxyz_A{}`を一文字ずつ結合して送ってみましょう。結果は

* 64バイト：`acdeghilnoprstuvwy_A{}`
* 65バイト：`bfjkmqxz`

となりました。これでは一意に次の文字を決められません。

なので繰り返してみるとどうかと考えました。予想では

* `AlpacaAlpacaAlpacaAlpacaAlpaca`->`Alpaca(6,6)(6,6)(6,6)(6,6)`
* `AlpacaAlpacoAlpacoAlpacoAlpaco`->`Alpaca(5,6)o(5,6)o(5,6)o(5,6)o`

みたいに差が広がっていくんじゃないかと。(今考えたら二回目以降の`Alpaco`は`(6,6)`に置き換えられるかも)

結果は、正解の時だけ1バイト小さくなるようになりました。つまり1文字ずつ総当りをして、1つだけバイト長が短くなるものを採用していけば、フラグが求まるようになりました！

しかし、実験してみると何回繰り返して送っても、バイト長の差は毎回1バイトにしかなリませんでした。何故なんでしょうか？

僕の考察では

* `AlpacaAlpacaAlpacaAlpacaAlpaca`->`Alpaca(6,6)(6,6)(6,6)(6,6)`
* `AlpacaAlpacoAlpacoAlpacoAlpaco`->`Alpaca(5,6)o(6,6)(6,6)(6,6)`

になった後、`(6,6)`の部分がハフマン符号化によって短い符号長が割り当てられる様になったからかな？とか思うのですが。他の方のWriteupで勉強させてもらおうと思います。

## / Solver

```py
from pwn import *

flag = 'Alpaca{'

p = remote('34.170.146.252', 28539)

for _ in range(50):
    MinLen = 9999
    for c in 'abcdefghijklmnopqrstuvwxyz_A{}':
        candidate = flag + c
        print(f'Trying: {candidate}')
        candidate *= 5
        p.recvuntil(b'Your input: ')
        p.sendline(candidate.encode())
        p.recvuntil(b'Size of compressed data: ')
        size = int(p.recvline().decode().split()[0])
        print(f'Size: {size}')
        if size < MinLen:
            MinLen = size
            next_char = c
            
    flag += next_char
    print(flag)
    if next_char == '}':
        break
```