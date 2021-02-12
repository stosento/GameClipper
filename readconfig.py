import configparser
import collections

config_path = 'config.cfg'

# Methods needed
# 1. Read in configs into multi-section dict
# 2. Ability to write to the config file

# Get the config -- ASSUMPTION - file exists
def get_config():
    config = configparser.RawConfigParser()
    config.read(config_path)

    return config

# Get the config dict for multiple layers
def get_config_section():
    config = get_config()
    config.section_dict = collections.defaultdict()
    for section in config.sections():
        config.section_dict[section] = dict(config.items(section))
    return config.section_dict

def write_config(section, values):
    config = get_config()

    config[section] = values

    with open(config_path, 'w') as conf:
        config.write(conf)

    return config
