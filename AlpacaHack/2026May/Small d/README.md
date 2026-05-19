# Small d

## / Overview

RSAで秘密鍵 $`d`$ が小さい場合の攻撃（Wiener's attack）

## / Writeup

チャレンジの暗号化プロセスは以下のとおりです．

1. 大きな素数 $`p, q`$ を選び，$`N=pq`$ を計算する．
2. $`e`$ を選び，秘密鍵 $`d`$ を $`ed \equiv 1 \pmod{\phi(N)}`$ となるように計算する．
3. フラグを整数 $`m`$ に変換し，$`c \equiv m^e \pmod{N}`$ を計算する．

### 関係式を作る

RSAの鍵生成の条件 $`ed \equiv 1 \pmod{\phi(N)}`$ は，ある正の整数 $`k`$ を用いて以下のように書けます．

$`ed - k\phi(N) = 1`$

ここで，$`\phi(N) = (p-1)(q-1) = N - p - q + 1`$ を代入し，両辺を $`dN`$ で割ると以下のようになります．

$`\frac{e}{N} - \frac{k(N - p - q + 1)}{dN} = \frac{1}{dN}`$

これを $`\frac{e}{N}`$ について整理すると，以下の等式が得られます．

$`\frac{e}{N} = \frac{k}{d} \left( 1 - \frac{p + q - 1 - \frac{1}{k}}{N} \right)`$

この式は，公開されている $`\frac{e}{N}`$ と，求めたい未知の分数 $`\frac{k}{d}`$ との間にどれだけの誤差があるかを示しています．

### 連分数展開と近似分数による秘密鍵の特定

この誤差を評価し，未知の $`d`$ を見つけ出すために「連分数に関するLegendreの定理」を利用します．

> **連分数に関するLegendreの定理**
> 
> ある実数 $`x`$ と既約分数 $`\frac{a}{b}`$ について，$`\left| x - \frac{a}{b} \right| < \frac{1}{2b^2}`$ が成り立つならば，$`\frac{a}{b}`$ は必ず $`x`$ の連分数展開の近似分数のいずれかになる．

先ほどの等式から $`\frac{e}{N}`$ と $`\frac{k}{d}`$ の誤差を大まかに見積もります．$`p, q`$ はほぼ同じ大きさの素数($`\approx \sqrt{N}`$)であるため $`p+q < 3\sqrt{N}`$ となり，$`ed \approx kN`$ から $`k < d`$ となります．

先程の等式を変形し，先程の議論を当てはめると次の不等式が得られます．

$`\left| \frac{e}{N} - \frac{k}{d} \right| = \frac{k}{d} \frac{p + q - 1 - \frac{1}{k}}{N} \approx \frac{k}{d} \cdot \frac{3\sqrt{N}}{N} < \frac{3}{\sqrt{N}}`$

Legendreの定理の条件 $`\frac{1}{2d^2}`$ を満たすためには，以下が成り立てばよいことになります．

$`\frac{3}{\sqrt{N}} < \frac{1}{2d^2}`$

この不等式を解くと $`d < \frac{1}{\sqrt{6}} N^{\frac{1}{4}}`$ となります．

問題の設定により，秘密鍵 $`d`$ はこの条件を満たすほど小さく設定されています．したがって，公開鍵 $`\frac{e}{N}`$ を連分数展開し，その展開を途中で打ち切って作る近似分数を順に計算していけば，そのリストの中に必ず $`\frac{k}{d}`$ が出現することになります．

近似分数から得られた分母 $`d`$ を候補とし，$`k`$ と $`d`$ から $`\phi(N)`$ の候補を逆算して方程式 $`x^2 - (N - \phi(N) + 1)x + N = 0`$ の解 $`p, q`$ が整数になるかを検算することで，正しい秘密鍵を効率的に特定できます．

### 秘密鍵と素因数 $p, q$ の復元

近似分数の計算から得られた $`d`$ と $`k`$ のペアが本当に正しい秘密鍵であるかは，RSA暗号の性質を利用して素因数 $`p, q`$ が正しく復元できるかで判定します．

まず，$`ed - 1 = k\phi(N)$ の関係から，$\phi(N)`$ の候補を逆算します．
$$\phi(N) = \frac{ed - 1}{k}$$
この時点で $`(ed - 1)`$ が $`k`$ で割り切れない場合，その $`d`$ は候補から外れます．

次に，$`\phi(N) = (p-1)(q-1) = N - p - q + 1`$ という定義から，$`p`$ と $`q`$ の和を導き出します．
$$p + q = N - \phi(N) + 1$$

ここで，2つの数 $`p, q`$ の和 $`S = p+q`$ と，積 $`N = pq`$ が判明しました．解と係数の関係より，$`p`$ と $`q`$ は以下の二次方程式の2つの解となります．
$$x^2 - Sx + N = 0$$

この二次方程式を解の公式で解くと，以下のようになります．
$$x = \frac{S \pm \sqrt{S^2 - 4N}}{2}$$

この解は $`p, q`$ であり，正の整数になるためには，平方根の中身である判別式 $`D = S^2 - 4N`$が0以上であり，かつ完全平方数である必要があります．
判別式が条件を満たし，得られた解 $`p, q`$ が整数になれば，元の $`N`$ を正しく素因数分解できたことになります．これは同時に，仮定した $`d`$ が真の秘密鍵であったことの証明となります．

## / Solver

ソルバはGeminiに作ってもらいました．
```py
from pwn import *
from Crypto.Util.number import long_to_bytes
from math import isqrt

n = ...省略...
e = ...省略...
c = ...省略...

# -------------------------
# 連分数展開
# -------------------------
def continued_fraction(n, d):
    cf = []
    while d:
        q = n // d
        cf.append(q)
        n, d = d, n - q * d
    return cf

# -------------------------
# 連分数から収束分数生成
# -------------------------
def convergents(cf):
    p0, p1 = 0, 1
    q0, q1 = 1, 0

    for a in cf:
        p2 = a * p1 + p0
        q2 = a * q1 + q0
        yield (p2, q2)
        p0, p1 = p1, p2
        q0, q1 = q1, q2

# -------------------------
# 平方判定
# -------------------------
def is_perfect_square(x):
    if x < 0:
        return False
    r = isqrt(x)
    return r * r == x

# -------------------------
# Wiener attack本体
# -------------------------
def wiener_attack(e, n):
    cf = continued_fraction(e, n)

    for k, d in convergents(cf):
        if k == 0:
            continue

        # ed - 1 = k * phi(n) から d の判定
        if (e * d - 1) % k != 0:
            continue

        phi = (e * d - 1) // k

        # x^2 - (n - phi + 1)x + n = 0
        s = n - phi + 1

        # 判別式
        discr = s * s - 4 * n
        if discr < 0:
            continue

        if not is_perfect_square(discr):
            continue

        t = isqrt(discr)
        p = (s + t) // 2
        q = (s - t) // 2

        if p * q == n:
            return d, p, q

    return None

# -------------------------
# 復号
# -------------------------
def decrypt(c, d, n):
    return pow(c, d, n)

# -------------------------
# 使用例
# -------------------------
if __name__ == "__main__":

    res = wiener_attack(e, n)

    if res:
        d, p, q = res
        print("[+] Found d:", d)
        print("[+] p:", p)
        print("[+] q:", q)

        m = decrypt(c, d, n)
        print("[+] plaintext:", long_to_bytes(m))
    else:
        print("[-] attack failed (d not small enough)")
```