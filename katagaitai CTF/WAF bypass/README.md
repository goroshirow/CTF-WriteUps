# WAF bypass

## / Overview

WAF回避のためにフラグを分けて受信

## / Writeup

http://web.katagaitai-ctf.net/http/step5.html

にアクセスすると、`The flag is [censored] ` と表示されます。

これは途中にフラグの内容をフィルターするWAFが存在するからです。

フィルター方法は次のようになっています。

```js
var proxy = require('express-http-proxy');
var app = require('express')();

app.use('/', proxy('http5', {
    userResDecorator: function(proxyRes, proxyResData, userReq, userRes) {
        // Replace html contents to censor flags!
        return String(proxyResData).replaceAll(/katagaitai-CTF\{.*\}/g, "[censored]");
    }})
);

app.listen(80)
```

`/katagaitai-CTF\{.*\}/g`は`katagaitai-CTF{`で始まって`}`で終わる文字列を`[censored]`に置き換えるという意味です。プレイヤーはサーバーやWAFに何か操作を加えられるわけではないので、受け取り方を工夫します。

具体的には、burpでリクエストヘッダに`Range: bytes=0-48`を追加すると、受け取るデータは`}`の一つ前までとなって`}`の欠けたフラグが表示されます。