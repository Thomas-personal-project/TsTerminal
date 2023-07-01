# TsTerminal
A windows-based open-source python-based terminal emulator, designed to be configurable and editable. It uses a config.toml file to make most of its desitions. Please note that this is my first big project so if you have any issues or questions feel free to let me know and i'll update things accordingly.

## INSTALLATION
To install, simply run the install.py script to add the correct modules to PATH, and ensure you have the following modules avaliable:
 - PrettyTable
 - TOML

## USAGE
Simply run the main.py file, and the terminal will start!

## Modules and module loading
The terminal is extensible, so you can add commands via either the Commands folder or the 'load' command

*TO ADD USING 'Commands'*:
Create a new python file in the Commands folder. Then, import _commands and TPC in this file. To create a new command, use:  

```
@_commands.command(
  name = "command_name",
  aliases = ["alias1", "alias2"]
)
def helloworld():
  print("Hello, world!")
```

Then, in __init__.py in the Commands folder, add:

```
from .file_name import (
  helloworld
)
```

And now the ```helloworld``` command is avaliable in your shell! Please note that you can only export functions, not classes with the dunder call specified.

*TO ADD USING 'load'*:
To add a module using 'load', simply create a module file as described above, and place it wherever is convient on your system (usually it is good to put it in a dedicated folder or in the installation directory). Then, when in your terminal, use the command:

```
load <path/to/file>
```

And the module will be loaded into your session. Keep in mind that modules in Commands are always loaded but external modules loaded with ```load``` are not and are session-only.
