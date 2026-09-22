from __future__ import annotations

from rich.console import Console
from rich.theme import Theme

# Signal orange + acid lime. Not the usual cyan CLI skin.
FOREX_THEME = Theme(
    {
        "brand": "bold #FF5A1F",
        "accent": "bold #C8FF3D",
        "ice": "#7EE8FF",
        "ok": "#C8FF3D",
        "warn": "#FFB020",
        "danger": "bold #FF3B5C",
        "muted": "#8A7A70",
        "field": "bold #FFE8C8",
        "value": "#FFFFFF",
        "prompt": "bold #FF5A1F",
        "log": "#A8D4C8",
    }
)

console = Console(theme=FOREX_THEME, highlight=False)
BORDER = "#FF5A1F"
