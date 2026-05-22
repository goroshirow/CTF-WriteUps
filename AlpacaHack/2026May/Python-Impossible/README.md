# Python:Impossible

## / Overview

環境変数で`assert`無効

## / Writeup

ユーザは`name`, `value`, `arg`の３つを入力すると、サブプロセスで環境変数に`name: value`がセットされた状態で、`python3 chall.py arg`が実行されます。

`chall.py`で`arg`は整数`n`に変換されますが、絶対回避できないアサーション

```py
assert n > 0
assert n < 0
```

が待ち構えていて、その後にあるフラグにたどり着けません。

環境変数を使って`assert`を無効化するために`python assert 無効 環境変数`と調べると、環境変数`PYTHONOPTIMIZE`に`1`を設定すれば良いことが分かりました[[1]](https://codezine.jp/article/detail/12179)。

したがって以下の手順でクリアできます。

```sh
$ nc 34.170.146.252 12527
env> PYTHONOPTIMIZE=1
arg> 0 # 何でも良い
Alpaca{...}
```