# rsa_oracle

## / Overview

RSA準同型dec偽装

## / Writeup

復号オラクルにpassword.encを直接聞けない。

* 2を暗号化オラクルに聞く
* 結果をenc_passwordと掛け算する
* それを復号オラクルに聞く
* 返ってくるのは2*password

`secret.enc`の先頭が`Salted__`なのでaesと判断。

```
openssl enc -d -aes-256-cbc -in secret.enc -out decrypted.txt
```

でパスワードに復号結果をhexで入力