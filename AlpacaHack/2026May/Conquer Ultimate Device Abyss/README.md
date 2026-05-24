# Conquer Ultimate Device Abyss

## / Overview

CUDAで書かれた暗号ロジックの解読

## / Writeup

このチャレンジでは T4 GPU で動作する実行ファイル`chal_sm_75`と 6000 Ada で動作する`chal_sm_89`、それらのソースコード`chal.cu`が配布されます。.cuとはCUDAのソースコードファイルの拡張子であり、中身はC言語ライクに記述されています。

CUDAはNVIDIAが開発したGPU計算に特化したプラットフォームです。並列計算を高速に行えるため、単純な計算を大量に行う深層学習にも使われています。pythonで機械学習をする方であれば`device=torch.device('cuda')`などと書いたことがあるのではないでしょうか。

問題に戻って`chal.cu`を見てみますと、4x4の配列`B`, `C`, `flag`とユーザの入力`A`に対して以下のロジックでフラグの正誤判定を行っています。

```c
flag == compute(12, A, B, 29, C)
```

なお、ここでは CPU と GPU 間での変数の受け渡しは省略することでロジックを見やすくしています。実際のソースコードでは接頭辞`d_`が付く変数が GPU の変数に対応しています。

では次に`compute()`を見てみます。

```c
__global__ void compute(int a, int *b, long *c, int d, long *e)
{
    int f = threadIdx.y;
    int g = threadIdx.x;

    if (f < SIZE && g < SIZE)
    {
        long h = 0;
        for (int i = 0; i < SIZE; i++)
        {
            h += (long)b[f * SIZE + i] * c[i * SIZE + g];
        }
        e[f * SIZE + g] = (long)a * h + (long)d * e[f * SIZE + g];
    }
}
```

これがCUDAの特別な書き方で、`threadTdx`を用いると`f`, `g`が0からSIZE-1までの場合を並列でまとめて計算してくれます。C言語で書き換えるとこうなります。

```c
__global__ void compute(int a, int *b, long *c, int d, long *e)
{
    for (int f = 0; f < SIZE; f++)
    {
        for (int g = 0; g < SIZE; g++)
        {
            long h = 0;
            for (int i = 0; i < SIZE; i++)
            {
                h += (long)b[f * SIZE + i] * c[i * SIZE + g];
            }
            e[f * SIZE + g] = (long)a * h + (long)d * e[f * SIZE + g];
        }
    }
}
```

この関数を見ると`f`は2次元配列の行、`g`は列に対応していることが分かります。さらに`SIZE`を`S`として`h`を展開すると

$$e[f*S + g] = a(\sum_{i=0}^{S-1} b[f * S + i] * c[i * S + g]) + d \cdot e[f*S + g]$$

と表せます。これは(`b`の`f`行)と(`c`の`g`列)の積の`a`倍を(`e`の`f`行`g`列)の`d`倍を足しているので以下のような以下のような行列積で表せます。(行列と分かりやすいように大文字で表しています)

$$E = a(BC) + dE$$

実際の入力はややこしいですが`(a,b,c,d,e)=(12,A,B,29,C)`なので、これが`flag`と一致する時

$$FLAG = 12(AB) + 29C$$

が成り立ちます。このときの入力`A`が答えなので、式変形により`A`を逆算します。

$$A = (FLAG - 29C)\cdot B^{-1}/12$$

あとはこれをpythonで実装するだけなのですが、1つ目の注意点として、`A`の計算結果をそのままintにキャストすると計算精度の問題でフラグの一部の文字が前後してしまいます。これは四捨五入することで解決します。2つ目に`A`の左上の要素から右に`long_to_bytes`して末尾に追加する実装だと、エンディアンの影響でフラグが4バイトずつ逆に出力されます。`.to_bytes(4, byteorder='little')` でエンディアンを指定してあげましょう。

## / Solver

```py
import numpy as np

flag = [
    [0x00000ee698dea1b1, 0x00000e9dd071a07b, 0x00000c1924ac2e63, 0x00000db7c6567969],
    [0x00000cf7dca22a8d, 0x00000d361500d93b, 0x00000a4b9a1df377, 0x00000c43dffefdad],
    [0x000010b0871e1f25, 0x0000108db4c64da3, 0x00000c9baca0e87f, 0x0000100afc00a4b1],
    [0x00000f83590cad41, 0x00000ead68311d37, 0x00000bf80ff254c3, 0x00000e85f5468875]
]

B = [
    [0xde, 0xad, 0xbe, 0xaf],
    [0xab, 0xad, 0x1d, 0xea],
    [0xca, 0xfe, 0xba, 0xbe],
    [0xfe, 0xed, 0xfa, 0xce]]

C = [
    [0x61706c41, 0x61486163, 0x44206b63, 0x796c6961],
    [0x61706c41, 0x61486163, 0x44206b63, 0x796c6961],
    [0x61706c41, 0x61486163, 0x44206b63, 0x796c6961],
    [0x61706c41, 0x61486163, 0x44206b63, 0x796c6961]]

flag = np.array(flag)
B = np.array(B)
C = np.array(C)

a = 12
d = 29

B_inv = np.linalg.inv(B)
Input = np.round(np.matmul((flag - d * C) // a, B_inv)).astype(np.int32)

answer = b''

for line in Input:
    for i in line:
        i = int(i)
        answer += i.to_bytes(4, byteorder='little')

print(f"{answer = }")
```