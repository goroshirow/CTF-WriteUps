# Useful Machine

## 概要

`program`とそれを読み込んで命令を実行する`vm.py`が与えられます．

`vm.py`は`program`を3バイトずつ`opcode`,`operand1`.`operand2`として解釈して以下のことを実行します．

| Opcode | 動作内容 |
|------:|---------|
| 0 | 入力1文字を読み込み、ASCII値を `mem[oprand1]` に格納 |
| 1 | `oprand2` を `mem[oprand1]` に格納 |
| 2 | `mem[oprand2]` の値を `mem[oprand1]` にコピー |
| 3 | `mem[oprand1]` に `mem[oprand1]` + `mem[oprand2]` を加算（mod 256） |
| 4 | `mem[oprand1]` に `mem[oprand1]` × `mem[oprand2]` を乗算（mod 256） |
| 5 | `mem[oprand1]` に `mem[oprand1]` XOR `mem[oprand2]` を格納 |
| 6 | `mem[oprand1]` が 1 なら 0 に，それ以外なら0に反転 |

入力したフラグが正解なら`Correct flag!`が表示されるみたいです．

## 解法

最初に思いついたのは，出力を逆順にトレースして，入力を復元するという方法でしたが，最後の状態が`mem[0] == 0`ということしか分からないし，一意に定まらない命令が多いので現実的ではありません．

デバック用のコードを追加した[check.py](./check.py)で遊んでいると，次のことを発見しました．

- 同じような命令セットが繰り返されている．
- 正解の入力が続く間は`mem[0] == 1`になる．
- 最後の命令だけ`mem[0]`を反転させている．

これを利用すればフラグがゲットできそうです．`mem[0] == 0`になったら停止して現在のステップ数を返す[sever.py](./sever.py)と，そのサーバーに総当たり攻撃を仕掛ける[solve.py](./solve.py)を用意しました．アルゴリズムは次のとおりです．

1. `flag = ""`とする．
2. `chr(33)`から`chr(126)`を`flag`と結合させて`sever.py`に入力する．
3. 一番長いステップ数を要した文字`c`を`flag = flag + c`で追加
4. `c != '{'`なら2に戻る

これでフラグがゲットできました！

## フラグ
```
Alpaca{Futures_Made_of_Virtual_Machines}
```