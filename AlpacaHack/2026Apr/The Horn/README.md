# The Horn

## / Overview
XORと置換で構成される暗号に対する選択的平文攻撃

## / Writeup
今回のゴールは最初に与えられる暗号文$`ct`$から平文$`pt`$を復号することです。

暗号化に使われているPBOX置換は、入力される配列の各要素をPBOXに従って入れ替えます。本チャレンジでは

```python
PBOX = [5, 22, 31, 18, 3, 19, 11, 13, 10, 25, 24, 0, 2, 17, 20, 12, 6, 26, 1, 7, 16, 4, 27, 21, 15, 8, 30, 28, 14, 23, 29, 9]
```

が使われており、例えば0番目の要素は5番目に移動します。

更にXORとPBOX置換をそれぞれ、$`x \oplus y`$、$`P(x)`$と表すと、暗号化は

$$E(pt, key) = P(...P(P(pt \oplus key) \oplus key)... \oplus key)$$

のように表せます。ここで$`P(x \oplus y)=P(x) \oplus P(y)`$であることを用いると、

$$E(pt, key) = P^{32}(pt) \oplus P(key) \oplus P^2 (key) \dots \oplus P^{32}(key) $$

$$= P^{32}(pt) \oplus S$$

のように簡単にすることができます。ここで

$$S = P(key) \oplus P^2 (key) \dots \oplus P^{32}(key)$$

です。

復号のために$`P`$の逆関数の適用、つまりPBOX置換をもとに戻す事を考えますが、これは簡単で以下の配列を用いた再置換で実現できます。

```python
PBOX_INV = [11, 18, 12, 4, 21, 0, 16, 19, 25, 31, 8, 6, 15, 7, 28, 24, 20, 13, 3, 5, 14, 23, 1, 29, 10, 9, 17, 22, 27, 30, 26, 2]
```

後は$`S`$さえ求まれば$`pt`$を復号できるので、オラクルを用いて$`S`$を知ります。オラクルには任意の平文を入力として、暗号化の結果を出力することができるので$`pt=0`$とした時、暗号化の結果はそのまま$`S`$になります。

ここまでの情報を用いて以下の手順で復元できます。

1. オラクルに平文$`0`$の結果を聞く。
$$S = P^{32}(0) \oplus S$$

2. SとPの逆関数を用いて復号する。
$$pt = P^{-32}(ct \oplus S)$$

## / Solver

```python
from pwn import *

BLOCK_SIZE = 32
ROUNDS = 32
PBOX = [5, 22, 31, 18, 3, 19, 11, 13, 10, 25, 24, 0, 2, 17, 20, 12, 6, 26, 1, 7, 16, 4, 27, 21, 15, 8, 30, 28, 14, 23, 29, 9]
PBOX_INV = [11, 18, 12, 4, 21, 0, 16, 19, 25, 31, 8, 6, 15, 7, 28, 24, 20, 13, 3, 5, 14, 23, 1, 29, 10, 9, 17, 22, 27, 30, 26, 2]

def pbox(pt):
    assert len(PBOX) == BLOCK_SIZE
    return bytes([pt[PBOX[index]] for index in range(BLOCK_SIZE)])

def pbox_inv(ct):
    return bytes([ct[PBOX_INV[index]] for index in range(BLOCK_SIZE)])

def bxor(bs1, bs2):
    return bytes([b1 ^ b2 for b1, b2 in zip(bs1, bs2)])

def reorder(ct):
    for _ in range(ROUNDS):
        ct = pbox_inv(ct)
    return ct

if __name__ == "__main__":
    p = remote('34.170.146.252', 30351)
    
    p.recvuntil("CHALLENGE: ")
    challenge = bytes.fromhex(p.recvline().strip().decode())
    challenge_reordered = reorder(challenge)
    
    payload = b'00' * BLOCK_SIZE
    p.recvuntil("pt: ")
    p.sendline(payload)
    response = bytes.fromhex(p.recvline().strip().decode())
    response_reordered = reorder(response)
    
    CHALLENGE = bxor(challenge_reordered, response_reordered)
    
    p.recvuntil("pt: ")
    p.sendline(b'guess')
    p.recvuntil("challenge: ")
    p.sendline(CHALLENGE.hex())
    print(p.recvall().decode())
```