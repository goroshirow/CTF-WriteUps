# C++ flag checker

## / Overview

**C++プログラムの逆コンパイル**

配布された実行ファイル`cpp-flag-checker`にstringsコマンドを実行すると

- Input:
- Correct! The flag is
- Incorrect...

という文字列が見えます。よってこのチャレンジはリバースエンジニアリングによるフラグ判定ロジックを解読することが目的だと推測されます。

そこでGhidraを用いて逆コンパイルすると、C++で書かれたソースコードが見れます。

```cpp

undefined8 main(void)

{
  bool bVar1;
  long lVar2;
  ostream *poVar3;
  long in_FS_OFFSET;
  undefined1 auVar4 [16];
  string local_88 [32];
  array local_68 [72];
  long local_20;
  
  local_20 = *(long *)(in_FS_OFFSET + 0x28);
  std::__cxx11::string::string(local_88);
                    /* try { // try from 00102285 to 00102379 has its CatchHandler @ 0010239c */
  std::operator<<((ostream *)std::cout,"Input: ");
  std::getline<>((istream *)std::cin,local_88);
  lVar2 = std::__cxx11::string::size(local_88);
  if (lVar2 == 0x3e) {
    auVar4 = std::__cxx11::string::operator.cast.to.basic_string_view(local_88);
    encode(local_68,auVar4._0_8_,auVar4._8_8_,local_68,auVar4._0_8_,auVar4._8_8_);
    bVar1 = std::operator==(local_68,(array *)encoded);
    if (bVar1) {
      bVar1 = true;
      goto LAB_0010230c;
    }
  }
  bVar1 = false;
LAB_0010230c:
  if (bVar1) {
    poVar3 = std::operator<<((ostream *)std::cout,"Correct! The flag is ");
    poVar3 = std::operator<<(poVar3,local_88);
    std::ostream::operator<<(poVar3,std::endl<>);
  }
  else {
    poVar3 = std::operator<<((ostream *)std::cout,"Incorrect...");
    std::ostream::operator<<(poVar3,std::endl<>);
  }
  std::__cxx11::string::~string(local_88);
  if (local_20 != *(long *)(in_FS_OFFSET + 0x28)) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return 0;
}
```

このコードからフラグの判定条件を紐解いていきましょう。

## / Writeup

`Correct! The flag is `や`Incorrect...`をラップしている条件分岐から`bVar1`がTrueになった時、フラグと一致していたと言えそうです。

この変数の元を辿ると

```cpp
bVar1 = std::operator==(local_68,(array *)encoded);
```

というコードにあたります。`local_68`は変数で、`encoded`は配列のようです。配列の中身を右クリックメニューの「Copy Special...」>「Python List」からコピーすると以下の配列が得られます。

```py
[ 0xfc, 0x6c, 0xe5, 0xc9, 0xee, 0x63, 0x2e, 0x49, 0xfc, 0x06, 0x72, 0x66, 0xc8, 0xb8, 0x0a, 0x44, 0xdc, 0x1b, 0xf0, 0x6b, 0x82, 0x93, 0x27, 0x91, 0x92, 0x9c, 0x7a, 0x17, 0x62, 0xf0, 0x3a, 0x74, 0x9a, 0x9d, 0xf7, 0x15, 0x59, 0x99, 0x3d, 0xc5, 0x6b, 0x5b, 0x4a, 0xad, 0x3e, 0x17, 0x33, 0x89, 0x61, 0x4d, 0xfc, 0xe0, 0x2b, 0xf9, 0x27, 0xf9, 0x3c, 0xfc, 0x7c, 0x77, 0x13, 0x3f ]
```

`local_68`は1行前の`encode()`で処理された後に、この配列と一致します。

では次に`encode()`の中の処理を見ます。この時`local_68`を含め6つの変数が見受けられますが、実際に関数に飛ぶと、3つの変数しか取らないみたいです。このような出来事は時折発生しますが、main側の前半の3つが大体正しい入力です。実際、後半の3つは繰り返しになっているだけなので無視して進めます。

