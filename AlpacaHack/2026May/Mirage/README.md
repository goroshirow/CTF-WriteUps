# Mirage

## / Overview

XOR解読

## / Writeup

`main()`のフラグ判定は，毎ループで`((uint8_t)buf[i] ^ (state & 0x7F)) == enc[i]`あることが条件なので，逆に`enc[i]^(state & 0x7F)`で一文字ずつ解読できます．

`state`は`state=step(state)`で毎回更新されますが，初期値も`step()`の実装も分かっているので再現できます．よって以下のソルバを使って先頭から一文字ずつフラグを復元します．

## / Solver

```py
enc = [
    0x31, 0x54, 0x6c, 0x2f, 0x04, 0x52, 0x22, 0x41, 0x3f, 0x59,
    0x27, 0x45, 0x67, 0x79, 0x1a, 0x4e, 0x78, 0x2d, 0x19
]

def step(s):
    bit = ((s >> 0) ^ (s >> 2) ^ (s >> 3) ^ (s >> 5)) & 1
    return (s >> 1) | (bit << 15)

state = 0xACE1 

flag = ""

for i in enc:
    state = step(state)
    flag += chr(i ^ (state & 0x7F))

print(flag)
```