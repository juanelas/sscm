import os
import pickle
import sys
from argparse import ArgumentParser
from multiprocessing import Pool
from operator import itemgetter
from typing import List

import numpy as np
from tqdm import tqdm

from contagion.run_simulation import run_simulation
from contagion.SimplicialComplex import (SimplicialComplex,
                                         from_iacopini_cliques,
                                         from_random_sc_file,
                                         from_simplicial_csvs)
from contagion.utils import (get_iacopini_cliques,
                             get_random_simplicial_complexes,
                             get_simplicialbros_datasets, parse_results)
from directories import config, contagion_results_dir
from logger import logger

# Simulation Parameters
MAX_TIMESTEPS = 2000
ITERATIONS = 100
PROCESSES = 6

simulations_parameters = [
    # {
    #     # Infection parameters. For the slices with different values of lambda
    #     "mu": 0.05,
    #     # from 0.2 to 3.0 every 0.2. I use 3.1 because final value is not included
    #     "lambdas": np.arange(0.2, 3.1, .3),
    #     "rho0s_per_lambda_delta": {
    #         0: [.01],
    #         0.8: [.01],
    #         2.5: [.01, .4]
    #     },
    #     # the rhos to simulate for specific lambda and lambda_delta
    #     "rhos_over_time": {
    #         "rho_0s": np.arange(.005, 1, .1),
    #         "lambda": None,  # If not set is automatically chosen
    #         "lambda_delta": None  # If not set is automatically chosen
    #     }
    # },
    # {  # Experiment 1
    #     "tag": "ex1",
    #     "mu": 0.5,
    #     "betas": np.array([.01]),
    #     "rho0s_per_beta_delta": {
    #         0.03333333333333333: [.2, .8]
    #     },
    #     "sigma": 0.003322259136212625,
    #     "sigma_delta": 0.01107419712070875
    # },
    # {  # Experiment 1 no stochastic
    #     "tag": "ex1_sigma0",
    #     "mu": 0.5,
    #     "betas": np.array([.01]),
    #     "rho0s_per_beta_delta": {
    #         0.03333333333333333: [.2, .8]
    #     }
    # },
    # {  # Experiment 2
    #     "tag": "ex2",
    #     "mu": 0.970873786407767,
    #     "betas": np.array([0.05]),
    #     "rho0s_per_beta_delta": {
    #         0.16666666666666666: [.2, .8]
    #     },
    #     "sigma": 0.023809523809523808,
    #     "sigma_delta": 0.07936507936507936
    # },
    # {  # Experiment 2 no stochastic
    #     "tag": "ex2_sigma0",
    #     "mu": 0.970873786407767,
    #     "betas": np.array([0.05]),
    #     "rho0s_per_beta_delta": {
    #         0.16666666666666666: [.2, .8]
    #     }
    # },
    # {  # Experiment 3
    #     "tag": "ex3",
    #     "mu": 0.5,
    #     "betas": np.array([.03]),
    #     "rho0s_per_beta_delta": {
    #         0.09999999999999999: [.2, .8]
    #     },
    #     "sigma": 0.009966777408637875,
    #     "sigma_delta": 0.03322259136212625
    # },
    # {  # Experiment 3 no stochastic
    #     "tag": "ex3_sigma0",
    #     "mu": 0.5,
    #     "betas": np.array([.03]),
    #     "rho0s_per_beta_delta": {
    #         0.09999999999999999: [.2, .8]
    #     }
    # }
    {  # Experiment 1 paper
        "tag": "ex1",
        "mu": 0.7,
        "betas": np.array([0.025]),
        "rho0s_per_beta_delta": {
            0.041666666666666664: [.2, .8]
        },
        "timesteps": 2000,
        "sigma": 0.017499999999999998,
        "sigma_delta": 0.041666666666666664,
        "bounded_beta": False,
        "independent_noises": False
    },
    {  # Experiment 1 paper no stochastic
        "tag": "ex1_sigma0",
        "mu": 0.7,
        "betas": np.array([0.025]),
        "rho0s_per_beta_delta": {
            0.041666666666666664: [.2, .8]
        },
        "timesteps": 2000
    },
    {  # Experiment 2 paper
        "tag": "ex2",
        "mu": 0.5,
        "betas": np.array([0.03]),
        "rho0s_per_beta_delta": {
            0.09999999999999999: [.2, .8]
        },
        "timesteps": 30000,
        "sigma": 0.034999999999999996,
        "sigma_delta": 0.11666666666666665,
        "bounded_beta": False,
        "independent_noises": False
    },
    {  # Experiment 2 paper no stochastic
        "tag": "ex2_sigma0",
        "mu": 0.5,
        "betas": np.array([0.03]),
        "rho0s_per_beta_delta": {
            0.09999999999999999: [.2, .8]
        },
        "timesteps": 30000
    },
    {  # Experiment 3 paper
        "tag": "ex3",
        "mu": 0.7,
        "betas": np.array([.04]),
        "rho0s_per_beta_delta": {
            0.13333333333333333: [.2, .8]
        },
        "timesteps": 2000,
        "sigma": 0.01,
        "sigma_delta": 0.03333333333333333,
        "bounded_beta": False,
        "independent_noises": False
    },
    {  # Experiment 3 no paper stochastic
        "tag": "ex3_sigma0",
        "mu": 0.7,
        "betas": np.array([.04]),
        "rho0s_per_beta_delta": {
            0.13333333333333333: [.2, .8]
        },
        "timesteps": 2000,
    },
    {  # Juan's ex1
        "tag": "ex1b",
        "mu": 0.7,
        "betas": np.array([0.013999999999999999]),
        "rho0s_per_beta_delta": {
            0.02: [.2, .8]
        },
        "timesteps": 2000,
        "sigma": 0.01870828693386971,
        "sigma_delta": 0.009354143466934854,
        "bounded_beta": False,
        "independent_noises": False
    },
    {  # Juan's ex1
        "tag": "ex1b_sigma0",
        "mu": 0.7,
        "betas": np.array([0.013999999999999999]),
        "rho0s_per_beta_delta": {
            0.02: [.2, .8]
        },
        "timesteps": 2000
    },
    {  # Juan's ex2
        "tag": "ex2b",
        "mu": 0.5,
        "betas": np.array([0.03]),
        "rho0s_per_beta_delta": {
            0.02: [.2, .8]
        },
        "timesteps": 20000,
        "sigma": 0.035355339059327376,
        "sigma_delta": 0.017677669529663688,
        "bounded_beta": False,
        "independent_noises": False
    },
    {  # Juan's ex2
        "tag": "ex2b_sigma0",
        "mu": 0.5,
        "betas": np.array([0.03]),
        "rho0s_per_beta_delta": {
            0.02: [.2, .8]
        },
        "timesteps": 20000
    },
    {  # Juan's ex3
        "tag": "ex3b",
        "mu": 0.5,
        "betas": np.array([0.0375]),
        "rho0s_per_beta_delta": {
            0.08: [.2, .8]
        },
        "timesteps": 2000,
        "sigma": 0.02738612787525831,
        "sigma_delta": 0.013693063937629155,
        "bounded_beta": False,
        "independent_noises": False
    },
    {  # Juan's ex3
        "tag": "ex3b_sigma0",
        "mu": 0.5,
        "betas": np.array([0.0375]),
        "rho0s_per_beta_delta": {
            0.08: [.2, .8]
        },
        "timesteps": 2000
    },
    {  # Juan's ex2 InVS15
        "tag": "ex2c",
        "mu": 0.6,
        "betas": np.array([0.03193514708591783]),
        "rho0s_per_beta_delta": {
            0.02: [.2, .8]
        },
        "timesteps": 2000,
        "sigma": 0.03474086009637279,
        "sigma_delta": 0.017370430048186395,
        "bounded_beta": False,
        "independent_noises": False
    },
    {  # Juan's ex2 InVS15
        "tag": "ex2c_sigma0",
        "mu": 0.6,
        "betas": np.array([0.03193514708591783]),
        "rho0s_per_beta_delta": {
            0.02: [.2, .8]
        },
        "timesteps": 2000
    },
]


