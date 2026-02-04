# jailiaj

## / Overview

回文でローカルファイル`flag.txt`を表示するpythonコードを作る。

## / Writeup

回文とは、反対から読んでも同じ文のことで次のような例がある。
```
来てもよい頃だろ、来いよモテ期
```

pythonで意味のある回文を作るには`#`を使えば良い。何か実行したい`<script>`に対して、
```
<script> # >tpircs<
```
でRCEが可能である。`<script>`を`print(open('flag.txt', 'r').read())`に書き換えることでフラグを抽出できる。

