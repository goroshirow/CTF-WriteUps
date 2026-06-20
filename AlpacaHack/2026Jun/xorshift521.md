# xorshift521 

## / Overview

位数 $`2^{521} - 1`$ の擬似乱数生成器を用いた計算

与えられた擬似乱数生成器の状態更新関数 $`next(state)`$ は、ビットシフトとXORのみで構成されています。XORは $`GF(2)`$ 上での加算に相当するため、この状態更新は $`\mathbb{F}_2`$ 上の線形写像として記述することができます。

`state` をベクトルで表現するために、次元を $`n = 521`$ とし、あるステップ $`i`$ における状態ベクトルを $`\mathbf{s}_i \in \mathbb{F}_2^{521}`$ と定義すると、
ビットシフト操作は行列として表現できます。左シフトを $`L`$、右シフトを $`R`$ とし、単位行列を $`I`$ とすると、各操作は以下の行列の乗算に相当します。

1. $`\mathbf{s} \leftarrow \mathbf{s} \oplus (\mathbf{s} \ll 5 \cdot 21) \implies \mathbf{s} \leftarrow (I + L_{105})\mathbf{s}`$
2. $`\mathbf{s} \leftarrow \mathbf{s} \oplus (\mathbf{s} \gg 52 + 1) \implies \mathbf{s} \leftarrow (I + R_{53})\mathbf{s}`$
3. $`\mathbf{s} \leftarrow \mathbf{s} \oplus (\mathbf{s} \ll 0o521) \implies \mathbf{s} \leftarrow (I + L_{337})\mathbf{s}`$

よって、1ステップの状態遷移は、以下の変換行列 $`T \in \mathbb{F}_2^{n \times n}`$ を用いて次のように表されます。
$$T = (I + L_{337})(I + R_{53})(I + L_{105})$$
$$\mathbf{s}_{i+1} = T \mathbf{s}_i$$

チャレンジにおけるゴールは、初期状態 $`\mathbf{s}_0`$ を $`N = 521^{521\cdot 521}`$ 回進めた状態 $`\mathbf{s}_N`$ を求めることです。
$$\mathbf{s}_N = T^N \mathbf{s}_0$$

## / Writeup

ここで、 $`2^{521}-1`$ は素数なので、行列 $`T`$ の特性多項式が既約多項式であれば、$`\mathbb{F}_2`$ 上の原始多項式となります。特性多項式が原始多項式である場合、行列 $`T`$ が生成する巡回群の位数は $`2^n - 1`$ になります。

おそらく今回もこの条件を満たしているので（確認してませんが）、初期状態に対して、状態は $`2^{521}-1`$ 周期で元に戻ります。
$$T^{2^{521}-1} \equiv I \pmod{2}$$

この性質を利用すると、巨大な指数 $`N`$ を法 $`2^{521}-1`$ で減らすことができます。
$$N' \equiv 521^{271441} \pmod{2^{521}-1}$$
これにより、求めるべき状態は $`\mathbf{s}_{N'} = T^{N'} \mathbf{s}_0`$ となり、計算量を大幅に削減できます。

しかし依然として行列の乗算コストが重くなります。そこで、多項式の剰余演算に帰着させます。行列 $`T`$ の特性多項式 $`P(x) \in \mathbb{F}_2[x]`$ を次のように定義します。
$$P(x) = \det(xI - T)$$

ケーリー・ハミルトンの定理により、行列 $`T`$ は特性多項式の解になります。
$$P(T) = O$$

この定理により、$`\mathbb{F}_2[x]`$ 上の任意の多項式 $`f(x)`$ について、行列 $`f(T)`$ の計算は $`f(x) \pmod{P(x)}`$ の計算と同じになります。$`x^{N'}`$ を $`P(x)`$ で割った商を $`Q(x)`$、余りを $`R(x)`$ とすると、
$$x^{N'} = Q(x)P(x) + R(x)$$
両辺の $x$ に行列 $T$ を代入すると、$P(T) = O$ であるため、
$$T^{N'} = Q(T)P(T) + R(T) = R(T)$$
が成り立ちます。

$`\mathbb{F}_2[x]`$ 上における $`x^{N'} \pmod{P(x)}`$ の計算は、多項式のバイナリ法を用いることで高速に計算できます。求まった剰余多項式 $R(x)$ の次数は、$`P(x)`$ の次数 $n$ 未満になります。

$`R(x)`$ の各項の係数を $`c_i \in \{0, 1\}`$ とすると、
$$R(x) = c_0 + c_1 x + c_2 x^2 + \dots + c_{n-1} x^{n-1}$$

先述の通り $T^{N'} = R(T)$ であるため、これを初期状態 $s_0$ に作用させます。
$$\mathbf{s}_{N'} = R(T) \mathbf{s}_0 = \left( \sum_{i=0}^{n-1} c_i T^i \right) \mathbf{s}_0 = \sum_{i=0}^{n-1} c_i (T^i \mathbf{s}_0)$$

ここで、$`T^i \mathbf{s}_0`$ は初期状態から $i$ ステップ進めた状態に対応します。
各 $T^i \mathbf{s}_0$ は、提供された `next()` 関数を $i$ 回呼び出すだけで得られます。したがって、多項式の係数 $c_i$ が $1$ であるステップの状態のみを、変数にXORで足し合わせていけば、最終的な状態 $`\mathbf{s}_{N'}`$ が完全に復元されます。

計算が完了した $`\mathbf{s}_{N'}`$ を用いて、`expected`とのXORを取ることで、元のフラグがデコードされます。

あと全然関係ないですが、色々調べている中で僕のハンドルネームに似ている`xoroshiro`という擬似乱数が出てきてちょっと嬉しかったです。

<details><summary>Solver</summary>

```sage
n = 521
mask = (1 << n) - 1

def next_state(state):
    state ^^= (state << 105) & mask
    state ^^= state >> 53
    state ^^= (state << 337) & mask
    return state

F = GF(2)
I = matrix.identity(F, n)

L_105 = matrix(F, n, n, {(j + 105, j): 1 for j in range(n - 105)})
R_53 = matrix(F, n, n, {(j - 53, j): 1 for j in range(53, n)})
L_337 = matrix(F, n, n, {(j + 337, j): 1 for j in range(n - 337)})

T =  (I + L_337) * (I + R_53) * (I + L_105)

# 特性多項式
P = T.charpoly('x')
R = PolynomialRing(F, 'x')
x = R.gen()

period = (1 << 521) - 1
N_prime = pow(521, 521*521, period)

poly_N = pow(x, N_prime, P)

state = 521
state2 = 0

for c in poly_N.list():
    if c == 1:
        state2 ^^= state
    state = next_state(state)

state = state2

expected = bytes.fromhex("01dadc95cc4ad53980f0bfa25eb55bbea8590cc11c12f9922fd3783e0b4ba33846cd11520a0a3fb8b4905c996d")
flag = bytearray()
for i in range(len(expected)):
    flag.append(expected[i] ^^ (state & 0xFF))
    state = next_state(state)

print(flag.decode())

```
</details>

## / Reference

* [1] びりあるの研究ノート. Google Chromeが採用した、擬似乱数生成アルゴリズム「xorshift」の数理. https://blog.visvirial.com/articles/575 
* [2] Marsaglia, G. 2003. Xorshift RNGs. Journal of Statistical Software. 8, 14 (Jul. 2003), 1–6. DOI:https://doi.org/10.18637/jss.v008.i14.