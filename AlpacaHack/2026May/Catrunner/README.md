# Catrunner

## / Overview

os.path.join()のパス解釈の利用

## / Writeup

入力値`filename`が`os.path.join("/app", filename)`として`/app`の後に結合されます。フラグは`/flag.txt`にあるのでパストラバーサルを考えて`filename`に`../flag.txt`を入力して結合したいところですが、文字列中の`..`は検出されアサーションが出ます。

`os.path.join()`について調べると、`/`から始まるパスは常にルートディレクトリとして扱われるという仕様であることが分かりました。つまり`os.path.join("/A", "/B")`は`/B`として認識されます。

これを今回のチャレンジに適用すると、`/flag.txt`を入力した時に前の`/app`は無視されてファイルを開くことができます。