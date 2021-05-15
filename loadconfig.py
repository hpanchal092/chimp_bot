import json

CONFIG_FILE = "config.json"

def read(cog):
    with open(CONFIG_FILE) as config_file:
        loaded_file = json.load(config_file)
    return loaded_file[cog]

