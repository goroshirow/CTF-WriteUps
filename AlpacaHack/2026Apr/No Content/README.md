# No Content

## / Overview
明示されたContent-Lengthの無視

## / Writeup
このチャレンジでは、HTTPレスポンスとしてボディにフラグがセットされているのにもかかわらず、意図的にContent-Lengthを0に設定してステータスコード402を返すプログラムが稼働しています。

ブラウザやcurlコマンドでレスポンスボディを見たいのですが、Content-Lengthが0の時点でボディの内容は無視されてしまうようです。そこで`nc`コマンドを使います。これはヘッダの内容お構いなしに全ての通信内容を表示してくれるのでフラグの内容も表示できるはずです。

```sh
$ nc 34.170.146.252 48487
GET / HTTP/1.1

HTTP/1.0 204 No Content
Server: BaseHTTP/0.6 Python/3.14.2
Date: Tue, 07 Apr 2026 06:54:18 GMT
Content-Type: text/plain; charset=utf-8
Content-Length: 0

Alpaca{Plz_d0nt_no7_ignor3_RFC9110}
```

見事フラグを表示させることが出来ました。