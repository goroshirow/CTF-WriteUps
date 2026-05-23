# Even Worse RSA

## / Overview

$`m^e \pmod{p}`$を、指数削減とAMMアルゴリズムによって復号

## / Writeup

素数$`p`$と自然数$`e`$、およびフラグを暗号化した$`c = m^e \pmod{p}`$が公開されています。ここから$`m`$を復号することが目的です。

通常、この様なべき乗暗号は**オイラーの小定理**を用いた解読をします。$`ed \equiv 1 \pmod{p-1}`$となるような$`d`$を取ることができれば、$`c^d \equiv m \pmod{p}`$が計算できるからです。

しかし$`d`$を計算するには$`e`$と$`p-1`$が互いに素である必要があり、今回はこの条件を満たしていません。

残念ながら$`e`$の逆元は求まりませんが、互いに素でない場合も含めた一般化として、$`e`$と$`p-1`$の最大公約数を$`g`$として$`ed \equiv g \pmod{p-1}`$となる$`d`$を求めることはできます。これを使うと$`m^g \pmod{p}`$を求めることができます。

さて、べき乗の指数は小さくなりましたが、まだ答えは求まりません。有限体上の計算なので$`m^g \pmod{p}`$を単に$`g`$乗根を取るわけにも行かず、有限体上専用の$`g`$乗根計算アルゴリズムを考える必要があります。

今回私が実装したのは、**Adleman-Manders-Miller (AMM) による有限体上の $r$ 乗根計算アルゴリズムを改良した手法**です[[1]](https://arxiv.org/pdf/1111.4877)。このアルゴリズムは素数$`r`$に対して、$`x^r \equiv a \pmod p`$となる$`x`$が存在すれば、$`x`$出力しますが、このままでは$`g`$が合成数の時に根を取ることができません。なので$`g=q_1 q_2 ... q_n `$に素因数分解し、$`(m^{q_1 q_2 ... q_{n-1}})^{q_n} `$ を考えることで$`q_n`$乗根を求める問題に帰着させます。求まった解に対して$`q_{n-1}`$乗根を求めることで再帰的に$`g`$乗根の解を求められるようにします。

この時$`r`$乗根の解は最大で$`r`$個出てくるため、全体として解の候補の最大数は$`g`$個になります。これを全てデコードしてASCIIとして読めるものをフラグと判定します。

備考: SageMathを使えば多項式環の根を求める数行の実装で済むらしい。

## / Solver

```py
from Crypto.Util.number import long_to_bytes
import math

p = 8751921425256563367579143227840921849402469143061750238936013324282215699146538047799233649294185141005855739102550788165605861428703197268970229186963997
e = 65538
c = 5947948986109551330433379864390441851954259789762156065124570979131577895849125770689468451948141963015046816934387597958310386264293643862965407787651953

def EEA(u, v):
    a, b, c_val, d = 1, 0, 0, 1
    if v > u:
        u, v = v, u
        a, c_val = c_val, a
        b, d = d, b
    while v != 0:
        q_div = u // v
        a, c_val = c_val, a - q_div * c_val
        b, d = d, b - q_div * d
        u, v = v, u - q_div * v
    gcd = u
    return gcd, a, b

def _amm_prime_nth_root(delta: int, r: int, q: int) -> list[int]:
    """
    https://arxiv.org/pdf/1111.4877
    Table 4: Adleman-Manders-Miller rth root extraction algorithm に準拠した実装
    """
    if delta % q == 0:
        return [0]
        
    # Step 1 & 2: 非剰余 rho の探索（および解の存在確認）
    if pow(delta, (q - 1) // r, q) != 1:
        return []
        
    rho = 2
    while pow(rho, (q - 1) // r, q) == 1:
        rho += 1
        
    # Step 3: 初期化
    s = q - 1
    t = 0
    while s % r == 0:
        s //= r
        t += 1
        
    # s | r * alpha - 1 を満たす最小の非負整数 alpha を計算
    # (つまり r * alpha ≡ 1 (mod s) の逆元)
    alpha = pow(r, -1, s)
    
    # a, b, c, h の計算
    a_val = pow(rho, (r**(t - 1)) * s, q)
    b = pow(delta, r * alpha - 1, q)
    c = pow(rho, s, q)
    h = 1
    
    # Step 4: メインループ
    for i in range(1, t): # 1 から t-1 まで
        d = pow(b, r**(t - 1 - i), q)
        
        if d == 1:
            j = 0
        else:
            # j <- -log_{a_val}(d) の計算（離散対数）
            # a_val^j * d ≡ 1 (mod q) となる j を探す -> a_val^j ≡ d^-1 (mod q)
            d_inv = pow(d, -1, q)
            j = 1
            a_j = a_val
            while a_j != d_inv:
                a_j = (a_j * a_val) % q
                j += 1
                if j >= r:
                    raise RuntimeError("離散対数 j が見つかりません。")
                    
        # 変数の更新
        b = (b * pow(pow(c, r, q), j, q)) % q
        h = (h * pow(c, j, q)) % q
        c = pow(c, r, q)
        
    # Step 5: 最初に見つかった解
    root = (pow(delta, alpha, q) * h) % q
    
    # 1の原始 r 乗根を用いてすべての解を生成して返す
    zeta = pow(rho, (q - 1) // r, q)
    roots = []
    current_root = root
    for _ in range(r):
        roots.append(current_root)
        current_root = (current_root * zeta) % q
        
    return roots

def amm_nth_root(delta: int, n: int, q: int) -> list[int]:
    """
    合成数 n に対応し、すべての解をリストとして返すラッパー関数
    """
    # 1. n を素因数分解する
    factors = []
    temp = n
    for i in range(2, int(math.isqrt(n)) + 1):
        while temp % i == 0:
            factors.append(i)
            temp //= i
    if temp > 1:
        factors.append(temp)
        
    # 2. 各素因数について順番に根を求める（枝分かれ探索）
    candidates = [delta]
    for r in factors:
        next_candidates = []
        for c_val in candidates:
            next_candidates.extend(_amm_prime_nth_root(c_val, r, q))
        
        candidates = list(set(next_candidates))
        if not candidates:
            return []
            
    return candidates

# ==========================================
# 実行部
# ==========================================
g, a, b = EEA(e, p-1)
mg = pow(c, a, p)

for m in amm_nth_root(mg, g, p):
    pt = long_to_bytes(m)
    print(pt)
```


## / Reference

[1] Cao, Zhengjun, Qian Sha, and Xiao Fan. "Adleman-Manders-Miller root extraction method revisited." International Conference on Information Security and Cryptology. Berlin, Heidelberg: Springer Berlin Heidelberg, 2011.

