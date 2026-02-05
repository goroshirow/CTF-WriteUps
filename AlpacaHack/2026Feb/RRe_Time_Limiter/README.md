---
title: "Daily Alpacahack Inu Profile Writeup"
tags: ["Crypto", "CRT"]
---

# RRe_Time_Limiter

## / Overview

中国人剰余定理を用いた復号

## / Writeup

$$x \equiv a_i \pmod{n_i} \qquad (i=1,2,...k)$$

が与えられる時、nの積$`N=n_1 n_2 \cdots n_k`$から$`m_i =N/n_i`$ を定義して、$`m_i^{-1}`$を法$`n_i`$での$`m_i`$のモジュラ逆元とすると

$$x = \sum_{i=1}^{k} a_i m_i m_i^{-1}$$

で元のxが復元できます。

なぜならxを$`n_i`$で割ったあまりを考えると、第$`i`$項以外は$`n_i`$の倍数なので0になり、$`a_i m_i m_i^{-1} \equiv a_i \pmod{n_i}`$ となります。

## / Solver

```python
N = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 331, 337, 347, 349]
A = [1, 2, 0, 4, 8, 9, 8, 13, 16, 27, 0, 17, 17, 28, 20, 6, 28, 4, 47, 30, 37, 56, 57, 77, 35, 57, 89, 70, 27, 26, 108, 124, 25, 75, 122, 54, 64, 42, 158, 25, 68, 90, 89, 42, 90, 147, 124, 148, 225, 50, 182, 5, 162, 159, 252, 129, 145, 24, 119, 41, 215, 264, 299, 51, 203, 24, 18, 38, 55, 266]

from Crypto.Util.number import long_to_bytes

def CRTinv(A, N):
    N_total = 1
    x = 0
    for n in N:
        N_total *= n
    
    for a, n in zip(A, N):
        m = N_total // n
        inv = pow(m, -1, n)
        x += a * m * inv
    return x % N_total

flag_num = CRTinv(A, N)
flag = long_to_bytes(flag_num)
print(flag)
```