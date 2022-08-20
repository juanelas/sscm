import os
from configparser import ConfigParser

config = ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), '../config.ini'))

os.umask(0o000)

_figurespath = os.path.expanduser(config['Analysis']['figuresdir'])
if not os.path.exists(_figurespath):
    os.makedirs(_figurespath)
figures_dir = os.path.join(_figurespath, config['SimplicialDB']['dbname'])
if not os.path.exists(figures_dir):
    os.makedirs(figures_dir)

_statspath = os.path.expanduser(config['Analysis']['statsdir'])
if not os.path.exists(_statspath):
    os.makedirs(_statspath)
stats_dir = os.path.join(_statspath, config['SimplicialDB']['dbname'])
if not os.path.exists(stats_dir):
    os.makedirs(stats_dir)

_dbsimplicialcomplexpath = os.path.expanduser(config['Contagion']['db_simplicial_complex_csvs'])
if not os.path.exists(_dbsimplicialcomplexpath):
    os.makedirs(_dbsimplicialcomplexpath)
db_simplicialcomplex_dir = os.path.join(_dbsimplicialcomplexpath, config['SimplicialDB']['dbname'])
if not os.path.exists(db_simplicialcomplex_dir):
    os.makedirs(db_simplicialcomplex_dir)

ramdom_simplicialcomplex_dir = os.path.expanduser(config['Contagion']['random_simplicial_complex_dir'])
if not os.path.exists(ramdom_simplicialcomplex_dir):
    os.makedirs(ramdom_simplicialcomplex_dir)

contagion_results_dir = os.path.expanduser(config['Contagion']['contagion_results_dir'])
if not os.path.exists(contagion_results_dir):
    os.makedirs(contagion_results_dir)

contagion_figures_dir = os.path.expanduser(config['Contagion']['contagion_figures_dir'])
if not os.path.exists(contagion_figures_dir):
    os.makedirs(contagion_figures_dir)

iacopini_json_cliques = os.path.expanduser(config['Iacopini']['json_cliques_dir'])

sc_degrees_figures_dir = os.path.join(_figurespath, 'sc_degrees')
if not os.path.exists(sc_degrees_figures_dir):
    os.makedirs(sc_degrees_figures_dir)
