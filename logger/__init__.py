import logging
import os

from configparser import ConfigParser

config = ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), '../config.ini'))

logger = logging.getLogger()
logger.setLevel(config['Logger']['loglevel'])
formatter = logging.Formatter('%(levelname)s: %(asctime)s - %(message)s', datefmt='%H:%M:%S')
sh = logging.StreamHandler()
sh.setFormatter(formatter)
sh.setLevel(config['Logger']['loglevel'])
logger.addHandler(sh)