def select_parameters_for_rhos_over_time(stationary_rhos, lambda_delta=None):
    lambda_delta = np.max(list(stationary_rhos.keys())
                          ) if lambda_delta is None else lambda_delta
    rho_0_min = np.min(list(stationary_rhos[lambda_delta].keys()))
    rho_0_max = np.max(list(stationary_rhos[lambda_delta].keys()))
    lambdas = list(stationary_rhos[lambda_delta][rho_0_min].keys())

    avg_stationary_rhos_with_rho_0_min = np.mean(np.array(
        [stationary_rhos[lambda_delta][rho_0_min][lambda1] for lambda1 in lambdas]), axis=1)
    avg_stationary_rhos_with_rho_0_max = np.mean(np.array(
        [stationary_rhos[lambda_delta][rho_0_max][lambda1] for lambda1 in lambdas]), axis=1)
    difference = avg_stationary_rhos_with_rho_0_max - \
        avg_stationary_rhos_with_rho_0_min

    return lambdas[np.argmax(difference)], lambda_delta


def simulation(label: str, simplicial_complex, simulation_parameters, max_timesteps: int, iterations: int, processes: int):

    tag, mu = itemgetter('tag', 'mu')(simulation_parameters)

    sigma = simulation_parameters.get('sigma')
    sigma_delta = simulation_parameters.get('sigma_delta')

    bounded_beta = simulation_parameters.get('bounded_beta')
    independent_noises = simulation_parameters.get('independent_noises')

    timesteps = max_timesteps if max_timesteps else simulation_parameters.get(
        'timesteps')
    if not timesteps:
        timesteps = MAX_TIMESTEPS

    if 'lambdas' in simulation_parameters:
        lambdas = simulation_parameters['lambdas']
        if 'betas' in simulation_parameters or 'rho0s_per_beta_delta' in simulation_parameters:
            raise Exception(
                'Simulation parameters MUST depend either on betas or lambdas, but not both')
        if 'rho0s_per_lambda_delta' not in simulation_parameters:
            raise Exception(
                'rhos_per_lambda_delta is required if lambdas is provided')
        rho0s_per_lambda_delta = simulation_parameters['rho0s_per_lambda_delta']

    elif 'betas' in simulation_parameters:
        betas = simulation_parameters['betas']
        if 'rho0s_per_lambda_delta' in simulation_parameters:
            raise Exception(
                'Simulation parameters MUST depend either on betas or lambdas, but not both')
        if 'rho0s_per_beta_delta' not in simulation_parameters:
            raise Exception(
                'rhos_per_beta_delta is required if betas is provided')
        rho0s_per_beta_delta = simulation_parameters['rho0s_per_beta_delta']
        lambdas = 1.*(simplicial_complex.k/mu) * np.array(betas)
        rho0s_per_lambda_delta = {}
        for key, val in rho0s_per_beta_delta.items():
            rho0s_per_lambda_delta[float(
                key) * simplicial_complex.k / mu] = val

    else:
        raise Exception('Either lambdas or betas MUST be provided')

    # lambdas_str = f'[{lambdas[0]:.2f}]' if lambdas[0] == lambdas[-1] else f'[{lambdas[0]:.2f}..{lambdas[-1]:.2f}]'
    lambdas_str_arr = [f'{lambda1:.2f}' for lambda1 in lambdas]
    lambdas_str = '[' + ','.join(lambdas_str_arr) + ']'

    # Preparing arguments for the parallel processing
    arguments = []

    # rho0s_str = f'[{rho0s[0]:.2f}]' if rho0s[0] == rho0s[-1] else f'[{rho0s[0]:.2f}..{rho0s[-1]:.2f}]'
    rho0s_per_lambda_delta_str_list = []
    for lambda_delta, rho0s in rho0s_per_lambda_delta.items():
        rho0s_str = ','.join([f'{rho0:.2f}' for rho0 in rho0s])
        rho0s_per_lambda_delta_str_list.append(
            f'{lambda_delta:.2f}->[{rho0s_str}]')
    rho0s_per_lambda_delta_str = ','.join(
        rho0s_per_lambda_delta_str_list)

    for iteration in range(iterations):
        description = f'[{label} - {tag}] lambdas={lambdas_str}, sigma={sigma}, sigma_delta={sigma_delta}, mu={mu}, rho0s_per_lambda_delta={rho0s_per_lambda_delta_str}: it{iteration + 1}/{iterations}'
        arguments.append([f'{description}', simplicial_complex,
                          lambdas, sigma, sigma_delta, mu, rho0s_per_lambda_delta, timesteps, bounded_beta, independent_noises])

    # Multiprocessing
    results = []
    with Pool(processes=processes) as pool:
        logger.info(
            f'[{label}]: Starting {iterations} iterations for mu={mu}, lambdas={lambdas_str}, sigma={sigma}, sigma_delta={sigma_delta}, rho0s_per_lambda_delta={rho0s_per_lambda_delta_str}')
        for result in tqdm(pool.imap_unordered(func=run_simulation, iterable=arguments), total=len(arguments), ncols=80):
            results.append(result)

    if len(results) == 0:
        raise Exception(
            f'NO RESULTS!!! {label}, mu={mu}, rho0s_per_lambda_delta={rho0s_per_lambda_delta_str}')

    # Let us parse the results so we group iterations inside rhos, stationary_rhos, etc.
    return parse_results(results)


