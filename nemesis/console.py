#!/usr/bin/env python
# -*- coding: utf-8 -*-

from rich.console import Console
from rich.text import Text
from rich.theme import Theme

nemesis_theme = Theme(
    {
        "resource": "bold purple",
        "add": "bold green",
        "change": "yellow",
        "remove": "bold red",
        "error": "red",
        "function": "blue",
    }
)
console = Console(theme=nemesis_theme)
