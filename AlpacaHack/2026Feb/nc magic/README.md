---
title: "Daily Alpacahack nc magic Writeup"
tags: ["nc", "Misc"]
---

# AAAAAAAAEEEEEEEESSSSSSSS

## / Overview

改行を含まないデータの送信

## / Writeup

サーバーに接続すると次のメッセージが表示されます。

```
Just send back 6e877aaf8f5c679e1d2bde6f71b8c56a ... but can you?
```

このランダムな16進数 `secret` を送り返せばフラグが得られるらしいのですが、普通に入力しても一致しません。理由を調べるためにデバッグを追加した `server.py` をdockerで起動させます。入力は次のように解釈されていました。

```py
b'6e877aaf8f5c679e1d2bde6f71b8c56a\n'
```

つまり改行が邪魔なわけですが、どのように取り除けるでしょうか。

答えは入力を32バイトに制限することです。これを実現するためには`head`コマンドを使います。`-c`オプションを付ければ送信するバイト数を指定できます。

```sh
head -c 32 | nc 34.170.146.252 48683
```

しかし、このまま送信してもなんの応答も返ってきません。理由がわからなかったので試行錯誤していると、問題文がヒントになっていることに気が付きました。

> What kind of cat is netcat?

`man nc` でオプションを探していると `-N` の説明に興味深いものを見つけました。

```
-N      shutdown(2)  the  network socket after EOF on the in‐
        put.  Some servers require this to finish their work.
```

「サーバーによっては`-N`がないと通信が完了しないよ」ということなので追加してみるとフラグが取れました。

## / solver

```sh
head -c 32 | nc -N 34.170.146.252 48683
```