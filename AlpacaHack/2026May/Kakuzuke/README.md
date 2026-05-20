# Kakuzuke

## / Overview

`express.urlencoded({ extended: false })`の仕様を使ったディレクトリトラバーサル

## / Writeup

`index.js`をみるとレスポンスのパスの指定を文字列の結合で行っていることが分かります。

```js
res.type("html").sendFile(path.join(import.meta.dirname, `choices/${choice}`));
```

この`choice`はPOSTリクエストで`application/x-www-form-urlencoded`形式で送ることができます。

しかしこの`choice`には`choice.length <= 5`という制約があります。つまり`choice`が文字列だと、どう頑張っても`/flag.txt`を指定できません。


### express.urlencodedの仕様

文字列以外で送りつける方法を探していると、`express.urlencoded({ extended: false })`は**文字列**と**配列**をパースするという情報を見つけました。[[1]](https://stackoverflow.com/questions/23259168/what-are-express-json-and-express-urlencoded)

配列を使えるなら`choice.length`は文字の長さではなく、配列の要素数として扱われそうです。さらに調査を進めると、パースには`querystring`ライブラリを使っており[[2]](https://stackoverflow.com/questions/56751378/could-you-please-the-optionextended-false-used-in-express-urlencoded)、ソースコードを見ると次のように配列が作られることが分かりました。

```js
if (!hasOwnProperty(obj, k)) {
    obj[k] = v;
} else if (Array.isArray(obj[k])) {
    obj[k].push(v);
} else {
    obj[k] = [obj[k], v];
}
```

つまりは同じキーが繰り返されて初めて配列になります。`choice=x&choice=y`を送れば`{ choice: ['x', 'y'] }`とパースされます。

これで文字数制限はクリアしましたが、もう一つ問題があります。それが`` `choices/${choice}` ``による配列の解釈です。先程の`choice`は展開されて

```
choice/x,y
```

として文字列化されます。そのためx,yどちらに`../../flag.txt`を入れてもカンマが邪魔してパスが通りません。

僕が最初に試したのは`%00`による強制解釈終了ですが、これは最近では徹底的に対策されているようです。

最終的には降参してGeminiに聞いたところ、カンマをディレクトリとして扱うのが正解のようでした。つまり`choice=&choice=/../../../flag.txt`をペイロードとすれば次のようにパースされます。

```
choices/,/../../../flag.txt
```

ディレクトリの存在検証は行っていないのでこれで`flag.txt`に到達します。