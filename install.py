import os

pythonpath = os.getenv("PYTHONPATH")
pythonpath = pythonpath.split(";")

if not pythonpath or pythonpath == None:
    print("Failed to retrieve PYTHONPATH, please check python is corectly installed and configured on your system")
    exit()

TPC_path = os.path.abspath("TPC")
COMMANDS_path = os.path.abspath("Commands")

if TPC_path in pythonpath and COMMANDS_path in pythonpath:
    print("Cannot complete setup twice: PATH already contains modules")
    exit()

new_pythonpath = pythonpath.append(TPC_path).append(COMMANDS_path)
new_pythonpath = ";".join(new_pythonpath)

os.system(f"set PYTHONPATH='{new_pythonpath}'")


