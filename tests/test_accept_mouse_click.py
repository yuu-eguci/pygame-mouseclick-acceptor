import inspect

import pygame
import pytest
from pygame.locals import (
    K_DOWN,
    K_UP,
    KEYDOWN,
    KEYUP,
    MOUSEBUTTONDOWN,
    MOUSEBUTTONUP,
    MOUSEMOTION,
    MOUSEWHEEL,
    QUIT,
    K_a,
    K_c,
    K_x,
    K_z,
)

from accept_mouse_click import DummyEvent, switch

DEFAULT_KEYS = [(1, K_z), (2, K_c), (3, K_x), (4, K_UP), (5, K_DOWN)]


def mouse(type_, button):
    return pygame.event.Event(type_, button=button, pos=(0, 0))


@pytest.mark.parametrize(("button", "key"), DEFAULT_KEYS)
def test_default_mapping_returns_native_keydown(button, key):
    event = switch(mouse(MOUSEBUTTONDOWN, button))

    assert isinstance(event, pygame.event.Event)
    assert event.type == KEYDOWN
    assert event.key == key


def test_keydown_has_standard_key_attributes():
    event = switch(mouse(MOUSEBUTTONDOWN, 1))

    assert event.mod == pygame.KMOD_NONE
    assert event.unicode == ""
    assert event.scancode == 0
    assert event.window is None


def test_keydown_keeps_the_mouse_event_window():
    window = object()
    original = pygame.event.Event(MOUSEBUTTONDOWN, button=1, pos=(0, 0), window=window)

    assert switch(original).window is window


def test_custom_mapping_by_keyword_and_position():
    assert switch(mouse(MOUSEBUTTONDOWN, 2), scroll_click=K_a).key == K_a
    assert switch(mouse(MOUSEBUTTONDOWN, 3), K_a, K_a, K_UP).key == K_UP


def test_signature_is_backward_compatible():
    params = inspect.signature(switch).parameters
    positional = [
        (name, p.default)
        for name, p in params.items()
        if p.kind is p.POSITIONAL_OR_KEYWORD
    ]

    assert positional == [
        ("event", inspect.Parameter.empty),
        ("left_click", K_z),
        ("scroll_click", K_c),
        ("right_click", K_x),
        ("scroll_up", K_UP),
        ("scroll_down", K_DOWN),
    ]


@pytest.mark.parametrize(
    "original",
    [
        pygame.event.Event(QUIT),
        pygame.event.Event(MOUSEMOTION, pos=(0, 0), rel=(1, 1), buttons=(0, 0, 0)),
        pygame.event.Event(KEYDOWN, key=K_a, mod=0, unicode="a", scancode=4),
        pygame.event.Event(MOUSEWHEEL, x=1, y=0, flipped=False),
    ],
)
def test_other_events_are_returned_unchanged(original):
    assert switch(original) is original


@pytest.mark.parametrize("button", [6, 7])
def test_unknown_button_is_returned_unchanged_and_silently(button, capsys):
    original = mouse(MOUSEBUTTONDOWN, button)

    assert switch(original) is original
    assert capsys.readouterr() == ("", "")


def test_none_disables_a_button():
    original = mouse(MOUSEBUTTONDOWN, 1)

    assert switch(original, left_click=None) is original
    assert switch(mouse(MOUSEBUTTONDOWN, 3), left_click=None).key == K_x


def test_mousebuttonup_passes_through_by_default():
    original = mouse(MOUSEBUTTONUP, 1)

    assert switch(original) is original


@pytest.mark.parametrize(("button", "key"), DEFAULT_KEYS)
def test_keyup_opt_in_converts_mousebuttonup(button, key):
    event = switch(mouse(MOUSEBUTTONUP, button), keyup=True)

    assert isinstance(event, pygame.event.Event)
    assert event.type == KEYUP
    assert event.key == key


def test_keyup_opt_in_respects_none_and_unknown_buttons():
    disabled = mouse(MOUSEBUTTONUP, 1)
    unknown = mouse(MOUSEBUTTONUP, 6)

    assert switch(disabled, left_click=None, keyup=True) is disabled
    assert switch(unknown, keyup=True) is unknown


def test_keyup_is_keyword_only():
    with pytest.raises(TypeError):
        switch(mouse(MOUSEBUTTONUP, 1), K_z, K_c, K_x, K_UP, K_DOWN, True)


def test_switch_returns_native_event_not_dummy_event():
    event = switch(mouse(MOUSEBUTTONDOWN, 1))

    assert isinstance(event, pygame.event.Event)
    assert not isinstance(event, DummyEvent)
    assert not isinstance(DummyEvent(KEYDOWN, K_z), pygame.event.Event)


def test_dummy_event_construction_still_works():
    event = DummyEvent(KEYDOWN, K_z)

    assert (event.type, event.key) == (KEYDOWN, K_z)


def test_module_does_not_print(capsys):
    for button in range(1, 10):
        switch(mouse(MOUSEBUTTONDOWN, button))
        switch(mouse(MOUSEBUTTONUP, button), keyup=True)

    assert capsys.readouterr() == ("", "")


def test_event_queue_round_trip(display):
    """Synthetic events through the real (headless) pygame event queue."""
    for type_, button in [
        (MOUSEBUTTONDOWN, 1),
        (MOUSEBUTTONUP, 1),
        (MOUSEBUTTONDOWN, 6),
    ]:
        pygame.event.post(mouse(type_, button))

    converted = [
        switch(event, keyup=True)
        for event in pygame.event.get()
        if event.type in (MOUSEBUTTONDOWN, MOUSEBUTTONUP)
    ]
    assert [(e.type, getattr(e, "key", None)) for e in converted] == [
        (KEYDOWN, K_z),
        (KEYUP, K_z),
        (MOUSEBUTTONDOWN, None),
    ]

    for event in converted:
        pygame.event.post(event)
    received = [e for e in pygame.event.get() if e.type in (KEYDOWN, KEYUP)]
    assert [(e.type, e.key) for e in received] == [(KEYDOWN, K_z), (KEYUP, K_z)]
