from .formatting import (
    format_text,
    color_from_str,
    modifier_from_list,
    COLOR,
    MODIFIERS
)

class PromptBuilder:
    def __init__(self):
        self.elements = []

    def add(self, item: str, color: COLOR = "white", *modifiers: MODIFIERS):
        self.elements.append(
            format_text(
                item,
                color_from_str(color),
                modifier_from_list([*modifiers]) if modifiers else ""
            )
        )

    def radd(self, item: str):
        self.elements.append(
            item
        )

    def fetch(self, split_char: str = " "):
        return split_char.join(self.elements)