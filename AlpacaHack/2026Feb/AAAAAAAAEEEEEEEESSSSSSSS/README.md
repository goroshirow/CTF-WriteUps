---
title: "Daily Alpacahack Inu Profile Writeup"
tags: ["AES-ECB", "CPA", "Crypto"]
---

# AAAAAAAAEEEEEEEESSSSSSSS

## / Overview

AES-ECB選択的平文攻撃

## / Writeup

AES-ECBモードは、元のメッセージを16バイトずつ区切り、それぞれを**同じ鍵で暗号化**します。つまり、ある暗号化ブロックが他の暗号化ブロックと一致する場合、そのブロックは解読されてしまいます。

今回の問題では1ブロックに2文字しかない（例えば最初のブロックは`AAAAAAAAllllllll`）ので、55*55=3025通り計算すれば全てのブロックパターンを知ることが出来ます。

## / solver

```py
from pwn import *

p = remote('34.170.146.252', 50373)

flag_charset = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz{}_"

p.recvuntil(b'ciphertext(hex): ')
ct = p.recvline().strip().decode()
print(f"Ciphertext: {ct}")

index = []
blocks = []

for c in flag_charset:
    c_hex = hex(ord(c))[2:] * 8
    
    for d in flag_charset:
        d_hex = hex(ord(d))[2:] * 8
        guess = c_hex + d_hex
        
        p.recvuntil(b'plaintext to encrypt (hex): ')
        p.sendline(guess.encode())
        
        p.recvuntil(b'ciphertext(hex): ')
        res = p.recvline().strip().decode()
        
        index.append(c + d)
        blocks.append(res)

flag = ""

for i in range(16):
    curr_block = ct[i*32 : (i+1)*32]
    for j in range(len(index)):
        if blocks[j] == curr_block:
            found_chars = index[j]
            flag += found_chars
            print(found_chars)
            break

print(f"Flag: {flag}")
```