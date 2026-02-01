# operand

## / Overview

デコンパイル結果から判定ロジックの逆算

## / Writeup

ghidra でデコンパイルした結果のmain関数は次の通りです。
```c
undefined8 main(void)

{
  size_t flag_len;
  long in_FS_OFFSET;
  int count;
  char flag [48];
  char input [56];
  long local_20;
  
  local_20 = *(long *)(in_FS_OFFSET + 0x28);
  flag[0] = -0x3f;
  flag[1] = -0x35;
  flag[2] = -0x22;
  flag[3] = -0x35;
  flag[4] = -0x33;
  flag[5] = -0x35;
  flag[6] = -0x3d;
  flag[7] = -0x22;
  flag[8] = -0x35;
  flag[9] = -0x3d;
  flag[10] = -0x79;
  flag[0xb] = -0x17;
  flag[0xc] = -2;
  flag[0xd] = -0x14;
  flag[0xe] = -0x2f;
  flag[0xf] = -0x66;
  flag[0x10] = -0x26;
  flag[0x11] = -0x67;
  flag[0x12] = -0x28;
  flag[0x13] = -0x35;
  flag[0x14] = -0x3c;
  flag[0x15] = -0x32;
  flag[0x16] = -0xb;
  flag[0x17] = -0x65;
  flag[0x18] = -0x61;
  flag[0x19] = -0xb;
  flag[0x1a] = -0x2e;
  flag[0x1b] = -0x39;
  flag[0x1c] = -0x39;
  flag[0x1d] = -0x67;
  flag[0x1e] = -0xb;
  flag[0x1f] = -5;
  flag[0x20] = -0x35;
  flag[0x21] = -0x29;
  flag[0x22] = 0;
  write(1,"flag> ",7);
  read(0,input,0x32);
  xor("00000000000000000000000000000");
  count = 0;
  while( true ) {
    flag_len = strlen(flag);
    if (flag_len <= (ulong)(long)count) break;
    if (input[count] != flag[count]) {
      write(1,"You have wrong flag..\n",0x17);
                    /* WARNING: Subroutine does not return */
      exit(0);
    }
    count = count + 1;
  }
  write(1,"Congratulations!!\n",0x13);
  if (local_20 != *(long *)(in_FS_OFFSET + 0x28)) {
                    /* WARNING: Subroutine does not return */
    __stack_chk_fail();
  }
  return 0;
}
```

大まかな処理としては入力`input`と`flag`が一致しているかを調べているというところでしょう。

`xor("00000000000000000000000000000");`という気になる処理はありますが一旦気にせず `flag` をそのままasciiで復号してみます。ここで気をつけるのが符号の扱いです。 `flag` の各要素はint型で扱われているため`2の歩数表現`で解釈されていますが、実際はchar型なのでpythonで復号する場合は**すべての要素をビット反転して1足す**必要があります。復号結果はこちらです。

```
ÁËÞËÍËÃÞËÃéþìÑÚØËÄÎõõÒÇÇõûË×Ā
```

明らかに失敗しているので先程無視した`xor`の処理を見ます。

```c
void xor(void)

{
  size_t sVar1;
  char *in_XMM3_Qa;
  int local_1c;
  
  local_1c = 0;
  while( true ) {
    sVar1 = strlen(in_XMM3_Qa);
    if (sVar1 <= (ulong)(long)local_1c) break;
    in_XMM3_Qa[local_1c] = in_XMM3_Qa[local_1c] ^ 0xaa;
    local_1c = local_1c + 1;
  }
  return;
}
```

後から分かったのですが`XMM3 Qa`というのはレジスタの値のようです。`input`の値がここに入って、それぞれの文字が`0xaa`とXORされる処理です。

本番では、なんとなく「XORしてるなー」とわかると思うので、これを復号の処理に加えると、無事にフラグがゲットできます。
