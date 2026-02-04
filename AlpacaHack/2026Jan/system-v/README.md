# system-v

## / Overview

C言語の`SIMD`処理によるフラグ判定を解読する。

## / Writeup

フラグ判定プログラム`chal.c`はArm SVE (Scalable Vector Extensions) 命令セットという、聞き慣れない命令によって記述されています。問題を解く上では**データを並列に処理する**ための命令セットと理解しておけばいいと思っています。

> 詳しく知りたい方向けの外部記事
> https://eetimes.itmedia.co.jp/ee/articles/1608/25/news036.html

ということでフラグ判定のロジックを紐解いていきましょう。まずは使われている各命令についての理解からです。

ヒントにもあるように、[こちら](https://developer.arm.com/architectures/instruction-sets/intrinsics)のサイトで詳細を調べることは出来ますがめんどくさいと思いますので、ここでまとめます。

### Arm SVE 命令セット

#### 型定義
* `svuint16_t`, `svuint64_t`: それぞれ16ビット整数、64ビット整数の配列
* `svbool_t`: ベクトルの各要素が計算対象か否かを制御するためのマスク

#### 初期化
* `svdup_n_u16(uint16_t op)`: 全ての要素が`op`の値でベクトルを生成。[op, op, ..., op]
* `svptrue_b16()`, `svptrue_b64()`: 全ての要素がTrueであるマスクを生成。
* `svld1_u16(svbool_t pg, const uint16_t *base)`: マスクである`pg`がTrueの要素をメモリ`base`からベクトルレジスタにロード。(配列をベクトル変数に変換)
* `svst1_u16(svbool_t pg, uint16_t *base, svuint16_t data)`: マスク`pg`がTrueの要素をベクトルレジスタからメモリ`base`に書き戻す。(ベクトル変数から配列に変換)
* `svcntd()`: 実行しているハードウェアのベクトルレジスタに格納できる64ビット整数の最大数。

#### 演算
* `svmla_u16_m(svbool_t pg, svuint16_t op1, svuint16_t op2, svuint16_t op3)`: マスク`pg`がTrueの要素は$`op1[i]+op2[i]\times op3[i]`$, Falseの要素は$`op1[i]`$を計算する。

#### 比較
* `svcmpne_n_u16(svbool_t pg, svuint16_t op1, uint16_t op2)`: マスク`pg`がTrueのベクトル `op1` の各要素とスカラ `op2` を比較し、等しくない場合にTrueとなるマスクを生成。
* `svcmpeq_u64(svbool_t pg, svuint64_t op1, svuint64_t op2)`: マスク`pg`がTrueの2つのベクトルを比較し、等しい要素をTrueとするマスクを生成。
* `svand_b_z(svbool_t pg, svbool_t op1, svbool_t op2)`: マスク`pg`がTrueの `op1`, `op2` の各要素に論理積を取る。
* `svnot_b_z(svbool_t pg, svbool_t op)`: マスク`pg`がTrueの`op`のbool要素を反転させる。
* `svptest_any(svbool_t pg, svbool_t op)`: マスク`pg`がTrueの`op`の要素に一つでもTrueが含まれているか判定。

また、ベクトルの要素数については Scalable Vector Extensions の名前の通り、ハードウェアのベクトル長 (VL) によって決まります。しかし、今回は実行方法が
```bash
qemu-aarch64 -cpu max,sve=on,sve128=on ./chal
```
で固定されており、VLはどの環境でも128ビットになります。つまりu16の場合は128/16=8, u64の場合は128/64=2がベクトルの要素数となります。このことから`svcntd()`は2であると分かります。

### 解読
まずは`micro_kernelA`関数が何をしているのか調べましょう。先程の命令と見比べると、**activeがTrueの要素 i に対して$`array[i]+(0x1dea)\times(0xcafe)`$をして、元のarrayに戻す**関数であることが分かります。

さらに`main`関数の34行目からのループ処理を見ると、詳しい処理は追いませんが、`buf`の各要素に、何か**決定的**な`active`の条件をもとに、`micro_kernelA`関数を適用していることが分かります。

また、このループ以降のコードは処理後の`buf`と`flag`が一致しているかを調べているだけです。

**決定的**に`active`が決まるということは、`flag`に対して34行目からのループを使って、`micro_kernelA`の逆関数を適用すれば、正解となる入力が得られるということです。`svmla_u16_m`を、$`array[i]-(0x1dea)\times(0xcafe)`$を行う`svmls_u16_m`に差し替えて、`buf`に`flag`を代入すればフラグが復元されます。