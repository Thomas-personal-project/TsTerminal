from _commands import command, newline_output, with_manager_handle, exclude
from TPC import format_text, color_from_str, Config, TextFormat, CommandManager
import prettytable
import os
import datetime
import importlib

PATH_HISTORY = []
EXTERNAL_COMMANDS = []
FBLACKLIST = [
    "main.py",
    "_commands.py",
    "config.py",
    "formatting.py",
    "line_listener.py",
    "prompt_builder.py"
]

class InvalidPathError(OSError):
    """The path was invalid"""
    pass

@command(
    name = "cls", 
    aliases = [
        "clear"
    ]
)
def clear_screen():
    os.system("cls")

@command(
    name = "cd", 
    aliases = [
        "set-dir", 
        "set-directory"
    ]
)
@newline_output
def goto(abs_fpath: str):
    if not os.path.isdir(abs_fpath):
        print(format_text(
            "Item is not a valid directory",
            TextFormat.FG_RED,
            TextFormat.BOLD
        ))
        return

    PATH_HISTORY.append(abs_fpath)
    os.chdir(abs_fpath)

    if bool(Config().seek('Cd')['do_path_confirmation']):
        print(format_text(
            os.path.abspath("."),
            TextFormat.FG_GREEN,
            TextFormat.BOLD
        ))

@command(
    name = "ls", 
    aliases = [
        "dir"
    ]
)
@newline_output
def list_directories(*args):
    try:
        dir = args[0]
    except IndexError:
        dir = "."

    dirs = [item for item in os.listdir(dir) if os.path.isdir(os.path.join(dir, item))]
    files = [item for item in os.listdir(dir) if os.path.isfile(os.path.join(dir, item))]

    if not dirs and not files:
        print(format_text(
            "Directory is empty!",
            TextFormat.FG_RED,
            TextFormat.BOLD
        ))
        return

    table = prettytable.PrettyTable()
    table.field_names = [
        "Filename",
        "Type",
        "Last write time",
        "Readable",
        "Writable"
    ]

    rows = []

    for item in dirs:
        current_row = []
        if item in Config().seek("Ls")["exclude"]:
            continue
        current_row.append(item)
        current_row.append("Folder")
        current_row.append(str(datetime.datetime.fromtimestamp(os.path.getmtime(item))))
        current_row.append(str(os.access(item, os.R_OK)))
        current_row.append(str(os.access(item, os.W_OK)))
        rows.append(current_row)

    for item in files:
        current_row = []
        if item in Config().seek("Ls")["exclude"]:
            continue
        current_row.append(item)
        current_row.append("File")
        current_row.append(str(datetime.datetime.fromtimestamp(os.path.getmtime(item))))
        current_row.append(str(os.access(item, os.R_OK)))
        current_row.append(str(os.access(item, os.W_OK)))
        rows.append(current_row)

    table.add_rows(rows)

    print(format_text(
        table,
        color_from_str(Config().seek("Ls")["table_color"]),
        TextFormat.BOLD
    ))

@command(
    name  ="file", 
    aliases = [
        "touch", 
        "new-item"
    ]
)
@newline_output
def create_file(*args):
    try:
        filename = args[0]
    except IndexError:
        print(
            format_text(
                "Please provide a filename",
                TextFormat.FG_RED,
                TextFormat.BOLD
            )
        )
        return
    
    try:
        directory = args[1]
    except IndexError:
        directory = "."

    if os.path.isfile(filename):
        print(
            format_text(
                f"File already exists: {filename}",
                TextFormat.FG_RED,
                TextFormat.BOLD
            )
        )
        return
    
    with open(f"{directory}\\{filename}", "x"): pass
    
@command(
    name="directory", 
    aliases=[
        "mkdir", 
        "dtouch", 
        "ftouch"
    ]
)
@newline_output
def create_directory(*args):
    try:
        dirname = args[0]
    except IndexError:
        print(
            format_text(
                "Please provide a dirname",
                TextFormat.FG_RED,
                TextFormat.BOLD
            )
        )
        return
    
    try:
        path = args[1]
    except IndexError:
        path = "."

    if os.path.isdir(dirname):
        print(
            format_text(
                f"Directory already exists: {dirname}",
                TextFormat.FG_RED,
                TextFormat.BOLD
            )
        )
        return
    
    os.mkdir(f"{path}\\{dirname}")
        
@command(
    name = "pwd", 
    aliases = [
        "curdir", 
        "get_dir"
    ]
)
@newline_output
def print_working_directory():
    print(format_text(
        os.getcwd(),
        TextFormat.FG_GREEN
    ))

