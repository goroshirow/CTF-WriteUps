# Ruby Flag Checker

## / Overview

判定文と疑似素数をXORする。

## / Writeup

与えられたソースコードで重要なのは以下の箇所。

```ruby
Prime::Generator23.new.take(23).zip(STDIN.read(23).bytes).map{|x,y|x^y}.pack("C*")=="Coufhlj@bixm|UF\\JCjP^P<"
```

`Prime::Generator23`について調べると、純粋な素数生成器ではなく**2, 3といずれでも割り切れない整数**を生成するクラスであることが分かる。

> https://docs.ruby-lang.org/ja/latest/class/Prime=3a=3aGenerator23.html

`new`以降について動作は以下の通り。

* `Prime::Generator23`の先頭から23個整数を取って疑似素数配列を作り、
* 入力23文字のASCIIコードと`XOR`を取って、
* `Coufhlj@bixm|UF\\JCjP^P<`と一致するか調べる。

という流れなので逆に、`Coufhlj@bixm|UF\\JCjP^P<`と疑似素数配列を`XOR`すればフラグが抽出できる。
