# One Byte Padding Oracle Attack

## / Overview

AES-CBC パディングオラクル攻撃

## / Writeup

AESのCBCモードでは前のブロックの暗号文（またはIV）$`C_{i-1}`$と平文$`P_i`$をXORしたものを暗号化します。

$$C_i = E_K (P_i \oplus C_{i-1})$$

![alt text](image-1.png)

そのため復号フェーズでは、現在の暗号化ブロックの復号結果と、前の暗号化ブロックをXORします。

$$P_i = D_K (C_i) \oplus C_{i-1}$$

![alt text](image.png)

この性質を用いると、復号前に$`C_{i-1}`$を同じバイト長（16バイト）の任意の数$`I`$とXORすると

$$P_i = D_K (C_i) \oplus C_{i-1} \oplus I$$

が成り立ち、好きなビット位置を反転させることが出来ます。

さて、AESのCBCモードではバイト長が16バイトの整数倍ではないときにパディングを用いるのですが、その中の代表的なものに`PKCS#7`というパディングがあり、これは足りない分のバイト長で残りを埋めるというものです。例えば最後のブロックが15バイトなら`\x01`を付け足します。

これを悪用するのが今回の問題です。このパディングは裏を返せば適切な$`I`$を持ってきてXORすれば、最後のバイトが`\x01`となってパディングと誤認されます。この様になる条件は

$$0x01 = D_K (C_i) \oplus C_{i-1} \oplus I$$
$$D_K (C_i) = 0x01 \oplus C_{i-1} \oplus I $$

です。オラクルから`True`が返ってきたときにこれが成り立つので、配布された`README`のTODOをこれで埋めればパディングオラクル攻撃のsolverが完成します。

## / Solver

```py
from pwn import process, remote
from Crypto.Util.strxor import strxor

def send(sc, iv_ciphertext:bytes):
    sc.sendline(iv_ciphertext.hex())
    res = sc.readline()
    return b"True" in res

def change_byte(iv_ciphertext:bytes, index:int, b:int):
    l = list(iv_ciphertext)
    l[index] = b
    return bytes(l)

sc = remote("34.170.146.252", 60240) # you have to change localhost
# sc = process(["python3", "server.py"]) # or you can use for local debug

iv_ciphertext = bytes.fromhex(sc.readline().split(b'=')[1].decode())

iv_ciphertext = iv_ciphertext[:-16]

flag = ""
while len(iv_ciphertext) > 16:
    for i in range(256):
        b = change_byte(iv_ciphertext, len(iv_ciphertext)-17, i)
        if send(sc, b):
            a = iv_ciphertext[len(iv_ciphertext)-17]
            flag += chr(0x01 ^ i ^ a) # try change this line!
            break
    iv_ciphertext = iv_ciphertext[:-16]

print(''.join(reversed(flag)))
```