def save_to_file(dirname: str, filename: str, extension: str, contents: str, overwrite: bool = False):
    if not os.path.exists(dirname):
        os.makedirs(dirname)

    filepath = os.path.join(dirname, f'{filename}.{extension}')

    if not overwrite:
        i = 1
        while os.path.exists(filepath):
            filepath = os.path.join(dirname, f'{filename}_{i}.{extension}')
            i += 1

    with open(filepath, "wb") as file_handler:
        pickle.dump(contents, file_handler)

    return filepath


def main(datasets: List[str], experiments: List[str], max_timesteps: int, iterations: int, processes: int, overwrite_files: bool = False):
    # simplicialbros_datasets = get_simplicialbros_datasets()
    # random_simplicial_complexes = get_random_simplicial_complexes()
    experiments_parameters = list(
        filter(lambda x: x['tag'] in experiments, simulations_parameters))
    for dataset in datasets:
        simplicial_complex: SimplicialComplex = None
        if dataset in simplicialbros_datasets:
            simplicial_complex = from_simplicial_csvs(dataset)
            results_dir = os.path.join(
                contagion_results_dir, config['SimplicialDB']['dbname'])
        elif dataset in random_simplicial_complexes:
            simplicial_complex = from_random_sc_file(dataset)
            results_dir = os.path.join(contagion_results_dir, 'rsc')
        elif dataset in iacopini_simplicial_complexes:
            simplicial_complex = from_iacopini_cliques(dataset)
            results_dir = os.path.join(contagion_results_dir, 'iacopini')
        else:
            raise Exception(
                f'{dataset} is not a valid dataset/random simplicial complex')
        logger.info('Chosen dataset: %s, k=%f, k_delta=%f', dataset,
                    simplicial_complex.k, simplicial_complex.k_delta)
        for simulation_parameters in experiments_parameters:
            tag = itemgetter('tag')(simulation_parameters)
            label = f'{dataset}_{tag} - lambda_slices'
            results = simulation(label, simplicial_complex,
                                 simulation_parameters, max_timesteps, iterations, processes)

            # And save the results to a pickle file
            filepath = save_to_file(results_dir, label, 'pickle', results)

            logger.info(
                '[%s]: Simulation finished. Saving results to %s', label, filepath)

            if "rhos_over_time" in simulation_parameters and "rho_0s" in simulation_parameters["rhos_over_time"]:
                rhos, stationary_rhos, k, k_delta, lambdas, sigma, sigma_delta, rho0s_per_lambda_delta, mu = results

                lambda_delta = None
                if "lambda_delta" in simulation_parameters["rhos_over_time"] and isinstance(simulation_parameters["rhos_over_time"]["lambda_delta"], (float, int)):
                    lambda_delta = simulation_parameters["rhos_over_time"]["lambda_delta"]

                if "beta_delta" in simulation_parameters["rhos_over_time"] and isinstance(simulation_parameters["rhos_over_time"]["beta_delta"], (float, int)):
                    if lambda_delta is not None:
                        raise Exception(
                            'Simulation parameters MUST depend either on betas or lambdas, but not both')
                    lambda_delta = 1. * \
                        (k/mu) * \
                        simulation_parameters["rhos_over_time"]["beta_delta"]

                lambda1 = None
                if "lambda" in simulation_parameters["rhos_over_time"] and isinstance(simulation_parameters["rhos_over_time"]["lambda"], (float, int)):
                    lambda1 = simulation_parameters["rhos_over_time"]["lambda"]

                if "beta" in simulation_parameters["rhos_over_time"] and isinstance(simulation_parameters["rhos_over_time"]["beta"], (float, int)):
                    if lambda1 is not None:
                        raise Exception(
                            'Simulation parameters MUST depend either on betas or lambdas, but not both')
                    lambda1 = 1. * \
                        (k/mu) * \
                        simulation_parameters["rhos_over_time"]["beta"]

                if lambda1 is None or lambda_delta is None:
                    lambda1, lambda_delta = select_parameters_for_rhos_over_time(
                        stationary_rhos, lambda_delta)

                rhos_over_time_parameters = {
                    "mu": simulation_parameters["mu"],
                    "lambdas": [lambda1],
                    "rho0s_per_lambda_delta": {
                        lambda_delta: simulation_parameters["rhos_over_time"]["rho_0s"]
                    }
                }

                label = dataset + ' - rhos_over_time'
                results = simulation(
                    label, simplicial_complex, rhos_over_time_parameters, max_timesteps, iterations, processes)

                # And save the results to a pickle file
                filepath = save_to_file(
                    results_dir, label, 'pickle', results, overwrite=overwrite_files)

                logger.info(
                    '[%s]: Simulation finished. Saving results to %s', label, filepath)


