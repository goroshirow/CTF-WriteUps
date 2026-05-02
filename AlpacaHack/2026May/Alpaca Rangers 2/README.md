# Alpaca Rangers 2

## / Overview

ディレクトリトラバーサル

## / Writeup

Webサイトにアクセスし，[Red](http://34.170.146.252:25651/member?img=red.png)をクリックしたときのURLが

```
http://34.170.146.252:25651/member?img=red.png

```

になっています．`red.png`でファイル指定をしているということはここにフラグのファイルパスを入れたら`Alpaca{...}`が出てくるんじゃないでしょうか．

`app.py`をみるとパスの指定は`path = "./images/" + path`と実装されているので，`/app/images/`から`/flag.txt`を指定するには`../../flag.txt`を入力すれば良いということが分かります．

ただし直前の`path = path.replace("../", "")`によって`../`がサニタイズされてしまします．じゃあ，それを見越して`....//....//flag.txt`にしましょう．二重にはチェックされないのでこれでフラグにたどり着けます．

```sh
$ curl http://34.170.146.252:25651/member?img=....//....//flag.txt
Alpaca{...}
```