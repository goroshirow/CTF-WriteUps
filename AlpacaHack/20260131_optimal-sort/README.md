# optimal-sort

## / Overview

XORスワップの不備

## / Writeup

このチャレンジを解きます。

```python
import secrets, os

FLAG = os.getenv("FLAG", "Alpaca{REDACTED}")


def swap(xs: list[int], i: int, j: int):
    if i == j:
        return
    xs[i] ^= xs[j]
    xs[j] ^= xs[i]
    xs[i] ^= xs[j]


def sort_challenge(xs: list[int]) -> bool:
    limit = len(xs) + 5
    for _ in range(limit):
        i = int(input("i> "))
        j = int(input("j> "))

        print(f"xs[i]: {xs[i]} -> {xs[j]}")
        print(f"xs[j]: {xs[j]} -> {xs[i]}")
        swap(xs, i, j)

        is_sorted = all(x <= y for x, y in zip(xs, xs[1:]))
        print(f"{is_sorted = }")
        if is_sorted:
            return True
    return False


for size in [10, 100, 1000, 2000]:
    print(f"{size = }")
    xs = [secrets.randbelow(2**32) for _ in range(size)]

    if not sort_challenge(xs):
        print("Challenge failed...")
        exit(0)

print("Congratulations! Here's your flag:", FLAG)
```

まず `size` の長さのランダムな配列が与えられます。これを`swap`だけを使って `size`+5 回以内に整列させられるか、という問題です。

数学的に解くことができるか考えてみます。全ての要素を把握するには最低でも `size/2` 回の比較が必要であり、残り `size/2 + 5` 回でどれだけ効率よく交換しても整列させられないケースの方が多いと思います。そのため別の手段を考えます。

もう一度コードをよく見ると、次の部分が引っかかります。
```python
def swap(xs: list[int], i: int, j: int):
    if i == j:
        return
    xs[i] ^= xs[j]
    xs[j] ^= xs[i]
    xs[i] ^= xs[j]
```

`i==j`を禁止している理由は何でしょうか？もしも`i==j`が許可されていたら、この時 `xs[i] == xs[j]` であるため、XORの結果は次のようになります。
```python
xs[i] ^= xs[j]   # xs[i] = 0
xs[j] ^= xs[i]   # xs[i] = 元の値
xs[i] ^= xs[j]   # xs[i] = 0
```

つまりインデックス`i`の値が0になります。これを全てのインデックスに適用すれば、全要素が0になって整列の条件を満たしてしまいます。

ところで、pythonには負の値をインデックスに指定することで、配列を最後尾から指定できる機能があります。これを使えば `i` と `i - size` は同じ要素を指すことになります。よって、`size - 1`回の比較で`0` から `size - 2` まで全要素を 0 に書き換えることが出来ます。(最後の値は0以上なので交換不要)

後はこれを、全ての `size` について繰り返すだけです。