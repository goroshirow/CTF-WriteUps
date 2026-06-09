# A Piece of DHKE

## / Overview

**元の位数を利用した秘密鍵設定**

このチャレンジでは前半でDH鍵交換、後半でフラグをAES暗号化しています。

DH鍵交換では以下のプロセスで二者AとBの間で共通鍵を生成します。

1. 有限体$`\mathbb{F}_p`$上の共通の元$`g`$を二者間で定める。
2. A, Bはそれぞれ秘密の値$`a`$, $`b`$を生成し、AからBに$`g^a \pmod{p}`$を、BからAに$`g^b \pmod{p}`$を送る。
3. 受け取った値からそれぞれ$`sk = g^{ab} \pmod{p}`$を計算する。

このように、互いに値を交換することで初めて鍵を生成することができますが、今回は相手が自分の計算した値を送ってくれていません。そのため、私たちは手元の情報から$`sk`$を計算することができません。

AESの暗号化では$`sk`$を使っているため、フラグを複合するには何らかの方法でこの値を知る必要があります。

先程のモデルでサーバ側をAとした時、私たちが既知の情報は以下の通りです。

1. 素数$`p`$
2. 生成元$`g`$
3. 自分たちが決めることができる数$`b`$（ただし$`1< g^b <p-1`$）
4. サーバ側の$`a`$は実行毎にランダムに決定
5. 暗号化されたフラグ$`c`$
6. $`p-1`$は6で割り切れて、かつ$`g^{(p-1)/3} \not\equiv 1 \pmod{p}`$、$`g^{(p-1)/2} \equiv 1 \pmod{p}`$

## / Writeup

6の性質を使います。$`b=(p-1)/3`$としてあげれば

$$1 < g^{a\cdot (p-1)/3} \pmod{p} < p-1$$
$$sk = g^{a\cdot (p-1)/3} \pmod{p}$$

が成り立ち、$`a`$が3の倍数の場合に指数が$`p-1`$の倍数になります。この時、フェルマーの小定理（もしくは6の性質）より$`sk=1`$なので共通鍵を特定できます。$`a`$はランダムな値なので$`1/3`$の確率で3の倍数となり、フラグの復号に成功します。

## / Solver

```py
from pwn import *
from Crypto.Util.number import long_to_bytes
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Util.Padding import unpad

def hash_int(x: int) -> bytes:
    x_bytes = long_to_bytes(x)
    return SHA256.new(x_bytes).digest()

def decrypt(key: int, data: bytes) -> bytes:
    iv, ciphertext = data[: AES.block_size], data[AES.block_size :]
    cipher = AES.new(key=hash_int(key), mode=AES.MODE_CBC, iv=iv)
    payload = cipher.decrypt(ciphertext)
    return unpad(payload, AES.block_size)

# ==========
# pが未知の場合でもアサーションを用いた二分探索で特定できます。
# ==========

# low = 2
# high = 100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
# while True:
#     mid = (low + high) // 2
#     ps = remote("34.170.146.252", 50224)
#     ps.recvuntil(b"gb = ")
#     ps.sendline(str(mid).encode())
#     data = ps.recvline().decode().split()[0]
#     print(f"gb = {mid}, flag_enc = {data}")
#     if data == "Traceback":
#         high = mid
#     else:
#         low = mid + 1
#     ps.close()
#     if low >= high:
#         print(f"Found p-1: {low}")
#         p = low + 1
#         break

g = 2
p_hex = """
FFFFFFFF FFFFFFFF C90FDAA2 2168C234 C4C6628B 80DC1CD1 29024E08 8A67CC74
020BBEA6 3B139B22 514A0879 8E3404DD EF9519B3 CD3CB093 FFFFFFFF FFFFFFFF
"""
p = int.from_bytes(bytes.fromhex(p_hex), "big")

while True:
    gb = pow(g, (p-1)//3, p)
    ps = remote("34.170.146.252", 50224)
    ps.recvuntil(b"gb = ")
    ps.sendline(str(gb).encode())
    ps.recvuntil(b"flag_enc = ")
    flag_enc = bytes.fromhex(ps.recvline().decode())
    print(f"{flag_enc = }")
    ps.close()
    try:
        flag = decrypt(1, flag_enc)
        break
    except Exception as e:
        pass

print(f"flag: {flag.decode()}")
```

## / Appendix

この様に小さい部分群を狙った攻撃を防ぐために、実際にはあえて$`q|p-1`$となる最大の素数$`q`$の部分群の元に数を限定するみたいです。

つまりバリデーションは$`gb^q \equiv 1 \pmod{p}`$となることです。この時、$`q`$未満の素数の約数は位数になることができないため、今回の攻撃を無効化できます。

さらに正確に言うと、$`p-1`$から$`q`$を計算するのではなく、$`q`$から$`p=2q+1`$が素数になるような$`p`$を選びます。