import os

from contagion import SimplicialComplex
from directories import ramdom_simplicialcomplex_dir
from logger import logger
from argparse import ArgumentParser

setups = [
    {
        "N": 500,
        "k": 20,
        "k_delta": 6
    }
]


for setup in setups:
    sc = SimplicialComplex.from_random(
        setup['N'], float(setup['k']), float(setup['k_delta']))
    filepath = os.path.join(ramdom_simplicialcomplex_dir,
                            f'N{len(sc.nodes)}_k{sc.k}_kdelta{sc.k_delta}.pickle')
    logger.info('Random simplicial complex with N=%s, k=%s, k_delta=%s written to:\n\t%s', setup['N'], setup['k'], setup['k_delta'], sc.to_pickle_file(filepath))