def get_experiments():
    experiments = [simulation_parameter['tag']
                   for simulation_parameter in simulations_parameters]
    experiments.sort()

    return experiments


if __name__ == "__main__":
    # execute only if run as a script

    parser: ArgumentParser = ArgumentParser(
        description='Run the contagion model on dataset or random simplicial complex')

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-d", "--datasets",
                       help="a dataset or a comma-separated list of datasets to load")
    group.add_argument("-l",
                       "--listdatasets",
                       help="do nothing but get the list available simplicial datasets/random-simplicial-complexes to load from db",
                       action="store_true")
    group2 = parser.add_mutually_exclusive_group()
    group2.add_argument("-e", "--experiments",
                        help="an experiment or a comma-separated list of experiments to run")
    group2.add_argument("-le",
                        "--listexperiments",
                        help="do nothing but get the list available predefined experiments",
                        action="store_true")
    parser.add_argument("-t",
                        "--timesteps",
                        help="the maximum amount of time steps to simulate (overwrites those in simulation parameters)")
    parser.add_argument("-i",
                        "--iterations",
                        help="the amount of iterations to run")
    parser.add_argument("-p",
                        "--processes",
                        help="the amount of parallel processes to use for computation")
    parser.add_argument("-f",
                        "--overwritefiles",
                        help="overwrite contagion results' files (default is to create new files)",
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

        sys.exit()

    experiments_tags = get_experiments()
    if args.listexperiments:
        print('Available experiments: \n' + ','.join(experiments_tags))
        sys.exit()

    if not args.datasets:
        parser.print_usage()
        sys.exit()

    if args.experiments:
        experiments_tags = args.experiments.split(',')

    dsets: List[str] = args.datasets.split(',')

    max_timesteps = int(args.timesteps) if args.timesteps else None

    iterations = int(args.iterations) if args.iterations else ITERATIONS

    processes = int(args.processes) if args.processes else PROCESSES

    main(datasets=dsets, experiments=experiments_tags, max_timesteps=max_timesteps,
         iterations=iterations, processes=processes, overwrite_files=(args.overwritefiles or None))
