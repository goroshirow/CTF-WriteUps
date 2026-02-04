from Crypto.Util.number import long_to_bytes


# FactorDBの結果を使用
p = 87569276771316598432602743640004330672211
q = 106064726489863337434900206767547070156877

N = p * q
phi = (p - 1) * (q - 1)

# 与えられた暗号文
c1 = 7827437377925724428078233147899924081225364249930858942421079276821876942757073519
c2 = 8887391738833944793881713037947023989163050343070393147424888589467627754249865604

# c1^{-3} mod N を計算
core_inv = pow(c1, -3, N)

# m^{1337 - 4k} mod N を計算
mX = (c2 * core_inv) % N

# k = 0, 1, 2, 3 に対して復号を試みる。
for k in range(4):
    try:
        X_inv = pow(1337 - k * N, -1, phi)
    except ValueError:
        # 逆元が存在しない場合はスキップ
        continue
    m = pow(mX, X_inv, N)
    print(long_to_bytes(m))