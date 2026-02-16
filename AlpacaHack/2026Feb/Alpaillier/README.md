---
title: "Daily Alpacahack Alpaillier Writeup"
tags: ["Paillier Cryptosystem", "Crypto"]
---

# Alpaillier

## / Overview

乱数固定Paillier暗号に対する攻撃

## / Writeup

問題の暗号化プロセスは以下のとおりです．

1. 512ビット素数$`p,q`$を選ぶ．
2. $`n=pq`$, $`g=n+1`$を計算し, $`n`$と互いに素な$`r\in [2, n-1]`$を取る．
3. フラグ`Alpaca{...}`の各文字のASCIIコードを$`b_0 b_1 ... b_{34}`$として$`c_i = g^{b_i}r^n \pmod{n^2}`$を計算する．

この$`n`$と$`c_i`$が公開情報です．

### 関係式を作る

まずは二項定理を用いて$`g^{b_i}=(n+1)^{b_i}=Q(n)\cdot n^2 + b_i n + 1 `$のように変形します．$`n^2`$の剰余を取ると$`b_i n + 1`$が残るので

$`c_i \equiv (b_i n + 1)r^n \bmod{n^2}`$

と書き換えることが出来ます．さらに$`n`$を両辺に掛けると

$`nc_i \equiv (b_i n^2 + n)r^n \equiv nr^n \bmod{n^2}`$

が導かれます．もう一つ，暗号文同士の引き算を考えると

$`c_i - c_j \equiv (b_i - b_j)nr^n \bmod{n^2}`$

が成り立ちます．$`(b_i - b_j)`$はASCIIコード同士の引き算であるため，総当りが可能です．$`b_0 = A, b_1=l`$であることは分かっているので，この関係が本当に成り立っているのか検算することも可能です．
```py
assert (ord('A')-ord('l'))*nrn % n2 == (c[0] - c[1]) % n2
```

Solverは$`b_0 = A`$を基準に

$`(!-A)nr^n\equiv -32nr^n \pmod{n^2}`$

から

$`(\}-A)nr^n\equiv 60nr^n \pmod{n^2}`$

までを事前計算し，$`c_i - c_0`$と一致するかを判定しています．

## / Solver

```py
n = ...省略...
c = [...省略...] # 要素数35

n2 = n**2
nrn = c[0]*n % n2

# 検算
assert (ord('A')-ord('l'))*nrn % n2 == (c[0] - c[1]) % n2

table = [x*nrn % n2 for x in range(-32, 61)]

flag = ''

for s in c:
    target = (s - c[0]) % n2
    for i, ref in enumerate(table):
        if target == ref:
            flag += chr(i+33)
print(flag)
```