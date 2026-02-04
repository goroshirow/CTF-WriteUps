# ToyPQC

## / Overview

LWE問題を誤差項の総当りで解く

## / Writeup

LWE問題とは「誤差が混じった連立一次方程式を解くのは、めちゃくちゃ難しい」という問題です。この問題は量子コンピュータでも解くことが難しい格子暗号の一種として利用されています。(Post-Quantum Cryptography, PQC)

問題 `chal.sage` は次のように暗号化しています。

$\boldsymbol{b} = \boldsymbol{A} \cdot \boldsymbol{s} + \boldsymbol{e}$

`A`(行列), `b`(ベクトル)は公開情報で、`s`(ベクトル)を求めることがゴールです。

本来、誤差項は誤差ベクトル `e` は離散ガウス分布からのサンプリングされた値で構成されます。更に式の数も多いため、総当たりで `e` を特定することは難しいです。しかし今回の場合は `e` は 0 か 1 のどちらかであり、式の数も 10 本であるため、1024個の総当りをすれば

$`\boldsymbol{s}=\boldsymbol{A}^{-1}(\boldsymbol{b}-\boldsymbol{e})`$

として、正しい `s` が復号されます。