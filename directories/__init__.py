import os
from configparser import ConfigParser

config = ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), '../config.ini'))

os.umask(0o000)

_figurespath = config['Analysis']['figuresdir']
if not os.path.exists(_figurespath):
    os.makedirs(_figurespath)
figures_dir = os.path.join(_figurespath, config['SimplicialDB']['dbname'])
if not os.path.exists(figures_dir):
    os.makedirs(figures_dir)

_statspath = config['Analysis']['statsdir']
if not os.path.exists(_statspath):
    os.makedirs(_statspath)
stats_dir = os.path.join(_statspath, config['SimplicialDB']['dbname'])
if not os.path.exists(stats_dir):
    os.makedirs(stats_dir)
