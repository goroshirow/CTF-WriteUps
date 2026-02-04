# Paca Paca Authenticator

## / Overview

`AES-CBC` は `IV` に対する `Bit Flipping Attack` で偽装可能。(ただし最初のブロックだけ)

## / Writeup

> 今回の問題を解くのに勉強になった記事はこちらです
>
> https://dev.to/moritzhoeppner/bitflip-attack-on-cbc-change-of-the-iv-6ml

### 暗号の紹介

ブロック暗号の一つであるAESには、ブロックサイズ (16bytes) より大きい平文を扱うためにいくつかの**モード**が用意されています。

> 図解付きの説明
>
> https://ja.wikipedia.org/wiki/%E6%9A%97%E5%8F%B7%E5%88%A9%E7%94%A8%E3%83%A2%E3%83%BC%E3%83%89

今回扱うのはAES-CBCモードです。

![aes-cbc](./img/enc.png)
![aes-cbc](./img/dec.png)

### 問題のおさらい

チャレンジサーバに接続します。

```bash
$ nc 34.170.146.252 13161
[debug] fa6710504947ac4a8f152d72ad6521af
This is your login token: 84ea5dceb80e2b4102a200710793f9985f3ad862d0f53355d508a79b602c751bf3bb8680c5057ad84892e60f7d17e4d6
Oops! I forgot to save the iv, so I can't decrypt the token! Do you know it?
help me>
```

[debug] の後に表示されている値が IV で、token が暗号文に該当します。

help me> の後には IV を入力することで平文を復号してくれる仕組みです。

より詳しい情報を得るために `server.py` を確認しましょう。

```python
from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import AES
import os
import json

# 鍵は128ビットランダムだから特定できなさそう
aes_key = os.urandom(16)
flag = os.environ.get("FLAG", "Alpaca{dummy}")

def register(username, message):
    # data = b'{"name": username, "message": message}'
    data = json.dumps({"name": username, "message": message}).encode()
    cipher = AES.new(aes_key, AES.MODE_CBC)
    token = cipher.encrypt(pad(data, 16))
    # ivが表示される
    print("[debug]", cipher.iv.hex())
    return token

def login(iv, token):
    data = unpad(AES.new(aes_key, AES.MODE_CBC, iv=iv).decrypt(token), 16)
    data = json.loads(data)
    # 復号結果からnameとmessageを取り出す
    return data["name"], data["message"]


token = register("alpaca", "paca paca!")
print("This is your login token:", token.hex())

print("Oops! I forgot to save the iv, so I can't decrypt the token! Do you know it?")
# IVを入力
iv = bytes.fromhex(input("help me> "))

try:
    username, message = login(iv, token)
except Exception as e:
    print("something wrong:", e)
    exit(1)

if username == "alpaca":
    print("paca paca!")
    print("Thanks! That really helped!")
# nameがllamaならフラグゲット
elif username == "llama":
    print("llama!?!!?", flag)
    print("Oh no, I accidentally leaked the flag...")
else:
    print(f"{username}... who are you?")

```

分かっている情報をまとめましょう。

* 平文: `{"name": "alpaca", "message": "paca paca!"}`のバイナリデータ
* IV: `fa6710504947ac4a8f152d72ad6521af`
* 暗号文: `84ea5dceb80e2b4102a200710793f9985f3ad862d0f53355d508a79b602c751bf3bb8680c5057ad84892e60f7d17e4d6`

目標は細工した IV を送信して、復号文を`{"name": "llama", "message": "paca paca!"}`にすることです。

### Bit Flipping Attack

AES-CBCの復号プロセスを見ると、最初のブロックに関しては、 IV と暗号文を XOR することで復号しています。そのため、図の IV の**赤点のビット**を反転させると、復号文の**対応するビット**も反転します。この性質を利用すると**復号文の最初のブロック**を偽造できることが分かります。

これを Bit Flipping Attack と言います。

![aes-cbc](./img/dec-focus.png)

今回の問題で、平文をブロックに分けると改ざんしたい`alpaca`は最初のブロックに入っています。`[s]`はスペースを表す一文字だと思ってください。

* `{"name":[s]"alpaca`
* `",[s]"message":[s]"p`
* `aca[s]paca!"}\x05\x05\x05\x05\x05`

> ※ ascii文字は1byteなので16文字区切りで1ブロック
> 
> ※ `\x05\x05\x05\x05\x05`は平文を 16bytes の倍数にするための PKCS#7 Padding

name を`llama`にしたければ次のように書き換えます。

* `{"name":[s][s]"llama`
* `",[s]"message":[s]"p`
* `aca[s]paca!"}\x05\x05\x05\x05\x05`

`alpaca` から `llama` に変更することで文字数が1つ減るので帳尻を合わせるために `[s]` を２つ入れています。

> json.dump()は複数スペースを入れても1つに整形されるので `solve.py` のように `b'{"name":[s][s]"llama",[s]"message":[s]"paca[s]paca!"}'`を直接書きます。

`b'{"name":[s]"alpaca'`と`b'{"name":[s][s]"llama'`をXORすることで差分 `diff` を計算します。さらに元の IV と diff をXORすることで偽造用の IV を作ることが出来ます。これを16進文字列としてサーバに送信すれば`llama`としてログインできます。


