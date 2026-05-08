# Vending Machine

## / Overview

pythonの`find`と`pop`の仕様を使用

## / Writeup

自動販売機を模したプログラムで`a`から`e`を選ぶと変数`mark`に保存され，それぞれに対応したジュースが出てきます．更に`f`にはフラグが割り当てられています．しかし以下のルールによって`f`を選ぶことはできません．

```py
if mark not in ['a', 'b', 'c', 'd', 'e']: # No 'f'? Hmm...
            print("Invalid choice.")
            return
```

ところで自動販売機なのでジュースには在庫が設定されています．在庫は

```py
self.stock = 'a'*30 + 'b'*60 + 'c'*20 + 'd'*50 + 'e'*40 + 'f' # 'aaa...eeef'
```

で管理されています．`a`から`e`が選ばれると`loc = self.stock.find(mark)`によって`stock`で初めて`mark`が出現する位置のインデックスが返されます．**`mark`が文字列内に存在しない（在庫が切れている）なら-1を返します**．そして`loc`の位置の文字が`item`にポップされます．

在庫が切れていて`-1`が`loc`に入った時，ポップされる値は文字列の-1番目，つまり`f`になります．よってその後の処理によってフラグが表示されます．

```py
item = stock_list.pop(loc)
# --snip--
if item == 'f':
    print(f"Flag:", FLAG)
else:
    print("Thank you!")
```

まとめとして，いずれかのジュースのstockをなくしてから，もう一度そのジュースを選ぶとフラグが取れます．