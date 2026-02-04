# Cha-ll-enge

## 概要

中間言語LLVM-IRからフラグの判定条件を解析する．

## 解法

ファイル内の`@__isoc99_scanf`というワードで検索すると，`LLVM-IR`というアセンブリと高級言語の中間表現であることが分かった．拡張子は`.ll`である．

当然読めないので，コンパイルして実行ファイルにしたい．サイトを参考に一度，アセンブリ言語に変換する．

```bash
> llc ./cha.ll

llc: error: llc: ./cha.ll:20:29: error: use of undefined value '@__isoc99_scanf'
  %10 = call i32 (i8*, ...) @__isoc99_scanf(i8* noundef getelementptr inbounds ([3 x i8], [3 x i8]* @.str.1, i64 0, i64 0), i8* noundef %9)
```

エラーが出たので色々調べると以下のサイトが見つかった．

> [Cool compiler using ANTLR and LLVM
](https://www.google.com/url?sa=t&source=web&rct=j&opi=89978449&url=https://scholars.csus.edu/esploro/fulltext/graduate/Cool-compiler-using-ANTLR-and-LLVM/99257831148901671%3FrepId%3D12232541680001671%26mId%3D13237611750001671%26institution%3D01CALS_USL&ved=2ahUKEwic6JyG996RAxU2dvUHHXW_PVc4ChAWegQIIRAB&usg=AOvVaw0TZIKquPBeRywpRmnEHt4i)

資料で紹介されているLLVM-IRと同じ様に，定義文を追加するとうまくいくかもしれない．具体的には次の宣言である．

```
declare i32 @__isoc99_scanf(i8*, ...)
declare i32 @printf(i8*, ...)
declare i32 @puts()
declare i64 @strlen()
```

これでもう一度コンパイルしてみる．

```bash
> llc ./cha.ll

llc: error: llc: ./cha.ll:73:29: error: use of undefined metadata '!6'
  br label %15, !llvm.loop !6
```

`!6`というラベルがない，というエラーであるが一度コードを見直してみると全ての関数ラベルの横に`; preds = %38, %14`みたいなのが書いてある．

これは，他のどの関数から遷移しているかを表していそうだが，エラーが出た命令が含まれている関数からは`15`にしか遷移しなさそうだ．

削除しても影響がないものとして，もう一度コンパイルするとアセンブリファイル`cha.s`が生成された．

次にこのアセンブリファイルを実行ファイルに変換する．
```bash
> gcc ./cha.s

/usr/bin/ld: /tmp/cc4gEDlc.o: relocation R_X86_64_32 against `.rodata' can not be used when making a PIE object; recompile with -fPIE
/usr/bin/ld: failed to set dynamic section sizes: bad value
collect2: error: ld returned 1 exit status
```

このエラーは次のサイトを参考に`-no-pie`を追加して解消した．

> [SML#をUbuntu 16.10で動かす](https://keens.github.io/blog/2016/11/30/sml_woubuntu_16_10deugokasu/)

生成された実行ファイルをghidraで逆コンパイルしてc言語として読むと`&DAT_00402010`と入力を4byteずつXORして`&[DAT_00402010 + 8]`と一致するのかを判定しているようだ．

```c
undefined4 main(void)

{
  size_t sVar1;
  int local_13c;
  ulong local_138;
  char local_128 [80];
  uint local_d8 [52];
  
  memcpy(local_d8,&DAT_00402010,200);
  printf("Input FLAG : ");
  __isoc99_scanf(&DAT_004020e6,local_128);
  sVar1 = strlen(local_128);
  if (sVar1 == 0x31) {
    local_13c = 0;
    for (local_138 = 0; local_138 < 0x31; local_138 = local_138 + 1) {
      if (((int)local_128[local_138] ^ local_d8[local_138]) == local_d8[local_138 + 1]) {
        local_13c = local_13c + 1;
      }
    }
    if (local_13c == 0x31) {
      printf("Correct! FLAG is %s.\n",local_128);
      return 0;
    }
  }
  puts("Incorrect FLAG.");
  return 1;
}

```

`&[DAT_00402010 + 4i] ^ input[i] = &[DAT_00402010 + 4(i+1)]`から
`input[i] = &[DAT_00402010 + 4i] ^  &[DAT_00402010 + 4(i+1)]`としてフラグを再現できる．