import os
from typing import Literal

COLOR = Literal[
    "black",
    "red",
    "green",
    "yellow",
    "blue",
    "magenta",
    "cyan",
    "white"
]

MODIFIERS = Literal[
    "bold",
    "faint",
    "italic",
    "underline",
    "slow_blink",
    "rapid_blink",
    "reverse",
    "strikethrough",
    "none"
]

# Enable ANSI escape sequence processing in Windows
os.system("")

class TextFormat:
    # Reset
    RESET = "\033[0m"
    
    # Effects
    BOLD = "\033[1m"
    FAINT = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    SLOW_BLINK = "\033[5m"
    RAPID_BLINK = "\033[6m"
    REVERSE = "\033[7m"
    STRIKETHROUGH = "\033[9m"

    # Foreground colors
    FG_BLACK = "\033[30m"
    FG_RED = "\033[31m"
    FG_GREEN = "\033[32m"
    FG_YELLOW = "\033[33m"
    FG_BLUE = "\033[34m"
    FG_MAGENTA = "\033[35m"
    FG_CYAN = "\033[36m"
    FG_WHITE = "\033[37m"

    # Background colors
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"

def format_text(text: str, *formats: str):
    format_str = "".join([*formats])
    return f"{format_str}{text}{TextFormat.RESET}"

def color_from_str(color: COLOR) -> str:
    match color:
        case "black":
            return TextFormat.FG_BLACK
        case "red":
            return TextFormat.FG_RED
        case "green":
            return TextFormat.FG_GREEN
        case "yellow":
            return TextFormat.FG_YELLOW
        case "blue":
            return TextFormat.FG_BLUE
        case "magenta":
            return TextFormat.FG_MAGENTA
        case "cyan":
            return TextFormat.FG_CYAN
        case "white":
            return TextFormat.FG_WHITE
  
def modifier_from_str(modifier: MODIFIERS):
    match modifier:
        case "bold":
            return TextFormat.BOLD
        case "faint":
            return TextFormat.FAINT
        case "italic":
            return TextFormat.ITALIC
        case "underline":
            return TextFormat.UNDERLINE
        case "slow_blink":
            return TextFormat.SLOW_BLINK
        case "rapid_blink":
            return TextFormat.RAPID_BLINK
        case "reverse":
            return TextFormat.REVERSE
        case "strikethrough":
            return TextFormat.STRIKETHROUGH
        case "none":
            return
        
def modifier_from_list(modifiers: list[MODIFIERS]) -> str:
    modifier_str = ""
    for modifier in modifiers:
        modifier_str += modifier_from_str(modifier) if modifier_from_str(modifier) else ""

    return modifier_str