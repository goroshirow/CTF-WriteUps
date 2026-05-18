# Flag for Switch

## / Overview

User-Agent書き換え

## / Writeup

Webの問題です。

通常のアクセスでは`Sorry, this page is only available for Switch`と表示されます。フラグが表示される条件を調べるために配布ファイルの`index.js`を見ると、アクセス制御は以下の部分で行われています。

```js
const userAgent = req.headers['user-agent'] || '';
if (userAgent.includes("Switch")) {
    res.send(htmlForSwitch);
} else {
    res.send(html);
}
```

`html`が通常ユーザに表示するページで、`htmlForSwitch`がフラグを表示するページです。`userAgent.includes("Switch")`という条件からリクエストヘッダの`User-Agent`に`Switch`が含まれている必要がある事が分かりました。`curl`を使って以下のリクエストを送信することでフラグが取れます。

```sh
$ curl -H "User-Agent: Switch" http://34.170.146.252:13697
```