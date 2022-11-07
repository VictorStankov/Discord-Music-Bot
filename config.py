from configparser import ConfigParser
import os

cfg = ConfigParser()
cfg.read('config.cfg')

token = cfg['Information']['Token']
operating_system = cfg['Information']['Operating_System'].lower()

token = cfg["Credentials"]["Token"]
