# flag obfuscation

## / Overview

IPv6による難読化

## / Writeup

このチャレンジでは、あるEXEファイル（おそらくフラグに関係するファイル）が`obfuscaton.c`のプログラムによって難読化され、その結果が`data.h`に記録されています。

ではどの様に難読化されているかと言うと、核となるのは次の関数です。

```c
inet_ntop(AF_INET6, chunk, ipv6, sizeof(ipv6));
```

これがどのようなものか調べると**バイナリデータをIPアドレスに変換する**関数であることが分かります。更に`AF_INET6`はIPv6を指定しています。

> inet_ntop - IPv4/IPv6 アドレスをバイナリ形式からテキスト ...
> 
> https://manpages.ubuntu.com/manpages/trusty/ja/man3/inet_ntop.3.html

`data.h`を見ると、IPv6に変換されたデータが配列形式で保存されています。

ということでIPv6をバイナリデータに戻してEXEファイルを作りましょう。`inet_pton`関数で実現できます。

```c
#include <stdio.h>
#include <stdlib.h>
#include <winsock2.h>
#include <ws2tcpip.h>

#include "data.h"

int main(){

    FILE *f = fopen("output.exe", "wb");

    unsigned char chunk[16];

    for (int i = 0; i < ipv6_count; i++)
    {
        inet_pton(AF_INET6, ipv6_data[i], chunk);
        fwrite(chunk, 1, 16, f);
    }

    fclose(f);
    return 0;
}
```

これを`data.h`と同じディレクトリでコンパイル実行すると`output.exe`が生成されます。更にこのEXEを実行すると

```
Input flag: 
```

と表示されます。なので`Ghidra`で逆コンパイルしてフラグ判定ロジックを解読します。例えば`Input flag: `という文字列が使われている場所を調べると、次の関数がヒットします。

```c
undefined8
FUN_1400079e0(undefined8 param_1,undefined8 param_2,undefined8 param_3,undefined8 param_4)

{
  byte bVar1;
  FILE *_File;
  longlong lVar2;
  longlong lVar3;
  byte local_78 [48];
  byte local_48 [64];
  
  FUN_140001650();
  local_78[0x2c] = 0;
  local_78[0] = 0x41;
  local_78[1] = 0x6c;
  local_78[2] = 0x70;
  local_78[3] = 0x61;
  local_78[4] = 99;
  local_78[5] = 0x61;
  local_78[6] = 0x7b;
  local_78[7] = 0x69;
  local_78[8] = 0x70;
  local_78[9] = 0x76;
  local_78[10] = 0x36;
  local_78[0xb] = 0x5f;
  local_78[0xc] = 0x6f;
  local_78[0xd] = 0x62;
  local_78[0xe] = 0x66;
  local_78[0xf] = 0x75;
  local_78[0x10] = 0x73;
  local_78[0x11] = 99;
  local_78[0x12] = 0x61;
  local_78[0x13] = 0x74;
  local_78[0x14] = 0x69;
  local_78[0x15] = 0x6f;
  local_78[0x16] = 0x6e;
  local_78[0x17] = 0x5f;
  local_78[0x18] = 99;
  local_78[0x19] = 0x61;
  local_78[0x1a] = 0x6e;
  local_78[0x1b] = 0x5f;
  local_78[0x1c] = 0x65;
  local_78[0x1d] = 0x76;
  local_78[0x1e] = 0x61;
  local_78[0x1f] = 100;
  local_78[0x20] = 0x65;
  local_78[0x21] = 0x5f;
  local_78[0x22] = 0x73;
  local_78[0x23] = 0x69;
  local_78[0x24] = 0x67;
  local_78[0x25] = 0x6e;
  local_78[0x26] = 0x61;
  local_78[0x27] = 0x74;
  local_78[0x28] = 0x75;
  local_78[0x29] = 0x72;
  local_78[0x2a] = 0x65;
  local_78[0x2b] = 0x7d;
  FUN_140001550("Input flag: ",0x646176655f6e6163,param_3,param_4);
  _File = (FILE *)(*(code *)PTR_FUN_140008090)(0);
  fgets((char *)local_48,0x40,_File);
  lVar2 = 0;
  do {
    bVar1 = local_48[lVar2];
    lVar3 = lVar2 + 1;
    if (bVar1 != local_78[lVar2]) {
      FUN_140001550("Wrong\n",(ulonglong)bVar1,_File,param_4);
      return 0;
    }
    lVar2 = lVar3;
  } while (lVar3 != 0x2c);
  FUN_140001550("Correct!\n",(ulonglong)bVar1,_File,param_4);
  return 0;
}
```

local_78の最初の2文字が`0x41->A`, `0x6c->l`なので、おそらくフラグでしょう。これをASCII変換することでフラグが得られました。