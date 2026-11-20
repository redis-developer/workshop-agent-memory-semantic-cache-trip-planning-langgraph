"""
One line of log, shown by the layer it comes from, so you can see what called what. A node or a tool is not
indented, the domain function it calls is indented once, and the data function that one calls twice.

    log("search_memories")

You do not say which layer. It is found from the folder of the file that called `log`, and each layer has its
own color. Colors are left out when the output is not a terminal, or when NO_COLOR is set.

Where to call it: nodes, tools and domain functions log before they call anything, so they print above what
they call. A data function calls nothing else, so it logs once the work is done, with what came back.
"""

import os
import sys
from typing import NamedTuple


class Layer(NamedTuple):
    folder: str
    level: int
    color: str  # the number of one of the 256 terminal colors
    prefix: str


LAYERS = [
    Layer("/tools/", 0, "141", "tool: "),
    Layer("/agent_workflow/", 0, "36", ""),
    Layer("/domain/", 1, "33", ""),
    Layer("/data/", 2, "31", ""),  # Redis red
]

COLORS_ON = sys.stdout.isatty() and "NO_COLOR" not in os.environ


def log(message: str) -> None:
    # The file that called `log`
    file = sys._getframe(1).f_code.co_filename.replace("\\", "/")
    layer = next((candidate for candidate in LAYERS if candidate.folder in file), None)
    line = f"{'   ' * (layer.level if layer else 0)}{layer.prefix if layer else ''}{message}"
    print(f"\x1b[38;5;{layer.color}m{line}\x1b[39m" if layer and COLORS_ON else line, flush=True)
