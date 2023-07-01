from _commands import (
    command
)
import os

@command(
    name = "python",
    aliases = [
        "python3",
        "pyexec"
    ]
)
def python_execute(name: str = "", *args):
    if name == "":
        os.system("python")
    else:
        os.system(f"python {name} {' '.join(args) if args else ''}")
