---
title: "picoCTF hash-only-1 writeup"
tag: ["expliot"]
---

# hash-only-2

## / Overview

間違った`md5sum`を実行させる。

## / Writeup

ホームディレクトリに`flaghasher`がないので探します。

```sh
$ find / -type f | grep flaghasher
/usr/local/bin/flaghasher
```

パスが分かったのでカレントディレクトリにコピーします。

```sh
$ cp /usr/local/bin/flaghasher ./
```

[hash-only-1](../hash-only-1/)と同様に`md5sum`のリンクを`cat`に置き換えたいのですが、環境変数`PATH`が読み取り専用に設定されています。代わりに、`PATH`の中で書き込みの権限があり、2番目に優先度が高い`/usr/local/bin/`に偽の`md5sum`を作成します。

```sh
$ cp /usr/bin/cat /usr/local/bin/md5sum
```

これで`flaghasher`を実行するとフラグがゲットできます。
