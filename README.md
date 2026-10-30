AcceptMouseClick
===

pygame 作品でキーボード入力がうまく受け取れない環境 (昔の mac など) でも遊べるように、
マウスクリックをキーイベントへ変換するモジュール。

- Docker: 対応!
- Python: 3.11 - 3.15 (ライブラリ別の対応は下表)
- Linter: ruff
- Test: pytest

## パッと実行してみたい

仮想画面と合成イベントで lint とテストを実行する。

```bash
docker build -t accept-mouse-click-test .
docker run --rm accept-mouse-click-test
```

## 対応バージョン

| ライブラリ | Python |
| --- | --- |
| pygame 2.6 | 3.11 - 3.13 |
| pygame-ce 2.5 | 3.11 - 3.15 |

どちらも `import pygame` で使えるので、どちらか片方だけ入れる (同時に入れると衝突する)。

## 変換表 (デフォルト)

| マウス | `event.button` | キー |
| --- | --- | --- |
| 左クリック | 1 | `K_z` |
| スクロールクリック | 2 | `K_c` |
| 右クリック | 3 | `K_x` |
| 上スクロール | 4 | `K_UP` |
| 下スクロール | 5 | `K_DOWN` |

## Usage

`accept_mouse_click.py` をゲームと同じフォルダに置いて、イベントループで `switch` を通すだけ。
左クリックを Z キー、スクロールクリックを A キーにして、押されたキー名を表示する例:

```python
import pygame
from pygame.locals import K_a, K_z, KEYDOWN, QUIT

import accept_mouse_click

pygame.init()
screen = pygame.display.set_mode((320, 240))
running = True
while running:
    for event in pygame.event.get():
        event = accept_mouse_click.switch(
            event,
            left_click=K_z,
            scroll_click=K_a,
        )
        if event.type == KEYDOWN:
            print(pygame.key.name(event.key))
        elif event.type == QUIT:
            running = False
pygame.quit()
```

## API

`switch(event, left_click=K_z, scroll_click=K_c, right_click=K_x, scroll_up=K_UP, scroll_down=K_DOWN, *, keyup=False)`

- `MOUSEBUTTONDOWN` は pygame の本物の `KEYDOWN` イベント (`key`, `mod`, `unicode`, `scancode`, `window` 付き) になる。
- `keyup=True` を渡すと `MOUSEBUTTONUP` も `KEYUP` になる。デフォルトは今まで通り素通し。
- 引数に `None` を渡すとそのボタンは変換しない。
- 変換しないイベント (マウス以外、表にないボタン、`None` にしたボタン) は同じオブジェクトをそのまま返す。何も出力しない。
- `DummyEvent(type_, key)` は互換のため残してある。`switch` はもう返さない。
  戻り値は `pygame.event.Event` なので `isinstance(event, pygame.event.Event)` は True、`isinstance(event, accept_mouse_click.DummyEvent)` は False になる。

ホイールは pygame が 1 目盛りごとに `MOUSEBUTTONDOWN` と `MOUSEBUTTONUP` (ボタン 4 / 5) を続けて出すので、`keyup=True` だと `KEYDOWN` の直後に `KEYUP` が来る。
横スクロールと `MOUSEWHEEL` イベント、サイドボタン (6 / 7) はそのまま返す。

キーの状態を `pygame.key.get_pressed()` で見ているゲームには効かない。

## 開発

テストは SDL の dummy ドライバと合成イベントだけで動く (本物のマウス・キーボードやほかのアプリには触らない)。
実行方法は「パッと実行してみたい」と同じ。デフォルトは pygame-ce。pygame で試す場合は build に引数を足す:

```bash
docker build -t accept-mouse-click-test \
  --build-arg PYTHON_IMAGE=python:3.13-slim \
  --build-arg LOCK=requirements/pygame.txt .
```

ロックファイルの更新:

```bash
uv pip compile pyproject.toml --universal --python-version 3.11 --generate-hashes \
  --extra dev --extra pygame-ce -o requirements/pygame-ce.txt
uv pip compile pyproject.toml --universal --python-version 3.11 --generate-hashes \
  --extra dev --extra pygame -o requirements/pygame.txt
```

実機の mac でキー入力が本当に化けるか、実際のホイールやサイドボタンがどの番号で来るかは自動テストでは未確認。
確かめるときは Usage の例を実機で実行して、開いたウィンドウの中を自分でクリックする。
