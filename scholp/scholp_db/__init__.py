import os
import sys
from configparser import ConfigParser

sys.path.append('../')
from database.database import Database

config = ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), '../config.ini'))

scholp_db = Database(config['Database'])
