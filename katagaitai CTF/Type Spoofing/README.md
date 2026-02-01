
# Type Spoofing

## / Overview

`Content-Type`の書き換え

## / Writeup

http://web.katagaitai-ctf.net/http/step4.php

にアクセス後、`sample.png` を送信してみます。

ヘッダー確認すると

```
------WebKitFormBoundaryWePRV0HUlNcWERYy
Content-Disposition: form-data; name="upload"; filename="sample.png"
Content-Type: image/png
```

と書かれています。次に`attack.php`を送信した時のヘッダを確認すると

```
------WebKitFormBoundary7hJP8JQAhmAWsipI
Content-Disposition: form-data; name="upload"; filename="attack.php"
Content-Type: application/octet-stream
```

と書かれています。`Content-Type`を変えることで騙せそうです。burpで`attack.php`を送信するときのヘッダを、`Content-Type: image/png`に書き換えるとフラグゲット