from abc import ABC, abstractmethod
from typing import Callable
from .formatting import format_text, TextFormat
import readline
import os

# LIST [
#   DICT {
#       name: <NAME> STR, 
#       func: <FUNC> CALLABLE, 
#       aliases: LIST [
#         alias STR
#       ]
#   }
# ]
REGISTERED_TYPE = list[
    dict[
        "name": str, 
        "func": Callable, 
        "aliases": list[str]
    ]
]

class AutocompleteCompleter:
    def __init__(self, options: list[str]):
        self.options = options

    def complete(self, text, state):
        response = None
        if state == 0:
            if text:
                self.matches = [option for option in self.options if option.startswith(text)]
            else:
                self.matches = self.options[:]
        try:
            response = self.matches[state]
        except IndexError:
            response = None
        return response

class Reader(ABC):
    @abstractmethod
    def readline(self) -> str: pass

class SignalReloadError(Exception):
    """
    Signals for a reload
    """
    pass

class StdReader(Reader):
    def __init__(self, prompt: str):
        self.prompt = prompt

        # Enable tab completion
        readline.set_completer(self.complete)
        readline.parse_and_bind("tab: complete")

    def readline(self) -> str:
        line = input(self.prompt).lower()

        return line

    def complete(self, text, state):
        options = self.get_completions()
        matches = [option for option in options if option.startswith(text)]
        return matches[state] if state < len(matches) else None

    def get_completions(self) -> list[str]:
        return [obj.lower() for obj in os.listdir()]

class Processor(ABC):
    @abstractmethod
    def split_args(self, command: str) -> tuple[str, list[str]]: pass

class StdProcessor(Processor):
    """
    Turns commands into a tuple of the command
    and a list of the args. Replaces all matching 'symbols' given
    in __init__ and changes them to the value specified in
    the dict
    """
    
    def __init__(self, symbols: dict, config):
        # NOTE: config is a Config class, need to
        # fix the imports to fix this
        self.symbols = symbols
        self.config = config
    
    def split_args(self, command: str) -> tuple[str, list[str]]:
        # The symbols map is defined in config.toml
        # under [StdProcessorSymbols]
        # config is a Config class
        symbols = self.config.seek('StdProcessorSymbols')

        for symbol, value in symbols.items():
            sy_var = "<" + symbol + ">"
            value = value.replace("<home>", os.path.expanduser("~"))

            command = command.replace(sy_var, value.lower())

        for var, value in symbols.items():
            command.replace(
                var,
                value.replace("<HOME>", os.path.expanduser("~"))
            )
        
        # The args will be in the format "<cmd> <arg1> <arg2>"
        split_command = command.strip().split(" ")

        true_args = []

        for arg in split_command[1:]:
            if arg and not arg == "":
                true_args.append(arg)

        return (split_command[0], true_args)

class CommandNotFoundError(Exception):
    """
    The command was not found
    """

class CommandManager:
    """
    A singleton observer that will take a Reader, and some subscribers
    to certain commands (see register_command) and then will
    trigger functions when the command is run
    """

    def __init__(
            self, 
            reader: Reader, 
            processor: Processor, 
            invalid_command: Callable, 
            is_debug_mode: bool = False
            ):
        self.reader = reader
        self.processor = processor
        self.registered: REGISTERED_TYPE = []
        self.invalid_command = invalid_command
        self.is_debug_mode = is_debug_mode

    def register_command(self, 
                         command: str, 
                         func: Callable, 
                         aliases: list[str] = []
                        ):
        self.registered.append(
            {"name": command, "func": func, "aliases": aliases}
        )

    def deregister_command(self, command: str):
        for cmd in self.registered:
            if cmd['name'] == command:
                self.registered.remove(cmd)
                return

        raise CommandNotFoundError(f'The command {command} was not registered')

    def execute_one(self):
        line = self.reader.readline()
        name, args = self.processor.split_args(line)

        if not line:
            return

        for cmd in self.registered:
            if name == cmd["name"]:
                if self.is_debug_mode:
                    cmd["func"](*args)
                    print(f"Executed command: {name}")
                else:
                    try:
                        cmd["func"](*args)
                    except Exception as E:
                        if isinstance(E, SignalReloadError):
                            raise SignalReloadError
                        
                        print(format_text(
                            f"The command {name} raised an error: {E}\n",
                            TextFormat.FG_RED
                        ))
                return

            for alias in cmd["aliases"]:
                if name == alias:
                    if self.is_debug_mode:
                        cmd["func"](*args)
                        print(f"Executed command: {name}")
                    else:
                        try:
                            cmd["func"](*args)
                        except Exception as E:
                            if isinstance(E, SignalReloadError):
                                raise SignalReloadError
                            
                            print(format_text(
                                f"The command {name} raised an error: {E}",
                                TextFormat.FG_RED
                            ))
                    return
                
        self.invalid_command(name, args)

    def is_command(self, command_name: str):
        for cmd in self.registered:
            if cmd['name'] == command_name:
                return True
            
        return False

    def __str__(self):
        return f"CommandManager(registered={self.registered})"

    def __repr__(self):
        return f"CommandManager(registered={self.registered})"

