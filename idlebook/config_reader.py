''' 
Helper for getting a dict of config variables for a given section (aka config category)
'''
import os
import ConfigParser

config_location = os.getenv('IB_CONFIG')
CONFIG = ConfigParser.ConfigParser()
CONFIG.read(config_location)

def get_config(section):
    env_vars = {}
    options = CONFIG.options(section)
    for option in options:
        try:
            value = CONFIG.getboolean(section, option)
        except ValueError:
            try:
                value = CONFIG.getfloat(section, option)
                if value % 1 == 0.0:
                    value = int(value)
            except ValueError:
                try:
                    value = CONFIG.get(section, option)
                except:
                    print("can't get value for %s" % value)
                    value = None
            
        env_vars[option] = value
    return env_vars

