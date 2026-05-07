# permission denied 3

## / Overview

`rm`したファイルの復元

## / Writeup

今回のチャレンジではサーバに接続した瞬間`rm *`によって`flag.txt`を含む，カレントディレクトリのファイル全てが削除されます．この状況でフラグを復元したいので，`rm`したファイルを復元する方法について調べます．

> rmで削除したファイルを復元できる lsof
> 
> https://qiita.com/marukome/items/50f90f9a6f5078276e4d

この記事によると，削除されたファイルはファイルディスクリプタに紐づいていて，それをコピーしてくれば復元できると言っています．

今回の環境では`lsof`が使えないのですが，ファイルディスクリプタを探すだけなら`/proc`を直接探すだけでいいので，次のコマンドを実行します．

```sh
# ls -la /proc/*/fd/*
ls: cannot access '/proc/11/fd/3': No such file or directory
ls: cannot access '/proc/11/fd/4': No such file or directory
ls: cannot access '/proc/self/fd/10': No such file or directory
ls: cannot access '/proc/self/fd/3': No such file or directory
ls: cannot access '/proc/self/fd/4': No such file or directory
ls: cannot access '/proc/thread-self/fd/10': No such file or directory
ls: cannot access '/proc/thread-self/fd/3': No such file or directory
ls: cannot access '/proc/thread-self/fd/4': No such file or directory
lrwx------ 1 root root 64 May  6 15:54 /proc/1/fd/0 -> /dev/null
l-wx------ 1 root root 64 May  6 15:54 /proc/1/fd/1 -> 'pipe:[5454981]'
l-wx------ 1 root root 64 May  6 15:54 /proc/1/fd/2 -> 'pipe:[5454982]'
lrwx------ 1 root root 64 May  6 15:54 /proc/1/fd/3 -> 'socket:[5456399]'
lrwx------ 1 root root 64 May  6 15:54 /proc/1/fd/4 -> 'socket:[5456400]'
lrwx------ 1 root root 64 May  6 15:54 /proc/1/fd/5 -> 'socket:[5456401]'
lrwx------ 1 root root 64 May  6 15:54 /proc/11/fd/0 -> /dev/pts/0
lrwx------ 1 root root 64 May  6 15:54 /proc/11/fd/1 -> /dev/pts/0
lrwx------ 1 root root 64 May  6 15:54 /proc/11/fd/10 -> /dev/tty
lrwx------ 1 root root 64 May  6 15:54 /proc/11/fd/2 -> /dev/pts/0
lrwx------ 1 root root 64 May  6 15:54 /proc/6/fd/0 -> /dev/null
l-wx------ 1 root root 64 May  6 15:54 /proc/6/fd/1 -> 'pipe:[5454981]'
l-wx------ 1 root root 64 May  6 15:54 /proc/6/fd/2 -> 'pipe:[5454982]'
lrwx------ 1 root root 64 May  6 15:54 /proc/6/fd/3 -> 'socket:[5449433]'
lrwx------ 1 root root 64 May  6 15:54 /proc/6/fd/4 -> 'socket:[5449434]'
lrwx------ 1 root root 64 May  6 15:54 /proc/6/fd/5 -> /dev/pts/ptmx
lrwx------ 1 root root 64 May  6 15:54 /proc/6/fd/6 -> 'socket:[5456417]'
lrwx------ 1 root root 64 May  6 15:54 /proc/6/fd/7 -> 'socket:[5449435]'
lrwx------ 1 root root 64 May  6 15:54 /proc/7/fd/0 -> /dev/pts/0
lrwx------ 1 root root 64 May  6 15:54 /proc/7/fd/1 -> /dev/pts/0
lrwx------ 1 root root 64 May  6 15:54 /proc/7/fd/2 -> /dev/pts/0
lr-x------ 1 root root 64 May  6 15:54 /proc/7/fd/255 -> '/app/chal.sh (deleted)'
lrwx------ 1 root root 64 May  6 15:54 /proc/self/fd/0 -> /dev/pts/0
lrwx------ 1 root root 64 May  6 15:54 /proc/self/fd/1 -> /dev/pts/0
lrwx------ 1 root root 64 May  6 15:54 /proc/self/fd/2 -> /dev/pts/0
lrwx------ 1 root root 64 May  6 15:54 /proc/thread-self/fd/0 -> /dev/pts/0
lrwx------ 1 root root 64 May  6 15:54 /proc/thread-self/fd/1 -> /dev/pts/0
lrwx------ 1 root root 64 May  6 15:54 /proc/thread-self/fd/2 -> /dev/pts/0
```

`/proc/7/fd/255` に削除されたはずの`/app/chal.sh`が紐づいています．これをコピーして中身を見るとフラグが取れます．

```sh
# cp /proc/8/fd/255 ./
# ls
255
# cat 255
echo Alpaca{...} |
install -m 400 /dev/stdin flag.txt
rm *
sh
```