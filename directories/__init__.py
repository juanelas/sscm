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

_simplicialcomplexpath = config['Contagion']['simplicial_complex_csvs']
if not os.path.exists(_simplicialcomplexpath):
    os.makedirs(_simplicialcomplexpath)
simplicialcomplex_dir = os.path.join(_simplicialcomplexpath, config['SimplicialDB']['dbname'])
if not os.path.exists(simplicialcomplex_dir):
    os.makedirs(simplicialcomplex_dir)

_contagion_results_path = config['Contagion']['contagion_results_dir']
if not os.path.exists(_contagion_results_path):
    os.makedirs(_contagion_results_path)
contagion_results_dir = os.path.join(_contagion_results_path, config['SimplicialDB']['dbname'])
if not os.path.exists(contagion_results_dir):
    os.makedirs(contagion_results_dir)

_contagion_figures_path = config['Contagion']['contagion_figures_dir']
if not os.path.exists(_contagion_figures_path):
    os.makedirs(_contagion_figures_path)
contagion_figures_dir = os.path.join(_contagion_figures_path, config['SimplicialDB']['dbname'])
if not os.path.exists(contagion_figures_dir):
    os.makedirs(contagion_figures_dir)