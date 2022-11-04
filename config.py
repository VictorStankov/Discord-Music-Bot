from configparser import ConfigParser

cfg = ConfigParser()
cfg.read("config.cfg")

token = cfg["Credentials"]["Token"]
