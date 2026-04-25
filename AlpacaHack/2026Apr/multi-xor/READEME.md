# multi-xor

## / Overview

直積写像の単射性を用いた総当り解読

## / Writeup

フラグは鍵$`k_i`$と関数$`f, g`$を用いて次のように暗号化されます．


$$x_0 = FLAG, x_{i+1} = f(x_i) \oplus k_i$$
$$y_0 = FLAG, y_{i+1} = g(y_i) \oplus k_i$$

`output.txt`には$`x_{40}, y_{40}, k_i(0\le i \le 39)`$が出力されています．

### 関数f, gの特徴

実は解法にあまり関係しないのですが関数$`f, g`$の中身を見ましょう．$`f`$は$`x`$をバイト単位に分割した後，それぞれに対して以下のような$'f_{byte}'$を施します．ここで$`x`$のある1バイトをインデックスを用いて$`x_{byte} = x_F x_E x_D x_C x_B x_A x_9 x_8 x_7 x_6 x_5 x_4 x_3 x_2 x_1 x_0`$と表します．

$$f_{byte}(x_{byte})=\\
x_F x_E x_D x_C x_B x_A x_9 x_8 x_7 x_6 x_5 x_4 x_3 x_2 x_1 x_0 \oplus\\
 x_E x_D x_C x_B x_A x_9 x_8 x_7 x_6 x_5 x_4 x_3 x_2 x_1 x_0 ~0 \oplus\\
  0 ~x_F x_E x_D x_C x_B x_A x_9 x_8 x_7 x_6 x_5 x_4 x_3 x_2 x_1$$

元のバイトを左と右に1つずつずらしてXORした形です．これは1バイトの話なので実際の$`f`$は$`x`$の各バイトに対して独立した$`f_{byte}`$を適用することに注意してください．

関数$`g_{byte}`$は3バイトずつずらします．

$$g_{byte}(y_{byte})=\\
y_F y_E y_D y_C y_B y_A y_9 y_8 y_7 y_6 y_5 y_4 y_3 y_2 y_1 y_0 \oplus\\
y_C y_B y_A y_9 y_8 y_7 y_6 y_5 y_4 y_3 y_2 y_1 y_0 ~0 ~0 ~0 \oplus\\
0 ~0 ~0 ~y_F y_E y_D y_C y_B y_A y_9 y_8 y_7 y_6 y_5 y_4 y_3$$

### 解法

たくさんある関数の中に`combined_is_unique()`というものがあります．チャレンジに関係のない関数は入れないだろうというメタ解釈のもと，なぜこの様な関数があるのかを考えます．

`combined_is_unique()`の主張は次のとおりです．

$$ \forall u,v \in \{ 0, 1, ... , 255\}, u \ne v \Rightarrow (f_{byte}^{40}(u), g_{byte}^{40}(u)) \ne (f_{byte}^{40}(v), g_{byte}^{40}(v))$$

つまり異なるバイトに対して$`f_{byte}, g_{byte}`$をそれぞれ40回適用した結果のタプルは常に異なるということです．これにより$`(f_{byte}^{40}(u), g_{byte}^{40}(u))`$の結果から$`u`$の値が一意に定まります．

しかし，今回の暗号化プロセスでは$`k_i`$とのXORも同時に行われるため，一見役に立たないように思えます．

実は$`f(x \oplus y) = f(x) \oplus f(y)`$という関係を用いることで暗号化プロセスの40回の更新は次のように書き換えることが出来ます．

$$x_{40} = f(...f(f(x_0) \oplus k_0) \oplus k_1) \oplus ... )\oplus k_{39} \\ = f^{40}(x_0) \oplus f^{39}(k_0) \oplus f^{38}(k_1) \oplus ... \oplus f^0(k_{39})$$

今，$`k_0`$から$`k_{39}`$までは与えられているので

$$f^{40}(x_0) = x_{40} \oplus f^{39}(k_0) \oplus f^{38}(k_1) \oplus ... \oplus f^0(k_{39})$$

で左辺が求められます．同様にして

$$g^{40}(y_0) = y_{40} \oplus g^{39}(k_0) \oplus g^{38}(k_1) \oplus ... \oplus g^0(k_{39})$$

で左辺が求められます．これら2つの各バイトについては先程の`combined_is_unique()`の主張がそのまま適用可能です．したがって，0から255までのバイトに対して$`f_{byte}, g_{byte}`$をそれぞれ40回適用した結果を辞書形式で保存しておけば，FLAGの各バイトはもともと何であったかが$`(f^{40}(x_0), g^{40}(y_0))`$から逆引き出来ます．これで復号完了です．

## / Solver

```py
def f_byte(x: int) -> int:
    x &= 0xFF
    return (x ^ ((x << 1) & 0xFE) ^ ((x >> 1) & 0x7F)) & 0xFF

def g_byte(x: int) -> int:
    x &= 0xFF
    return (x ^ ((x << 3) & 0xF8) ^ ((x >> 3) & 0x1F)) & 0xFF

def iter_f_byte(x: int, rounds: int) -> int:
    for _ in range(rounds):
        x = f_byte(x)
    return x

def iter_g_byte(x: int, rounds: int) -> int:
    for _ in range(rounds):
        x = g_byte(x)
    return x

if __name__ == "__main__":
    cipher_f = None
    cipher_g = None
    f_keys = []
    g_keys = []
    
    with open("output.txt", "r") as f:
        for i, line in enumerate(f):
            val = line.split()[2]
            val = bytes.fromhex(val)

            if i == 0:
                cipher_f = val
            elif i == 1:
                cipher_g = val
            elif 2 <= i <= 41:
                f_keys.append(val)
            elif 42 <= i <= 81:
                g_keys.append(val)
                
    n = len(cipher_f)
    f_key_cipher = [0] * n
    g_key_cipher = [0] * n
    
    for i, key in enumerate(f_keys):
        for byte_idx in range(n):
            f_key_cipher[byte_idx] ^= iter_f_byte(key[byte_idx], 39-i)
            
    for i, key in enumerate(g_keys):
        for byte_idx in range(n):
            g_key_cipher[byte_idx] ^= iter_g_byte(key[byte_idx], 39-i)

    f_byte_cipher_list = []
    g_byte_cipher_list = []
    
    for i in range(256):
        f_byte_cipher_list.append(iter_f_byte(i, 40))
        g_byte_cipher_list.append(iter_g_byte(i, 40))
        
    flag = bytearray(n)  
    for i in range(n):
        for j in range(256):
            if (f_byte_cipher_list[j] ^ f_key_cipher[i]) == cipher_f[i] and (g_byte_cipher_list[j] ^ g_key_cipher[i]) == cipher_g[i]:
                flag[i] = j
                break
            
    print(flag.decode())
```
