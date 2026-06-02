# Cache Me If You Can

## / Overview

クエリストリングによる nginx proxy cache のバイパスの問題です。

チャレンジサーバを生成すると20分のタイムリミット付きでWebサイトにアクセスできます。このサーバで稼働しているサービスのソースコードが配られていて、クライアントとWebサーバの間にnginxのproxyが関与していることが分かります。

このproxyの役割はページをキャッシュすることです。つまりクライアントの2回目以降のサイトへのアクセスは、このproxyによってキャッシュされている情報にアクセスします。このキャッシュの期限は365日に設定されています。

一方でフラグはWebサーバに保存されていて、サブディレクトリ`/flag`に1回目アクセスをすると`Cache me if you can.`が表示されますが、2回目以降のアクセスでフラグが表示されるような設定になっています。

ここで問題は、proxyが2回目以降のアクセスを既にキャッシュ済みの`Cache me if you can.`を表示するような仕組みになっているために、Webサーバまで到達できないことです。この状況を打破するためにはproxyをバイパスしてwebサーバの`/flag`に2回アクセスする方法を見つけなければなりません。

## / Writeup

`nginx cache bypass`や`nginx cache avoid`など関連しそうなワードで検索しますが、今回使えそうな手法がなかなか出てきません。なのでGeminiに`nginxでキャッシュを無視してページを読み込む方法`と聞くと、**Cache Busting**という方法があると分かりました。これは**URLの後ろにダミーのクエリストリング**をつけることで、新しいURLとして認識させて同じページを見る方法です。

なので次のように2回Webサイトにアクセスすればフラグがゲットできます。

- 1回目
```
http://34.170.146.252:38555/flag
```

- 2回目
```
http://34.170.146.252:38555/flag?v=1
```

nginx proxy はキャッシュを探すキーとして`proxy_cache_key`というパラメータを使っています。以下にも示すようにデフォルトではURLのクエリストリング(`args`)まで使うように設定されているため、違うクエリストリングを指定すると同じURLでもキャッシュをスルーすることができます[[1]](https://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_cache_key)。

> ```
> Syntax:   proxy_cache_key string;
> Default:  proxy_cache_key $scheme$proxy_host$request_uri;
> Context:  http, server, location
> ```
> 
> Defines a key for caching, for example
>
> ```
> proxy_cache_key "$host$request_uri $cookie_user";
> ```
> 
> By default, the directive’s value is close to the string
>
> ```
> proxy_cache_key $scheme$proxy_host$uri$is_args$args;
> ```

リクエストを受け取ったWebサーバは、要求していないクエリストリングを無視し、単に`/flag`にアクセスしたときの結果を返すため、ページの更新に成功します。

Cache Bustingは有名なテクニックらしく、CDNやリバースプロキシを無視して更新されたWebサイトを見に行く時に使えるみたいです[[2]](https://zenn.dev/mindwood/articles/ba4594c53a93b0)。

私にとっては難しいチャレンジでしたが、Webに精通している人にとってはEasyなチャレンジだったのでしょうか？

## / reference

- [1] Module ngx_http_proxy_module https://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_cache_key
- [2] ブラウザのキャッシュを無効化する方法 https://zenn.dev/mindwood/articles/ba4594c53a93b0