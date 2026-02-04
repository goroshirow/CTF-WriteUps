# git gc

## / Overview

`git reset --hard HEAD~1`で消されたファイルを見る。

## / Writeup

`git reset ctf`で調べると、たくさん記事が出てくるのでそのうちの一つを真似すると解けます。

> SECCON Beginners CTF 2021 解けなかった問題を勉強した記録2
> 
> https://qiita.com/housu_jp/items/494bdf4b92a5f2e55ced#misc-01-git-leak

まずはcommit履歴を見ます。

```bash
$ git reflog
c0bf20c (HEAD -> main) HEAD@{0}: reset: moving to HEAD~1
75a6ad9 HEAD@{1}: commit: add flag
c0bf20c (HEAD -> main) HEAD@{2}: commit (initial): initial commit
```

２つ目が怪しいのでコミットハッシュを指定して中身を確認する。

```bash
$ git cat-file -p 75a6ad9
tree 1b44243c75077537d74f00aacbc930f2c7283b93
parent c0bf20c191a250522fc742093ff920243346f578
author AlpacaHack <alpacahack@alpacahack.internal> 1767977104 +0900
committer AlpacaHack <alpacahack@alpacahack.internal> 1767977104 +0900

add flag


$ git cat-file -p 1b44243c75077537d74f00aacbc930f2c7283b93
100644 blob 4c820f244ddd11f3286edfb63ac9d1537a3f2cb3    flag.txt


$ git cat-file -p 4c820f244ddd11f3286edfb63ac9d1537a3f2cb3
Alpaca{*** REDACTED ***}
```