@command(
    name = "pathh", 
    aliases = [
        "get_path_history", 
        "pathhistory", 
        "pht"
    ]
)
@newline_output
def get_path_history():
    print(format_text(
        PATH_HISTORY,
        TextFormat.FG_GREEN
    ))

@command(
    name = "cat",
    aliases = [
        "get-content",
        "contentof"
    ]
)
@newline_output
def get_content(*args):
    if not len(args) == 1:
        print(format_text(
            "Invalid args, please specify a path to a file",
            TextFormat.FG_RED
        ))
        return
    
    if not os.path.isfile(args[0]):
        print(format_text(
            "First argument must point to a valid file",
            TextFormat.FG_RED
        ))
        return

    with open(args[0], "r") as file:
        print(format_text(
            file.read(),
            TextFormat.FG_GREEN
        ))

@command(
    name = "load",
    aliases = [
        "declare_external",
        "tsloadexternalcommand"
    ]
)
@newline_output
@with_manager_handle
def tsLoadCommand(manager: CommandManager, command_file: str):
    # Locate the external file
    if not os.path.isfile(command_file) and \
        command_file.endswith(".py") and \
        os.path.basename(command_file) not in FBLACKLIST:
        print(
            format_text(
                f"Failed to resolve file {command_file} or file in blacklist",
                TextFormat.FG_RED,
                TextFormat.BOLD
            )
        )
        return

    try:
        # Now we have a tangible file, try and import it
        # dynamically to get a module to work with
        spec = importlib.util.spec_from_file_location(
            "dyn_newmodule",
            command_file
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except Exception as e:
        print(
            format_text(
                f"Failed to import new module: {e}",
                TextFormat.FG_RED,
                TextFormat.BOLD
            )
        )
        return
    
    # Now we will have the 'module' module to look into,
    # just replicating the loading done in main
    class_members = [getattr(module, name) for name in dir(module) if callable(getattr(module, name))]

    try:
        for func in class_members:
            if not isinstance(func, type(lambda: None)):
                continue

            if hasattr(func, "__wrapped__"):
                wrapped_func = func.__wrapped__  # Get the original function
            else:
                continue
            
            if not hasattr(wrapped_func, "notcommand"):
                if hasattr(wrapped_func, "name"):
                    name = wrapped_func.name
                else:
                    name = wrapped_func.__name__
                if hasattr(wrapped_func, "aliases"):
                    aliases = wrapped_func.aliases
                else:
                    continue

                # Big issue with multiple namespace loading:
                # If it is loaded multiple times, it will
                # only run the first loaded function, so
                # we need to make sure that this doesn't
                # occur or we will have functions not changing
                if not name in EXTERNAL_COMMANDS:
                    EXTERNAL_COMMANDS.append(name)

                    print(
                        format_text(
                            f"Loaded command: {name}",
                            TextFormat.FG_GREEN,
                            TextFormat.BOLD
                        )
                    )

                    manager.register_command(
                        name,
                        wrapped_func,
                        aliases
                    )
                else:
                    print(
                        format_text(
                            f"Cannot load command {name}: item already imported in namespace",
                            TextFormat.FG_RED,
                            TextFormat.BOLD
                        )
                    )
    except Exception as e:
        print(
            format_text(
                f"Failed to import new module: {e}",
                TextFormat.FG_RED,
                TextFormat.BOLD
            )
        )
        return

@command(
    name = "unload",
    aliases = [
        "unload_module",
        "unload_command"
    ]
)
@newline_output
@with_manager_handle
def tsUnloadCommand(manager: CommandManager, command_name: str):
    if manager.is_command(command_name):
        manager.deregister_command(command_name)
        if command_name in EXTERNAL_COMMANDS:
            EXTERNAL_COMMANDS.remove(command_name)
    else:
        print(
            format_text(
                "The command specifed is not loaded. NOTE: Provide the command and not an alias.",
                TextFormat.FG_RED,
                TextFormat.BOLD
            )
        )

@command(
    name = "policyview",
    aliases = [
        "policy",
        "tsPolicy",
        "tsPolicyView"
    ]
)
def policyview():
    config = Config()

    if bool(config.seek('PolicyView')['allow_policy_view']):
        print(TextFormat.FG_GREEN)
        print_config_keys(config._parsed_copy)
        print(TextFormat.RESET)

@exclude
def print_config_keys(config, indent=""):
    for key, value in config.items():
        if isinstance(value, dict):
            print(f"\n{indent}{repr(key)} ->")
            print_config_keys(value, indent + "\t")
        else:
            print(f"{indent}{repr(key)} -> {repr(value)}")


