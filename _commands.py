from typing import Callable
from TPC import format_text, TextFormat

GLOBAL_COMMAND_MANAGER_HNDL = ""
CURSOR_MOVE_TO = "\033[<X>;<Y>H"
ENTER_ALTERNATE_SCREEN = "\033[?1049h"
EXIT_ALTERNATE_SCREEN = "\033[?1049l"

class Command:
    name: str
    func: Callable
    aliases: list[str]

    def execute(self): pass

def newline_output(func):
    """
    Add newlines around this command's prints
    """
    def wrapper(*args, **kwargs):
        print()
        out = func(*args, **kwargs)
        print()
        return out
    return wrapper

"""
This uses the goofy ahh fact that functions can be 
assigned to with func.item = name like some
random object. Odd, but cleans up the syntax
a bit.
"""
def command(name: str, aliases: list[str], debugmode: bool = False):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if debugmode:
                func(*args, **kwargs)
            else:
                try: 
                    func(*args, **kwargs)
                except TypeError:
                    print(format_text(
                        "Invalid arguments for command\n",
                        TextFormat.FG_RED,
                        TextFormat.BOLD
                    ))
        wrapper.name = name
        wrapper.aliases = aliases
        return wrapper
    return decorator

def alternate_screen(func):
    def wrapper(*args, **kwargs):
        print(ENTER_ALTERNATE_SCREEN)
        func(*args, **kwargs)
        print(EXIT_ALTERNATE_SCREEN)

"""
Excludes a function from being a command
"""
def exclude(func):
    def wrapper(*args, **kwargs):
        func.notcommand = True
        out = func(*args, **kwargs)
        return out
    return wrapper

"""
Sets the first argument of the function to the
current CommandManager
""" 
def with_manager_handle(func):
    def wrapper(*args, **kwargs):
        return func(GLOBAL_COMMAND_MANAGER_HNDL, *args, **kwargs)
    return wrapper

#class ArgumentOverlapError(Exception):
    """
    A provided argument would cause 2 args to be in one
    position, which is an illegal operation
    """
#
#class ArgumentNotSuppliedError(Exception):
    """
    The argument was not supplied in the correct position
    """
#
#class InvalidArgumentTypeError(Exception):
    """
    The argument was unable to cast to the specified type
    """
#
#class Args:
#    def __init__(self, provided_args: list[str]):
#        self.args = []
#        self.provided_args = provided_args
#
#    def addarg(self, name: str, position: int, type_of_arg: Type):
#        for arg in self.args:
#            if arg['position'] == position:
#                raise ArgumentOverlapError('This position is already in use')#
#        
#        try:
#            item = self.provided_args[position]
#        except IndexError:
#            raise ArgumentNotSuppliedError('The argument was not supplied')
#
#        if not item or item is None:
#            raise ArgumentNotSuppliedError('The argument was not supplied')
#
#        try:
#            typed_item = type_of_arg(item)
#        except (TypeError, ValueError):
#            raise InvalidArgumentTypeError(f'Cannot cast str to {type_of_arg}')
#
#        new_arg = {
#            'name': name,
#            'position': position,
#            'value': typed_item
#        }
#
#        self.args.append(new_arg)
#        
#    def __getitem__(self, index):
#        if isinstance(index, str):
#            for item in self.args:
#                if item['name'] == index:
#                    return item['value']
#            raise IndexError(f'Invalid index: {index}')
#        elif isinstance(index, int):
#            for item in self.args:
#                if item['position'] == index:
#                    return item['value']
#            raise IndexError(f'Invalid index: {index}')

