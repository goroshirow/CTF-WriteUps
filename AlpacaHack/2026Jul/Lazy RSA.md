# Lazy RSA

## / Overview

因数分解を用いたRSAのp,q解読

## / Writeup

通常のRSA暗号化プロセスに加えて、$`\text{hint} = 12345p + 6789q`$の情報が与えられています。

$`p`$ と $`q`$ の線形結合が与えられている場合、因数分解することで元の値を知ることができます。具体的には以下の様な関数を考えます。

$$
\begin{align*}
    f(x) &= x^2 - \text{hint} \cdot x + 12345 \cdot 6789 \cdot n \\
         &= x^2 - (12345p + 6789q)x + 12345 \cdot 6789pq \\
         &= (x - 12345p)(x - 6789q)
\end{align*}
$$

この関数の解は $`12345p`$ と  $`6789q`$ であるため、出てきた解の内 $`12345`$ で割った値が整数になる方が $`p`$ であり、もう一方を $`6789`$ で割った値が $`q`$ になります。

この因数分解を使った手法を再現するために、SageMathを使って実装します。

<details> <summary> solver </summary>

```sage
from Crypto.Util.number import long_to_bytes
n = # snip
e = # snip
c = # snip
hint = # snip
R.<x> = QQ[]
F = factor(x^2 + hint*x + 12345*6789*n)

q, _ = F[0]
p, _ = F[1]
p = int(p.constant_coefficient() / 12345)
q = int(q.constant_coefficient() / 6789)

phi = (p-1)*(q-1)
d = pow(e, -1, phi)
m_dec = pow(c, d, n)
print(long_to_bytes(m_dec))
```

</details>