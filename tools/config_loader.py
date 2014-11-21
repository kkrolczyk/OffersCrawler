try:
    import configparser
except ImportError:
    import ConfigParser as configparser

class MyConfig(object):

    def __new__(cls, config_file, allow_no_value=False):

        config = configparser.ConfigParser(allow_no_value=allow_no_value)
        config.read(config_file)
        return [dict(config.items(sect)) for sect in config.sections()]
        # try catch anything ?