# curl as a service 2

## / Overview

curlの GOPHER URL を使ったデータ送信

## / Writeup

Dockerで`frontend`と`secret`というサーバが建てられています。ユーザは`frontend`のWebサイトから`curl --silent --show-error --insecure <URL>`を実行できます。入力できるのは`<URL>`の部分だけで、`secret`にある`/flag-xxx`を表示させなければなりません。`xxx`は予測不可能な文字列です。

普段`curl`は`http`や`https`のサイト情報を取得するために使いますが、実は色々なプロトコルに対して使用することができます。

```
DICT, FILE, FTP, FTPS, GOPHER, GOPHERS, HTTP, HTTPS, IMAP, IMAPS, LDAP, LDAPS, MQTT, MQTTS, POP3, POP3S, RTSP, SCP, SFTP, SMB, SMBS, SMTP, SMTPS, TELNET, TFTP, WS and WSS
```

今回のチャレンジでは`secret`の1337番ポートが開いていて、ここに`Give me a flag`を送信するとフラグが返ってきます。

さて、先程のプロトコルの中で使用するのは`GOPHER`です。`GOPHER`は`gopher://<HOST>:<PORT>/-<送りたいデータ>`の形で指定したポートに任意のデータを送りつけることができます。

`secret`の`1337`に対して`Give me a flag`を送りたければ、空白を`%20`に変更して以下のように送信できます[[1]](https://www.docswell.com/s/hasegawa/VZGWQK-SSRF#p16)。

```
URL: gopher://secret:1337/-Give%20me%20a%20flag

Output:
What is your wish?Your wish: Give me a flag
Sure! Here is the flag!
Alpaca{...}

```
