# Super Short Python Golf

## / Overview

`help()`を使ったPyjail

## / Writeup

6バイト以下の文字列が`eval()`で評価されます。フラグは`ALPACA_FLAG = os.environ.get("FLAG", "Alpaca{dummy}")`として変数に保存されています。

`eval()`はpythonの変数や関数を評価しますが、`ALPACA_FLAG`は文字数制限に引っかかります。なので6文字以下で呼び出せる関数がないか組み込み関数の`__builtins__`と`os`ライブラリの両面から調べます。

`os`は関数を呼び出すために`os.`を付ける必要があり、実質的に3文字しか使えないため厳しそうです。一方で、`__builtins__`のドキュメンテーションには`help()`や`vars()`といった条件を満たす関数がありました。中でも`help()`は対話的に呼び出すことができ、関数のヘルプを調べることができるようです。

この`help()`を使ったPyjailは有名らしく、たくさんのWriteupが見つかります。ページャー機能を使ったRCEの問題もあるようですが、今回は`__main__`を使う解き方のようです。`__main__`を指定するとメイン関数で定義されている変数が見れます。この中に`ALPACA_FLAG`も含まれていました。

```sh
$ nc 34.170.146.252 55149
code > help()

help> __main__
Help on module __main__:

NAME
    __main__

DATA
    ALPACA_FLAG = 'Alpaca{...}'
    code = 'help()'

FILE
    /app/jail.py
```