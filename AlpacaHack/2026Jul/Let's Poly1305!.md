# Let's Poly1305!

## / Overview

Poly1305における $`r`$ 漏洩時の選択的平文攻撃

Poly1305は高速なメッセージ認証コード（MAC）生成アルゴリズムです。単体でもメッセージ認証アルゴリズムとして使えますが、ブロック暗号のChaCha20と組み合わせた ChaCha20-Poly1305 という認証付き暗号（AEAD）として使われます。

Poly1305は鍵 $`K= (r, s)`$ を用いてデータ$`m = (m_1, m_2, \dots, m_n)`$をMACにします。条件として、$`r, s`$ は16バイトのバイナリデータです。

符号化プロセスは以下の式で表されます。

まずは $`r, s, (m_i||01)`$ をリトルエンディアンのバイト列として整数型 $`r', s', m'_i`$ に変換します。 $`(m_i||01)`$ は「$`m_i`$の末尾に1バイトの$`01`$を結合する」という意味です。

その後、$`r'`$ にはclampと呼ばれる以下の処理を施します。

$$ r' \leftarrow r' \land 21267647620597763993911028882763415551 $$

このマジックナンバーは16進数に直すと`0ffffffc0ffffffc0ffffffc0fffffff`です。つまり $`r'`$ の途中を除外するような作業です。

こうして処理された整数を用いて、最終的なMAC値は次のように計算されます。

$$MAC = \left[(m'_1 r'^n + m'_2 r'^{n-1} +  + m'_n r') \pmod{p} + s' \right]\bmod{2^{128}}$$

ここで$`p=2^{130}-5`$で、大外の $`\bmod{2^{128}}`$ はMACを16バイトに直すためにあります。

これでアルゴリズムの流れを掴めたので解法に移りましょう。

## / Writeup

今回のチャレンジでは、Poly1305の符号化において $`r`$ が公開されています。さらに、ターゲットデータ `admin=true` とは異なる任意の平文を符号化した結果を得る事ができます。

この時、ターゲットデータの符号化と同様のMAC値を得ることが出来るかという問題です。

符号化されるターゲットデータ`admin=true`は10バイトです。なので先程の説明に当てはめると16バイトブロックは一つであり、$`m = (m_1) `$です。

さらに`01`の結合やclampを経て最終的なMACコードは

$$MAC = \left[ m'_1 r' \bmod{p} + s' \right]\bmod{2^{128}}$$

で生成されます。$`m'_1`$ は `admin=true\x01` をリトルエンディアンで整数に変換したものなので `0x01...61` になることを覚えていてください。

ここで、`admin=true` とは異なる平文として `bdmin=true` を符号化してもらいます。01結合後のデータは `0x01...62` となり、$`m'_1 + 1`$ になっていることが分かります。したがってMAC値は

$$MAC' = \left[ (m'_1 + 1) r' \bmod{p} + s' \right]\bmod{2^{128}}$$

です。

もし$`(m'_1 r' \bmod{p}) + (r' \bmod{p}) = (m'_1 + 1) r' \bmod{p}`$が成り立てば

$$MAC' = MAC + r' \bmod{2^{128}}$$

と、既知の情報だけでターゲットのMACを知ることができます。この条件を満たす確率はいくつでしょうか？

簡単のため$`m'_1 r' \bmod{p}`$を$`[1,p-1]`$の一様分布とすると、条件を満たす時 $`m'_1 r' \bmod{p} < r'`$ である必要があるので求める確率は

$$\frac{p-r'-1}{p-1} \approx 1-(r'/p)$$ 

です。$`r' < 2^{124}`$ より(clampされているため) 

$$1-(r'/p) > 1 - 2^{-6} = 0.984$$

なので98%以上の確率でこの関係は成り立ちます。

$`MAC' = MAC + r' \bmod{2^{128}}`$ は高い確率で成り立つと分かったので、成功するまで繰り返すとこの解法は成り立ちます。

## / Solver

```py
from pwn import *

p = remote("34.170.146.252", 12581)
p.recvuntil(b"HINT! r: ")

r_bytes = bytes.fromhex(p.recvline().strip().decode())
print(f'{r_bytes = }')

r = int.from_bytes(r_bytes, 'little')
r = r & 0x0ffffffc0ffffffc0ffffffc0fffffff # clamp

p.sendafter(b'message:', b'bdmin=true\n')

c_bytes = bytes.fromhex(p.recvline().strip().decode())
c = int.from_bytes(c_bytes, 'little')

target_int = (c - r) % (2**128)

target_hex = target_int.to_bytes(16, 'little').hex()
p.sendafter(b'tag:', target_hex.encode()+b'\n')

print(f"{target_hex = }")

print(p.recvall())
```

## / Reference

[1] 晴耕雨読.「ChaCha20-Poly1305の解説と実装」. tex2e.github.io/blog/crypto/chacha20poly1305

[2] Nir, Y., & Langley, A. (2015). ChaCha20 and Poly1305 for IETF Protocols (RFC 7539). RFC Editor. https://doi.org/10.17487/RFC7539