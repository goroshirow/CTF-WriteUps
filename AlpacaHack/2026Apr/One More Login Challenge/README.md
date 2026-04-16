# One More Login Challenge

## / Overview

MongoDB/NoSQLインジェクション

## / Writeup

MongoDBで実装されたログインフォームから正規のパスワードを使わずにログインすることが目的です．

ログインフォームで入力されたデータは`application/x-www-form-urlencoded`として`username=hoge&password=hoge`という形式でポストされます．これを次の関数で処理します．

```js
const user = await client.db("db").collection("users").findOne({
    username,
    password,
});
```

実装を詳しく見ると`application/json`のポストが許可されていることが分かります．わざわざ許可しているということはこれを使って解くのでしょう．

実はMongoDBでは文字列のクエリだけではなく`JSONオブジェクト`を使ったクエリが可能です．どういうことかと言うと，例えば`名前`と`年齢`を管理しているデータベースがあったとしましょう．この時，**20歳以下のユーザー**を探したい時，次のように書くことができます．

```js
db.users.find({ age: { $lt: 20 } })
```

他にもいろいろな条件でデータを取得することができるので，参考にした以下の記事を見てみてください．

> 【MongoDB】基本的なクエリの書き方
>
> https://qiita.com/ktdatascience/items/92a91e6a9e5860f8404d

今回はこの仕様を利用してログインしましょう．今パスワードが分からないので`$ne`（等しくない）を代わりに使います．具体的には以下のJSONをサーバーに送信します．この時JSONとして認識させるために`Content-Type: application/x-www-form-urlencoded`から`Content-Type: application/json`に変更することを忘れないでください．

```sh
# 実際に使う場合は1行にしてください
$ curl -X POST http://34.170.146.252:19790/ 
    -H 'Content-Type: application/json' 
    -d '{"username":"admin","password":{"$ne":""}}'
```

パスワードは当然空白ではないので，フラグが表示されます．

ヒント3にもある通りこの様な攻撃は`NoSQLインジェクション`と呼ばれています．MongoDBだけではなく様々なデータベースに対して攻撃手法があるので同じ様な問題に出会ったら復習しようと思います．

> NoSQLインジェクション対策｜MongoDB、​Redis等の​脆弱性と​防御策
>
> https://guardian.jpn.com/security/web-api/sql-injection/column/nosql-injection-defense/