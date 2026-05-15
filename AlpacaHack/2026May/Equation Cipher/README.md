# Equation Cipher

## / Overview

SageMathで因数分解。

## / Writeup

チャレンジの内容は次の通りです。

```py
import os

FLAG = os.getenv("FLAG", "Alpaca{REDACTED}")
ps = prime_range(200)
assert len(FLAG) <= len(ps)
var("x")
print(expand(prod(p*x - ord(c) for p, c in zip(ps, FLAG))))
```

これはSageMathで書かれた多項式展開のプログラムで、以下の様な$`x`$に関する多項式が展開されます。

$$\Pi_{i=1}^{n}(p_i x - c_i)$$

ここで$`p_i`$は$`i`$番目の素数を、$`c_i`$はフラグの$`i`$文字目のASCIIコードを表しています。$`n`$はフラグの文字数です。

`output.txt`には展開した結果が保存されているので、因数分解するためのプログラムをSageで実行します。

```py
R.<x> = QQ[]
F = factor(<output.txtの内容>)
print(F)
---
(31610054640417607788145206291543662493274686990) * (x - 36) * (x - 65/2) * (x - 112/5) * (x - 97/7) * (x - 9) * (x - 97/13) * (x - 123/17) * (x - 111/19) * (x - 107/23) * (x - 110/31) * (x - 95/29) * (x - 120/41) * (x - 101/37) * (x - 116/43) * (x - 95/47) * (x - 108/59) * (x - 108/61) * (x - 116/73) * (x - 112/71) * (x - 105/67) * (x - 105/79) * (x - 69/53) * (x - 99/83) * (x - 117/101) * (x - 114/103) * (x - 125/113) * (x - 118/107) * (x - 95/89) * (x - 101/109) * (x - 67/97)
```

展開された式は

$$(\Pi_{i=1}^{n}p_i)\Pi_{i=1}^{n}(x - c_i/p_i)$$

の形になっています。

この時、もし$`c_i/p_i`$が整数なら出力結果は分数の形で表示されません。実際、$`(x - 36)`$と$`(x - 9)`$は整数なので$`c_i`$と$`p_i`$の情報が失われたように見えますが、連続する$`p_1`$から$`p_n`$のなかで出力に含まれていない素数は$`3`$と$`11`$だけであることと、ASCIIコードの性質から$`65 \le c_i \le 125`$であることを用いると$`(x - 108/3)`$と$`(x - 99/11)`$が復元できます。

あとは$`p_i`$を昇順に見たときの$`c_i`$を文字に直せばフラグが復元できます。

## / Solver

```py
import numpy as np

R.<x> = QQ[]
F = factor(<output.txtの内容>)
Consts = [poly.constant_coefficient() for poly, mult in F]
Consts = [str(c) for c in Consts] 
Consts[0] = '-108/3'
Consts[4] = '-99/11'
Consts = np.array([s.split('/') for s in Consts], dtype=int)
sort_indices = np.argsort(Consts[:, 1])
Consts = Consts[sort_indices]
flag = [chr(-c[0]) for c in Consts]
print(flag)
```