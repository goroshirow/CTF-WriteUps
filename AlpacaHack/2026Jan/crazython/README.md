# crazython

## / Overview

正しいエンコーディングから元のコードを抽出する。

## / Writeup

圧縮されたPythonコードがバイト列として与えられている。それを `zlib` で展開し、`exec`関数でそのまま実行している。

`exec`関数を`print`関数に変えれば中身を参照できそうだが、一筋縄ではいかない。

`bytes`関数の末尾を見るとバイト列は `L1` というエンコーディング方式によって表示されているため、例えば `UTF-8` で上書き保存するとバイト列ごと書き換わってしまう。

[pythonのcodecs](https://docs.python.org/ja/3/library/codecs.html)を確認すると次のような記載がある。

| codec | 別名 |
|---|---|
|latin_1|iso-8859-1, iso8859-1, 8859, cp819, latin, latin1, L1|

筆者の環境(VSCode)には`Western (ISO 8859-1)`が用意されているため、スクリプトをこのエンコーディング方式で開き直してから、`exec`関数を`print`関数に変えれば本当のスクリプトが表示される。

```python
import hashlib
import re
h = ["""省略"""]
flag = input("enter flag: ").strip()
if not re.fullmatch(r"Alpaca\{[a-z_]{66}\}", flag): print("invalid format :(")
else:
    flag = flag[7:-1]
    for i in range(66):
        if hashlib.sha256(flag[i].encode()).hexdigest() != h[i]:
            print("wrong :(")
            break
    else:
        print("correct!")

```

配列`h`の各要素は`[a-z_]`いずれかのsha256ハッシュを取っているだけなので先頭から順番に総当りしていけば良い。