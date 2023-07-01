import os
import toml

current_directory = os.getcwd()
DEFAULT_CONFIG_PATH = f"{current_directory}\\config.toml"

class InvalidConfigError(Exception):
    """
    The config file is invalid
    """
    pass

class CircularExternalConfigError(Exception):
    """
    Two or more config files each have EXTERNAL config settings
    and point to each other
    """
    pass

def config_check(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError or toml.TomlDecodeError:
            InvalidConfigError("Invalid config file")

    return wrapper

class Config:
    def __init__(self):
        self._stepped_files = []
        try:
            self.options = self.parse()
        except InvalidConfigError:
            print("Failed to start correct config")

    def reload(self):
        self.parse()

    def seek(self, search_key):
        """
        Returns the requested key data from the data
        """
        for dictionary in self.data:
            if search_key in dictionary:
                return dictionary[search_key]
        
        raise IndexError('Bad seek')

    @config_check
    def parse(self, cfg_path: str = DEFAULT_CONFIG_PATH):
        os.chdir("..")

        # First, we check if the cfg_path is valid
        if not os.path.isfile(cfg_path):
            raise FileNotFoundError("The default config path is invalid")
    
        # Now, we make sure it is readable and then get a raw copy
        with open(cfg_path, "r") as cfg_file:
            if not cfg_file.readable:
                raise OSError("The default config file is not readable")
        
            self._raw_copy = cfg_file.read()

        # Replace <HOME> with the expanded home directory path
        self._raw_copy = self._raw_copy.replace("<HOME>", os.path.expanduser("~").replace("\\", "\\\\"))

        # Now, use TOML to parse it
        self._parsed_copy = toml.loads(self._raw_copy)

        # Next, check for [Meta]CfgStorage being EXTERNAL
        if self._parsed_copy["Meta"]["CfgStorage"] == "EXTERNAL":
            if self._parsed_copy["Meta"]["CfgLocation"] in self._stepped_files:
                raise CircularExternalConfigError("Circular config")
            else:
                self._stepped_files.append(cfg_path)
                self.parse(self._parsed_copy["Meta"]["CfgLocation"])

        self.data = []

        for item in self._parsed_copy.keys():
            if not item == "Meta":
                self.data.append({item: self._parsed_copy[item]})
        
        return self.data

#class DictExpantion:
#    def __init__(self, dicts: dict[dict]):
#        self.flattened: dict = {}
#        self.flatten(dicts)
#
#    def flatten(self, dicts: dict):
#        for key, value in dicts.items():
#            if isinstance(value, dict):
#                self.flatten(value)
#            else:
#                self.flattened[key] = value