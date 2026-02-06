---
title: "Daily Alpacahack The World Writeup"
tags: ["Misc", ".sh"]
---

# The World

## / Overview

エラーに変数が展開されることを利用

## / Writeup

UNIX時間の誤差を`[Warmup]`で100秒以内、`[Impossible]`で100ナノ秒以内におさめる必要があります。一旦正攻法で解けるか次のスクリプトで試します。

```python
from pwn import *
import time

p = remote("34.170.146.252", 23758)

p.recvuntil(b"[Warmup] current time (seconds)?")
t = int(time.time())
p.sendline(str(t).encode())
p.recvuntil(b"[Impossible] current time (nanoseconds)?")
t2 = int(time.time_ns())
p.sendline(str(t2).encode())
p.interactive()
```

試すと分かりますが、9桁くらい合いません。しかも毎回ランダムに近い挙動を示すので、帳尻を合わせることも難しそうです。

次に`[Impossible]`の部分は自分で入力するようにスクリプトを変更して、色々実験していると`d1`と入力したときにエラーにならずに実行されることに気が付きました。

これは`d1`が文字ではなく変数として評価されたからだと推測して、今度は直接`FLAG`と入力したところ、エラー出力の中に変数展開されたフラグが出てきました。