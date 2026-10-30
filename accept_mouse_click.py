#!/usr/bin/env python

"""accept_mouse_click

pygame作品でキーボード入力がうまく受け取れない環境でも辛くも動かすため
マウスクリックをキー入力に化けさせる応急処置モジュール。

使用例: 左クリックをZキー、スクロールボタンをAキーに変換したい場合。
    import accept_mouse_click
    ...
    for event in pygame.event.get():
        event = accept_mouse_click.switch(
            event,
            left_click=K_z,
            scroll_click=K_a
            )
"""

import pygame
import pygame.locals as pgl

_KEY_TYPES = {
    pgl.MOUSEBUTTONDOWN: pgl.KEYDOWN,
    pgl.MOUSEBUTTONUP: pgl.KEYUP,
}


def switch(
    event,
    left_click=pgl.K_z,
    scroll_click=pgl.K_c,
    right_click=pgl.K_x,
    scroll_up=pgl.K_UP,
    scroll_down=pgl.K_DOWN,
    *,
    keyup=False,
):
    """マウスクリックをキー入力に変換します。
    デフォルトでは
        左クリック:Z
        スクロールクリック:C
        右クリック:X
        上スクロール:UP
        下スクロール:DOWN
    かえたいとこだけ指定してください。None にしたボタンは変換しません。
    keyup=True にすると MOUSEBUTTONUP も KEYUP に変換します。
    変換しないイベントはそのまま返します。
    """

    if event.type == pgl.MOUSEBUTTONUP and not keyup:
        return event
    key_type = _KEY_TYPES.get(event.type)
    if key_type is None:
        return event

    change_table = {
        1: left_click,
        2: scroll_click,
        3: right_click,
        4: scroll_up,
        5: scroll_down,
    }
    key = change_table.get(event.button)
    if key is None:
        return event

    return pygame.event.Event(
        key_type,
        key=key,
        mod=pgl.KMOD_NONE,
        unicode="",
        scancode=0,
        window=getattr(event, "window", None),
    )


class DummyEvent:
    """互換のため残してあるeventのダミー。switch はもう返しません。
    typeとkeyだけを持ちます。
    """

    def __init__(self, type_, key):
        self.type = type_
        self.key = key
