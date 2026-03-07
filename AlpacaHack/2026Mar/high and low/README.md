# high and low

## / Overview

擬似乱数生成器の解読

## / Writeup

この問題で使われる擬似乱数生成器は、要素数624個の32ビット乱数配列`state`と初期値`p=0`を用いて`next_value`関数を呼び出す度に以下の処理を実行します。

1. `state`の`p`, `p+1`, `p+397`番目の要素から`x`という値を計算する
2. `state`の`p`番目の要素に`x`を代入する
3. `p`をインクリメントする
4. `x`から疑似乱数`y`を計算する

`x`, `y`の計算ロジックは配布されたファイルから分かっているのですが、`state`の初期の乱数は分かりません。

この問題のポイントは`y`から`x`を逆算できることです。4.の計算は具体的に以下のようになっています。

```py
y = ((x >> 11) | ((x << 21) & 0xFFFFF800)) ^ 0xDEADBEEF
# マスクする値は0xFFE00000でも良い気がします
```

`x`の上位21ビットと下位11ビットを交換してから`0xDEADBEEF`とXORして`y`としています。つまりその逆は`y`と`0xDEADBEEF`をXORして上位11ビットと下位21ビットを交換することです。

```py
x = y ^ 0xDEADBEEF
x = ((x >> 21) | ((x << 11) & 0xFFFFF800))
```

`x`が分かったということは、2.で更新される`state[p]`の値が分かります。つまり、次にこの数を使うときは`y`の値を完全に予想できます。`next_value`関数を呼び出すごとに`p`がインクリメントされて、既知の`state[p]`の要素も増えていきます。

ソルバでは312ゲームをとりあえず回して`state`の要素全てを既知にします。その後は`next`の値を手元で計算できるので正確に high and low を当て続けることが出来ます。

## / Solver

```py
from pwn import *

N = 624
p = remote('34.170.146.252', 6881)

def dec(y):
    x = y ^ 0xDEADBEEF
    x = ((x >> 21) | ((x << 11) & 0xFFFFF800))
    return x

def next_value(current, state):
        p, q, r = current, (current+1) % N, (current + 397) % N
        a = state[p] & 0x80000000
        b = state[q] & 0x7fffffff
        x = (a | b) ^ state[r]
        y = ((x >> 11) | ((x << 21) & 0xFFFFF800)) ^ 0xDEADBEEF
        return y

state = [0 for _ in range(N)]

current = 0
while True:
    p.recvuntil(b'money: ')
    money = int(p.recvline().strip())
    print(f'current: {current}, money: {money}')
    if money > 1337:
        print(p.recvall())
    p.recvuntil(b'value: ')
    value = int(p.recvline().strip())
    print(f'value: {value}, est: {next_value(current, state)}')  
    p.recvuntil(b'high or low?')
    
    if value < next_value((current+1) % N, state):
        p.sendline(b'h')
    else:
        p.sendline(b'l')
    
    p.recvuntil(b'next: ')
    next = int(p.recvline().strip())
    state[current] = dec(value)
    state[(current+1) % N] = dec(next)
    current = (current + 2) % N

```