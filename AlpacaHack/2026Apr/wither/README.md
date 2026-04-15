# wither

## / Overview

ANDを使った暗号文の解読

## / Writeup

このチャレンジではEnterを押す度に、平文とランダムな鍵が`AND`された暗号文が入手できます。

通常、暗号で使われるのは`XOR`だと思いますが、`AND`だと何かまずいのでしょうか。

結論から言うと、十分な量の暗号文を集めて`OR`を取ることで平文が解読されます。次の式を見てください。

平文を$`pt`$、鍵を$`k_i`$とします。$`i`$はEnterを押した回数です。この時、暗号文は

$$ct_i = pt\land k_i$$

と表せます。この暗号文を例えば3回`OR`してみましょう。

$$ct_1 \lor ct_2 \lor ct_3 = (pt\land k_1) \lor (pt\land k_2) \lor (pt\land k_3)$$

分配法則より

$$= pt \land (k_1 \lor k_2 \lor k_3)$$

になります。鍵はランダムなので、各桁のビットが1になる確率は`1/2`です。つまり10個くらい`OR`すれば$`k_1`$から$`k_10`$までの論理和は全て1になる確率が高いです。つまり、

$$ct_1 \lor \cdots \lor ct_{10} = pt$$

となるでしょう。

## / Solver

```py
from pwn import *
from Crypto.Util.number import long_to_bytes
context.log_level = 'debug'

cts = []

p = remote('34.170.146.252', 29127)
for _ in range(10):
    p.sendafter(b'Press Enter to get the encrypted flag...', '\n')
    p.recvuntil(b'Encrypted flag: ')
    cts.append(int(p.recvline(), 16))

result = 0
for i in cts:
    result |= i

print(long_to_bytes(result))
```