`encode()`の他2つの変数を見ると`auVar4._0_8_`と`auVar4._8_8_`となっています。`auVar4`は`local_88`を`basic_string_view`化したものであり、公式ドキュメントより「文字列へのポインタ」と「文字列のサイズ」を持つ変数であることが分かります[[1]](https://cpprefjp.github.io/reference/string_view/basic_string_view.html)。

また`_0_8_`と`_8_8_`はそれぞれ**0から8バイト**と**8から8バイト**を表していることと、ポインタが8バイトであることを踏まえると、前者が「文字列へのポインタ」で後者が「文字列のサイズ」であると考えられます。

さらに前を見ると`local_88`は入力値であることが分かるので`encode()`では入力値を使った`local_68`の加工が行われていると推測できます。

では`encode()`の実装を見ましょう。

```cpp

/* encode(std::basic_string_view<char, std::char_traits<char> >) */

array<> * encode(array<> *param_1,undefined8 param_2,undefined8 param_3)

{
  uchar *puVar1;
  uchar *puVar2;
  undefined8 uVar3;
  undefined8 uVar4;
  undefined8 uVar5;
  undefined8 uVar6;
  undefined8 local_48;
  undefined8 local_40;
  array<> *local_30;
  
  local_48 = param_2;
  local_40 = param_3;
  local_30 = param_1;
  puVar1 = (uchar *)std::array<>::end(param_1);
  puVar2 = (uchar *)std::array<>::begin(local_30);
  std::iota<>(puVar2,puVar1,10);
  uVar3 = std::array<>::begin(local_30);
  uVar4 = std::array<>::begin(local_30);
  uVar5 = std::basic_string_view<>::end((basic_string_view<> *)&local_48);
  uVar6 = std::basic_string_view<>::begin((basic_string_view<> *)&local_48);
  std::transform<>(uVar6,uVar5,uVar4,uVar3);
  return local_30;
}
```

まず注目したいのは

```cpp
std::iota<>(puVar2,puVar1,10);
```

で、この関数は`puVar2`から`puVar1`まで10からインクリメントした値が代入されます。つまり`param1`として渡されている配列`local_68`の先頭から順番に10, 11, ...が代入されます。

次に

```cpp
std::transform<>(uVar6,uVar5,uVar4,uVar3);
```

では`transeform`を適用しており、引数として「`local_48`の先頭」「`local_48`の末尾」「`local_30`の先頭」「`local_30`の先頭」を受け取っています。

`local_30`はmain側の`local_68`であり、`local_48`は入力文字列へのポインタであることに注意して、さらに`transform`の中身を見ます。

```cpp

uchar * std::transform<>(char *param_1,char *param_2,uchar *param_3,uchar *param_4)

{
  uchar uVar1;
  {lambda(char,unsigned_char)#1} local_29;
  uchar *local_28;
  uchar *local_20;
  char *local_18;
  char *local_10;
  
  local_28 = param_4;
  local_20 = param_3;
  local_18 = param_2;
  for (local_10 = param_1; local_10 != local_18; local_10 = local_10 + 1) {
    uVar1 = encode(std::basic_string_view<>)::{lambda(char,unsigned_char)#1}::operator()
                      (&local_29,*local_10,*local_20);
    *local_28 = uVar1;
    local_20 = local_20 + 1;
    local_28 = local_28 + 1;
  }
  return local_28;
}
```

`local_10`という変数が`encode()`側の`local_48`の先頭から末尾までをforループで取得し、入力値の同じインデックスのポインタとともに`encode(std::basic_string_view<>)::{lambda(char,unsigned_char)#1}::operator()`に入力されています。なのでさらにこの関数の中身を見ます。

```cpp

int __thiscall
encode(std::basic_string_view<>)::{lambda(char,unsigned_char)#1}::operator()
          ({lambda(char,unsigned_char)#1} *this,char param_1,uchar param_2)

{
  return (uint)param_2 * (uint)param_2 * (uint)param_2 + (uint)(byte)(param_1 ^ 0x55);
}
```

やっと最深部にたどり着きました。ここまでの変数の流れを整理すると、`param_1`は入力文字のn番目の要素であり、`param_2`はn+10であることが分かります。returnされた値はもう一度mainの配列`local_68`に格納されるため、この関数の逆変換を実装し、`encoded`を入力とすればフラグが求まるはずです。

引き算の結果が負にならないように`mod 256`を取りつつ、一文字ずつ解読するソルバを作ればフラグを獲得できます。

## / Solver

```py
encoded = [ 0xfc, 0x6c, 0xe5, 0xc9, 0xee, 0x63, 0x2e, 0x49, 0xfc, 0x06, 0x72, 0x66, 0xc8, 0xb8, 0x0a, 0x44, 0xdc, 0x1b, 0xf0, 0x6b, 0x82, 0x93, 0x27, 0x91, 0x92, 0x9c, 0x7a, 0x17, 0x62, 0xf0, 0x3a, 0x74, 0x9a, 0x9d, 0xf7, 0x15, 0x59, 0x99, 0x3d, 0xc5, 0x6b, 0x5b, 0x4a, 0xad, 0x3e, 0x17, 0x33, 0x89, 0x61, 0x4d, 0xfc, 0xe0, 0x2b, 0xf9, 0x27, 0xf9, 0x3c, 0xfc, 0x7c, 0x77, 0x13, 0x3f ]


def dec(encoded):
    flag = ""
    for i in range(len(encoded)):
        flag += chr(((encoded[i] - (i+10)**3)%0x100)^0x55)
    return flag

if __name__ == "__main__":
    print(dec(encoded))
```