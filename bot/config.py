import json
from configparser import ConfigParser
import os
from typing import Dict

cfg = ConfigParser()
cfg.read('config.cfg')

token = cfg['Information']['Token']
operating_system = cfg['Information']['Operating_System'].lower()

if operating_system == 'windows':
    ffmpeg_location = os.curdir + "\\ffmpeg\\bin\\ffmpeg.exe"
elif operating_system == 'linux':
    ffmpeg_location = '/usr/bin/ffmpeg'
else:
    ffmpeg_location = None

del operating_system

logging_level = cfg['Information']['logging_level'].upper()
bot_description = cfg['Information']['description']

with open("misc/command_descriptions.json") as desc:
    command_descriptions: Dict[str, str] = json.loads(desc.read())

del cfg
