# Parroting

## / Overview

scriptタグを挿入してalertする

## / Writeup

http://web.katagaitai-ctf.net/http/step2.php

の入力フォームに`hi`と送ると
```html
<span id="rep">hi</span>
```
になる。`</span><script>alert('hi');</script>`を送るとフラグゲット