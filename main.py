import _commands
import Commands
import TPC
import os
import prettytable
import ctypes

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

class SignalReloadError(Exception):
    """
    Signals for a reload
    """
    pass

def invalid_command(name, args):
    config = TPC.Config()

    if bool(config.seek('InvalidCommand')['os_exec_invalid_commands']):
        os.system(name + " " + " ".join(args))
        return

    pbuilder = TPC.PromptBuilder()

    pbuilder.add(
        config.seek('InvalidCommand')['invalid_command_message'].replace('<name>', name).replace('<args>', ", ".join(args)),
        config.seek('InvalidCommand')['invalid_command_message_color'],
        *config.seek('InvalidCommand')['invalid_command_message_modifiers']
    )

    print("\n" + pbuilder.fetch().strip() + "\n")

def create_prompt() -> TPC.PromptBuilder:
    """
    Returns a TPC.PromptBuilder with the prompt loaded
    from config. To get the prompt as a string, use
    PromptBuilder.fetch()
    """
    
    cfg = TPC.Config()
    cfg.data = cfg.data[0]

    prompt_builder = TPC.PromptBuilder()
    prompt_builder.add(
        cfg.data["Prompt"]["name"],
        cfg.data["Prompt"]["name_color"],
        *cfg.data["Prompt"]["name_modifiers"]
    )
    prompt_builder.add(
        cfg.data["Prompt"]["version"],
        cfg.data["Prompt"]["version_color"],
        *cfg.data["Prompt"]["version_modifiers"]
    )
    prompt_builder.add(
        cfg.data["Prompt"]["pointer"],
        cfg.data["Prompt"]["pointer_color"],
        *cfg.data["Prompt"]["pointer_modifiers"]
    )

    dir = os.getcwd()

    filepath_format = cfg.data["Prompt"]["filepath_format"]
    if filepath_format == "mini":
        dir = dir.split("\\")[-1]
    elif filepath_format == "short":
        dir = "\\".join(dir.split("\\")[-2:])
    elif filepath_format == "long":
        pass

    prompt_builder.add(
        dir,
        cfg.data["Prompt"]["filepath_color"],
        *cfg.data["Prompt"]["filepath_modifiers"]
    )

    if cfg.data["Prompt"]["use_admin_symbol"]:
        if is_admin():
            prompt_builder.add(
                cfg.data["Prompt"]["admin_symbol"],
                cfg.data["Prompt"]["admin_symbol_color"],
                *cfg.data["Prompt"]["admin_symbol_modifiers"]
            )

    prompt_builder.add(
        cfg.data["Prompt"]["end"],
        cfg.data["Prompt"]["end_color"],
        *cfg.data["Prompt"]["end_modifiers"]
    )

    return prompt_builder

def main():
    tsStartup = TPC.Config().seek('Startup')['startup_directory'].replace('<HOME>', os.path.expanduser("~"))
    Commands.defaults.goto(
        tsStartup if os.path.isdir(tsStartup) else os.path.expanduser("~")
    )
    
    prompt_builder = create_prompt()
    reader = TPC.StdReader(prompt_builder.fetch(
        TPC.Config().data[0]["Prompt"]["seperator"]
    ))
    processor = TPC.StdProcessor({}, TPC.Config())

    debugmode = bool(TPC.Config().seek('Startup')['debug_mode'])
    manager = TPC.CommandManager(
        reader=reader,
        processor=processor,
        invalid_command=invalid_command,
        is_debug_mode=debugmode
    )

    class_members = [getattr(Commands, name) for name in dir(Commands) if callable(getattr(Commands, name))]

    for func in class_members:
        if hasattr(func, "__wrapped__"):
            wrapped_func = func.__wrapped__  # Get the original function
        else:
            wrapped_func = func
        
        # No more importing random ahh things
        if not isinstance(func, type(lambda: None)):
            continue

        if not hasattr(wrapped_func, "notcommand"):
            if hasattr(wrapped_func, "name"):
                name = wrapped_func.name
            else:
                continue
            if hasattr(wrapped_func, "aliases"):
                aliases = wrapped_func.aliases
            else:
                continue
            
            # Prevents reloading defaults again
            Commands.defaults.EXTERNAL_COMMANDS.append(name)

            manager.register_command(
                name,
                wrapped_func,
                aliases
            )

    manager.register_command(
        "exit",
        exit,
        ["quit", "leave"]
    )

    @_commands.newline_output
    def commands():
        table = prettytable.PrettyTable()
        table.field_names = [
            "Name",
            "Aliases"
        ]
        rows = []
        for command in manager.registered:
            current_row = []
            current_row.append(str(command["name"]))
            current_row.append(", ".join(command["aliases"]))
            rows.append(current_row)

        table.add_rows(rows)

        color = TPC.formatting.color_from_str(
            TPC.Config().seek('Getcmd')['table_color']
        )

        print(TPC.format_text(
            table,
            color,
            TPC.TextFormat.BOLD
        ))

    def reload():
        raise SignalReloadError

    manager.register_command(
        "commands",
        commands,
        ["getcmd"]
    )
   
    manager.register_command(
        "exit-d",
        reload,
        ["debug_exit", "force_exit", "dexit", "dxit"]
    )

    _commands.GLOBAL_COMMAND_MANAGER_HNDL = manager

    do_startup_clear = bool(TPC.Config().seek("Startup")["clear_screen_on_startup"])

    if do_startup_clear:
        os.system("cls")

    if bool(TPC.Config().seek('Startup')['do_init_code_inject']):
        try:
            exec(TPC.Config().seek('Startup')['init_code'])
        except Exception as E:
            print(TPC.format_text(
                f"The init code raised an error: {E}",
                TPC.TextFormat.FG_RED
            ))

    while True:
        try:
            manager.execute_one()
        except KeyboardInterrupt:
            break
        
        # Refreshes the prompt
        prompt_builder = create_prompt()
        manager.reader.prompt = prompt_builder.fetch(
            TPC.Config().seek('Prompt')['seperator']
        )

if __name__ == "__main__":
    main()
        
