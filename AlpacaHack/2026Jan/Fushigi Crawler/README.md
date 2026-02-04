# Fushigi Crawler

## / Overview

サーバーから指定したサイトへの`Request Header`を見る。

## / Writeup

サーバーには、ユーザーが指定したサイトへアクセス可能かを確認するクローラーが稼働している。

具体的には、フロントエンド（`index.html`）の以下のコードで、 `/api/crawl-request` に対して入力データを送信しする。

```js
const res = await fetch("/api/crawl-request", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ url: form.url.value.trim() }),
        });
```

これを受けたバックエンド（`index.js`）では、以下の処理によって指定された URL への到達可能性を確認する。

```js
app.post("/api/crawl-request", async (req, res) => {
  const url = req.body?.url;
  if (typeof url !== "string" || (!url.startsWith("http://") && !url.startsWith("https://")))
    return res.status(400).send("Invalid url");
  try {
    const r = await fetch(url, { headers: { FLAG }, signal: AbortSignal.timeout(5000) }); // !!
    if (!r.ok) return res.status(502).send("Fetch failed");
    return res.sendStatus(200);
  } catch (e) {
    return res.status(500).send(`Something wrong: ${e.name}`);
  }
});
```

ここで注目したいのが`const r = await ...`の行で、入力した URL にリクエストを投げるときにHTTPヘッダーにFLAGを含めている。

つまり、自分が通信を観測できるWeb サーバーを構築し、そこへクローラーを誘導すれば、リクエストヘッダーの中から FLAG を抽出できることになる。

今回は、自分の PC のポートを直接開放する代わりに、[Webhook.site](https://webhook.site)というサービスを利用した。ここで作成したurlにクローラーでアクセスしてもらうことでヘッダー内のFLAGを確認することができた。