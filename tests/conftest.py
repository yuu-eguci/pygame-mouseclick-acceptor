import os

# Headless only: never open a real window or touch real input devices.
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame  # noqa: E402
import pytest  # noqa: E402


@pytest.fixture
def display():
    """Dedicated 1x1 dummy surface so the event queue works."""
    pygame.display.init()
    surface = pygame.display.set_mode((1, 1))
    pygame.event.clear()
    yield surface
    pygame.display.quit()
