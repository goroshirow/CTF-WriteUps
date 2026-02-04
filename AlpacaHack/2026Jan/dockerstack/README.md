# dockerstack

## / Overview

docker image の layer からフラグを復元する。

## / Writeup

まずは問題の流れを紐解いていきます。

`build`ディレクトリを見ると`build.sh`というファイルがあるので、中の処理を見ます。

```bash
set -eu

# Alpaca{...}->{...}に加工してbase64でflag.b64.txtに保存
sed 's/^Alpaca//' flag.txt | base64 -w0 | tr -d '=' > flag.b64.txt 

IMAGE_NAME=output-image
# Dockerfileでimageをbuild
docker image build -t "$IMAGE_NAME" .
# imageをtarで保存
docker image save "$IMAGE_NAME" > "$IMAGE_NAME.tar"
# imageを削除
docker image rm "$IMAGE_NAME"

rm flag.b64.txt
mv "$IMAGE_NAME.tar" ..
```

また`Dockerfile`は次のように記述されています。

```docker
FROM alpine:3.23.2

WORKDIR /app
COPY flag.b64.txt .
RUN rm flag.b64.txt
```

一度`flag.b64.txt`をコピーしてから削除していますね。このファイルを復元できるのでしょうか？

### imageの再現

`output-image.tar`からimageを以下のコマンドで作成します。

```bash
docker load < output-image.tar
```

`output-image:latest`というimageが作成されました。この状態で、コンテナの作成/起動を試してみてください。`/app`ディレクトリにフラグがないことを確認できます。

### layerの確認

フラグは一度コピーされてから削除されているので、何かロールバック的なことができればフラグを取得できそうな気がします。imageについて詳しく調べると、`layer`という仕組みで構成されていることが分かりました。

> こちらの記事がわかりやすいです。
> 
> qiita.com/zembutsu/items/24558f9d0d254e33088f

dockerには`docker history`という、 layer を確認できるコマンドが存在するので、先程作成した image に試してみましょう。

```bash
$ docker history output-image
IMAGE          CREATED       CREATED BY                                      SIZE      COMMENT
935c27cb58c7   2 weeks ago   RUN /bin/sh -c rm flag.b64.txt # buildkit       12.3kB    buildkit.dockerfile.v0
<missing>      2 weeks ago   COPY flag.b64.txt . # buildkit                  12.3kB    buildkit.dockerfile.v0
<missing>      2 weeks ago   WORKDIR /app                                    8.19kB    buildkit.dockerfile.v0
<missing>      4 weeks ago   CMD ["/bin/sh"]                                 0B        buildkit.dockerfile.v0
<missing>      4 weeks ago   ADD alpine-minirootfs-3.23.2-x86_64.tar.gz /…   9.11MB    buildkit.dockerfile.v0
```

やはり一つ前の層には、フラグの情報が残っていそうです。

実は`IMAGE`のカラムが`<missing>`でなければロールバックする方法があるみたいなのですが、今回は適用できません。

### `output-image.tar`を展開する

次はアーカイブファイルを直接見てみます。

展開すると、メタデータが記載されている`manifest.json`が確認できます。中身を整形すると次のようになっています。

```json
[
	{
		"Config": "blobs/sha256/ddceb7aa914367258c7573c22a200ef88612608dfc3694102256cc1076b3fcbd",
		"RepoTags": [
			"output-image:latest"
		],
		"Layers": [
			"blobs/sha256/7bb20cf5ef67526cb843d264145241ce4dde09a337b5be1be42ba464de9a672d",
			"blobs/sha256/c57a625e7523f654b7256b33b17e43cf74c8650bd1a441884a70615d7327b85b",
			"blobs/sha256/265c6b6c91fb0cab080e43824b80565687c834631d570b43ba64196e8a6bb20b",
			"blobs/sha256/0531badbea1bbfd8db4244371c4c89e587f729a37c1dbf6dbc75a89bb09e003c"
		],
		"LayerSources": {
			"sha256:0531badbea1bbfd8db4244371c4c89e587f729a37c1dbf6dbc75a89bb09e003c": {
				"mediaType": "application/vnd.oci.image.layer.v1.tar",
				"size": 2560,
				"digest": "sha256:0531badbea1bbfd8db4244371c4c89e587f729a37c1dbf6dbc75a89bb09e003c"
			},
			"sha256:265c6b6c91fb0cab080e43824b80565687c834631d570b43ba64196e8a6bb20b": {
				"mediaType": "application/vnd.oci.image.layer.v1.tar",
				"size": 2560,
				"digest": "sha256:265c6b6c91fb0cab080e43824b80565687c834631d570b43ba64196e8a6bb20b"
			},
			"sha256:7bb20cf5ef67526cb843d264145241ce4dde09a337b5be1be42ba464de9a672d": {
				"mediaType": "application/vnd.oci.image.layer.v1.tar",
				"size": 8724480,
				"digest": "sha256:7bb20cf5ef67526cb843d264145241ce4dde09a337b5be1be42ba464de9a672d"
			},
			"sha256:c57a625e7523f654b7256b33b17e43cf74c8650bd1a441884a70615d7327b85b": {
				"mediaType": "application/vnd.oci.image.layer.v1.tar",
				"size": 1536,
				"digest": "sha256:c57a625e7523f654b7256b33b17e43cf74c8650bd1a441884a70615d7327b85b"
			}
		}
	}
]
```

この中で`layer`の情報を保持していそうなのは

* `blobs/sha256/7bb20cf5ef67526cb843d264145241ce4dde09a337b5be1be42ba464de9a672d`
* `blobs/sha256/c57a625e7523f654b7256b33b17e43cf74c8650bd1a441884a70615d7327b85b`
* `blobs/sha256/265c6b6c91fb0cab080e43824b80565687c834631d570b43ba64196e8a6bb20b`
* `blobs/sha256/0531badbea1bbfd8db4244371c4c89e587f729a37c1dbf6dbc75a89bb09e003c`

です。ファイルは`mediaType`からtarファイルであることが分かります。

どの様なファイルが含まれているか、それぞれ確認します。

```bash
tar tvf blobs/sha256/...
```

すると`blobs/sha256/265c...`に`flag.b64.txt`が含まれていました。後は`tar xvf`でファイルを展開すれば中身を確認できます。

中身はbase64でエンコードされているので最後にデコードするとフラグが得られます。