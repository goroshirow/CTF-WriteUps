# super_simultaneous_equations

## / Overview

消去定理を用いた連立多項式方程式の簡約化

## / Writeup

> 本Writeupはグレブナー基底を初学者である私が解釈するために，本当は正しくない表現をいくつか用いています．正確な理解のためには後述の参考文献やSageMathの実装を詳しく調べることをおすすめします．

解法は非常にシンプルです．`Solver`でも示す通り，[SageMathの公式ドキュメント](https://doc.sagemath.org/html/en/reference/polynomial_rings/sage/rings/polynomial/multi_polynomial_ideal.html)からグレブナー基底を求めるプログラムに書き換えるだけです．具体的には連立方程式の配列をイデアルにした後，`groebner_basis()`メソッドを呼び出すと結果が出ます．

これだけだと物足りないので，もう少し深堀りしてグレブナー基底について調べてみます．

グレブナー基底を求めるアルゴリズムの一つにブッフバーガーアルゴリズムがあります．これは誤解を恐れずに言うと線形連立方程式の**ガウスの消去法**を非線形連立方程式でも使えるようにしたものです．普通の線形連立方程式の場合は，変数が入り混じった連立方程式を簡約化することで答えを求めていましたが，今回は多変数多項式からなる非線形連立方程式をブッフバーガーアルゴリズムで簡約化することで答えを求めます．つまりブッフバーガーアルゴリズムで求められるグレブナー基底は「非線形連立方程式を簡約化した式の集まり」と解釈することが出来ます．そのため，これらの基底が0になる連立方程式を解くことは元の連立方程式を解いた結果と一致します．

ただし，数学的な定義としては全く正しくないので正確な定義については、参考にした以下の資料をご覧ください．

> グレブナー基底
>
> https://www.math.kyoto-u.ac.jp/~kino2013/houkoku/kino2013_aoyama_toru.pdf

余談ですが，調べていて一番興味深かったのが，2003年にグレブナー基底を求める`F5アルゴリズム`を用いて，PQCの有力候補だった多変数多項式暗号であるHFE暗号を破ったという論文を見つけたことです．もし興味があれば`Algebraic cryptanalysis of hidden field equation (HFE) cryptosystems using Gröbner bases`で見てみてください．

## / Solver

```sage
# 2**64 で余りを取るという意味
# Define a ring to perform calculations modulo 2^64.
Ring = Zmod(2**64)

# 自動的に 2**64 で余りを取る変数x0~x4を生成すると言う意味
# Define a polynomial ring with 5 variables (x0-x4) over the modulo ring.
Poly.<x0,x1,x2,x3,x4> = PolynomialRing(Ring, 'x', 5)

# 目標: このすべての式を0にするx0~x4を見つけてください
# Goal: Find the values of x0 to x4 that satisfy all of these equations (make them equal to 0).
I = ideal(...省略...).groebner_basis()

print(I)
```