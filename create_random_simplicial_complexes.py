import os
from argparse import ArgumentParser

from contagion.SimplicialComplex import SimplicialComplex, from_random
from contagion.utils import (get_iacopini_cliques,
                             get_random_simplicial_complexes,
                             get_simplicialbros_datasets, sc_from_dataset)
from directories import ramdom_simplicialcomplex_dir
from logger import logger

# setups = [
#     {
#         "N": 500,
#         "k": 20,
#         "k_delta": 6
#     }
# ]


def write_to_file(simplicial_complex: SimplicialComplex):
    filepath = os.path.join(ramdom_simplicialcomplex_dir,
                            f'N{len(simplicial_complex.nodes)}_k{simplicial_complex.k:.3f}_kdelta{simplicial_complex.k_delta:.3f}.pickle')
    logger.info('Random simplicial complex with N=%d, k=%.3f, k_delta=%.3f written to:\n\t%s',
                simplicial_complex.N, simplicial_complex.k, simplicial_complex.k_delta, simplicial_complex.to_pickle_file(filepath))


if __name__ == "__main__":
    # execute only if run as a script

    parser: ArgumentParser = ArgumentParser(
        description='Create a random simplicial complex with provided N, k and k_delta, or from a real simplicial complex')

    group1 = parser.add_argument_group('from parameters')
    group1.add_argument("-N", "--nodes", help="the amount of nodes", type=int)
    group1.add_argument("-k", "--k", help="the order k", type=float)
    group1.add_argument("-kd", "--k_delta",
                        help="the order k_delta", type=float)

    group2 = parser.add_argument_group('from existing dataset')
    group2.add_argument("-fd",
                        '--fromdataset',
                        help='build a random simplicial complex with the same amount of nodes, and orders k and k_delta as the provided datasets')
    group2.add_argument("-l",
                        "--listdatasets",
                        help="do nothing but get the list available simplicial datasets/random-simplicial-complexes to load from db",
                        action="store_true")

    args = parser.parse_args()

    simplicialbros_datasets = get_simplicialbros_datasets()
    random_simplicial_complexes = get_random_simplicial_complexes()
    iacopini_simplicial_complexes = get_iacopini_cliques()

    if args.listdatasets:
        print('Simplicial Bros datasets:\n' +
              ','.join(simplicialbros_datasets))
        print()
        print('Generated random simplicial complexes:\n' +
              ','.join(random_simplicial_complexes))
        print()
        print('Iacopini et al json cliques:\n' +
              ','.join(iacopini_simplicial_complexes))

    elif args.fromdataset:
        sc = sc_from_dataset(dataset=args.fromdataset)
        write_to_file(sc)

    elif args.nodes:
        if not args.k or not args.k_delta:
            parser.error('N, k and k_delta MUST be provided')
        sc = from_random(args.nodes, args.k, args.k_delta)
        write_to_file(sc)

    else:
        parser.print_help()
