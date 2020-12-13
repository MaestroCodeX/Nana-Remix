from os import environ
from configparser import ConfigParser

config = ConfigParser()
config.read("config.ini")


def get_var(name, default=None):
    ENV = bool(environ.get("ENV", False))
    if ENV:
        return environ.get(name, default)

    try:
        return config.get("nana", name)
    except AttributeError:
        return None
