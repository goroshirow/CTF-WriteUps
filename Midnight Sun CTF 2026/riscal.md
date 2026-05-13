# riscal

## / Overview

Ghidra逆コンパイル

## / Writeup

配布されたファイルが何なのか`file`コマンドで調べます。

```sh
$ file riscal-0f56f1aacbef526420953111a1d07d10
riscal-0f56f1aacbef526420953111a1d07d10: ELF 64-bit LSB pie executable, UCB RISC-V, RVC, double-float ABI, version 1 (SYSV), dynamically linked, interpreter /lib/ld-linux-riscv64-lp64d.so.1, BuildID[sha1]=20dcdb0413bbc616a8579b26627b51b89bd2008e, for GNU/Linux 4.15.0, stripped
```

64bitリトルエンディアンELFファイルですが、`RISC-V`という命令セットで作られています。これをGhidraで指定して逆コンパイルするとフラグがハードコードされていました。

```
FUN_ram_00100870("midnight{RISCV_1S_4_34zy_1S4_70_unDeRst4Nd!!}");
```