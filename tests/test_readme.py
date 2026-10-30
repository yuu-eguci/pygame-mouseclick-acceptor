import re
from pathlib import Path

import pygame
from pygame.locals import MOUSEBUTTONDOWN, QUIT

README = Path(__file__).parents[1] / "README.md"


def test_readme_quickstart_runs(monkeypatch, capsys):
    """Run the README Usage block headless, feeding it synthetic clicks."""
    text = README.read_text(encoding="utf-8")
    code = re.search(r"```python\n(.*?)```", text, re.S).group(1)
    real_get = pygame.event.get
    calls = []

    def scripted_get(*args, **kwargs):
        calls.append(None)
        assert len(calls) < 10, "quickstart did not stop on QUIT"
        if len(calls) == 1:
            for button in (1, 2, 4):
                pygame.event.post(
                    pygame.event.Event(MOUSEBUTTONDOWN, button=button, pos=(0, 0))
                )
            pygame.event.post(pygame.event.Event(QUIT))
        return real_get(*args, **kwargs)

    monkeypatch.setattr(pygame.event, "get", scripted_get)
    exec(compile(code, str(README), "exec"), {"__name__": "__main__"})

    assert capsys.readouterr().out.split() == ["z", "a", "up"]
