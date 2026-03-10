# 100

## / Overview

色々なバリエーションの100

## / Writeup

次のようなassertに引っかからない文字列を100個見つけます。

```py
assert l00.isascii()
assert len(l00) <= 10.0
assert l00 not in I00
assert int(l00) == 100
```

`int()`関数で100と評価される文字列を探すことが目的なので[公式ドキュメント](https://docs.python.org/3/library/functions.html#int)を見てみます。次の一文がヒントになりそうです。

> Optionally, the string can be preceded by + or - (with no space in between), have leading zeros, be surrounded by whitespace, and have single underscores interspersed between digits.

- `+`を接頭語に使える
- 先頭に0をいくつでもつけて良い
- 数字の間に`_`を入れて良い

ということで、今回の条件を満たす数として例えば`+00_10_0`とかも考えられるわけです。後はassert文と、先程のルールを満たす文字列を考えると、全部で225個あります。その中から100個選んで送りましょう。

## / Solver

```py
from pwn import *

p = remote('34.170.146.252', 23793)

payloads = ['100', '10_0', '1_00', '1_0_0']

prefixs = ['', '+']
def PrependZero(prefix):
    prefix = prefix + '0'
    if len(prefix) > 7:
        return
    prefixs.append(prefix)
    PrependZero(prefix)
    PrependZero_(prefix)

def PrependZero_(prefix):
    prefix = prefix + '0_'
    if len(prefix) > 7:
        return
    prefixs.append(prefix)
    PrependZero(prefix)
    PrependZero_(prefix)
    
PrependZero('')
PrependZero_('')
PrependZero('+')
PrependZero_('+')

payloads = [x + y for x in prefixs for y in payloads if len(x + y) <= 10]
print(payloads)

for i, payload in enumerate(payloads):
    p.sendlineafter(b'100? ', payload.encode())
    if i >= 99:
        break
p.interactive()
```