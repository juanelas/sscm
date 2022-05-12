import os
import pickle
import sys
from argparse import ArgumentParser
from glob import glob
from multiprocessing import Pool
from operator import itemgetter
from pathlib import Path
from typing import List
from directories import config

import numpy as np
import pandas as pd
from tqdm import tqdm

from contagion.run_simulation import run_simulation
from contagion.SimplicialComplex import SimplicialComplex, from_simplicial_csvs, from_random_sc_file, from_iacopini_cliques
from contagion.utils import parse_results
from directories import contagion_results_dir, iacopini_json_cliques, ramdom_simplicialcomplex_dir, stats_dir
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
    {  # Experiment 1
        "tag": "ex1",
        # Infection parameters. For the slices with different values of lambda
        "mu": 0.7,
        # from 0.2 to 3.0 every 0.2. I use 3.1 because final value is not included. Lambda = beta/mu
        "lambdas": np.array([.5]) / .7,
        # beta_delta = .25 => lambda_delta = .25/.7
        "rho0s_per_lambda_delta": {
            .25/.7: [.2, .8]
        },
        "sigma": .35,
        "sigma_delta": .25
    },
    {  # Experiment 2
        "tag": "ex2",
        # Infection parameters. For the slices with different values of lambda
        "mu": 0.5,
        # from 0.2 to 3.0 every 0.2. I use 3.1 because final value is not included. lambda = k/mu * beta
        "lambdas": np.array([.6]) / .5,
        # beta_delta = .25 => lambda_delta = .25/.7
        "rho0s_per_lambda_delta": {
            .3/.5: [.2, .8]
        },
        "sigma": .5,
        "sigma_delta": .6
    },
    {  # Experiment 3
        "tag": "ex3",
        # Infection parameters. For the slices with different values of lambda
        "mu": 0.7,
        # from 0.2 to 3.0 every 0.2. I use 3.1 because final value is not included. Lambda = beta/mu
        "lambdas": np.array([.8]) / .7,
        # beta_delta = .25 => lambda_delta = .25/.7
        "rho0s_per_lambda_delta": {
            .8/.7: [.2, .8]
        },
        "sigma": .2,
        "sigma_delta": .2
    }
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

    tag, mu, lambdas, sigma, sigma_delta, rho0s_per_lambda_delta = itemgetter(
        'tag', 'mu', 'lambdas', 'sigma', 'sigma_delta', 'rho0s_per_lambda_delta')(simulation_parameters)

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
                          lambdas, sigma, sigma_delta, mu, rho0s_per_lambda_delta, max_timesteps])

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


def save_to_file(dirname, filename, extension, contents):
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    
    filepath = os.path.join(dirname, f'{filename}.{extension}')
    i = 1
    while os.path.exists(filepath):
        filepath = os.path.join(dirname, f'{filename}_{i}.{extension}')
        i += 1

    with open(filepath, "wb") as file_handler:
        pickle.dump(contents, file_handler)

    return filepath


def main(datasets: List[str], max_timesteps=MAX_TIMESTEPS, iterations=ITERATIONS, processes=PROCESSES):
    # simplicialbros_datasets = get_simplicialbros_datasets()
    # random_simplicial_complexes = get_random_simplicial_complexes()
    for dataset in datasets:
        simplicial_complex: SimplicialComplex = None
        if dataset in simplicialbros_datasets:
            simplicial_complex = from_simplicial_csvs(dataset)
            results_dir = os.path.join(contagion_results_dir, config['SimplicialDB']['dbname'])
        elif dataset in random_simplicial_complexes:
            simplicial_complex = from_random_sc_file(dataset)
            results_dir = os.path.join(contagion_results_dir, 'rsc')
        elif dataset in iacopini_simplicial_complexes:
            simplicial_complex = from_iacopini_cliques(dataset)
        else:
            raise Exception(
                f'{dataset} is not a valid dataset/random simplicial complex')

        for simulation_parameters in simulations_parameters:
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
                if "lambda_delta" in simulation_parameters["rhos_over_time"] and (type(simulation_parameters["rhos_over_time"]["lambda_delta"]) is float or type(simulation_parameters["rhos_over_time"]["lambda_delta"]) is int):
                    lambda_delta = simulation_parameters["rhos_over_time"]["lambda_delta"]

                lambda1 = None
                if "lambda" in simulation_parameters["rhos_over_time"] and (type(simulation_parameters["rhos_over_time"]["lambda"]) is float or type(simulation_parameters["rhos_over_time"]["lambda"]) is int):
                    lambda1 = simulation_parameters["rhos_over_time"]["lambda"]
                else:
                    lambda1, lambda_delta = select_parameters_for_rhos_over_time(
                        stationary_rhos, lambda_delta)

                rhos_over_time_parameters = {
                    # Infection parameters. For the slices with different values of lambda
                    "mu": simulation_parameters["mu"],
                    # from 0.2 to 3.0 every 0.2. I use 3.1 because final value is not included
                    "lambdas": [lambda1],
                    "rho0s_per_lambda_delta": {
                        lambda_delta: simulation_parameters["rhos_over_time"]["rho_0s"]
                    }
                }

                label = dataset + ' - rhos_over_time'
                results = simulation(
                    label, simplicial_complex, rhos_over_time_parameters, max_timesteps, iterations, processes)

                # And save the results to a pickle file
                filepath = save_to_file(results_dir, label, 'pickle', results)

                logger.info(
                    '[%s]: Simulation finished. Saving results to %s', label, filepath)


def get_random_simplicial_complexes():
    def filename(filepath):
        return Path(filepath).stem

    return list(map(filename, glob(os.path.join(ramdom_simplicialcomplex_dir, '*.pickle'))))


def get_simplicialbros_datasets():
    df_datasets_stats = pd.read_csv(
        glob(f'{stats_dir}/datasets_stats.csv')[0], sep=';')
    df_datasets_stats = df_datasets_stats.set_index('dataset')
    return df_datasets_stats.index

def get_iacopini_cliques():
    def dataset(filepath):
        return Path(filepath).stem.split('_')[-1]

    return list(set(map(dataset, glob(os.path.join(iacopini_json_cliques, '*.json')))))

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
    parser.add_argument("-t",
                        "--timesteps",
                        help="the maximum amount of time steps to simulate")
    parser.add_argument("-i",
                        "--iterations",
                        help="the amount of iterations to run")
    parser.add_argument("-p",
                        "--processes",
                        help="the amount of parallel processes to use for computation")

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

    if not args.datasets:
        parser.print_usage()
        sys.exit()

    dsets: List[str] = args.datasets.split(',')

    max_timesteps = int(args.timesteps) if args.timesteps else MAX_TIMESTEPS

    iterations = int(args.iterations) if args.iterations else ITERATIONS

    processes = int(args.processes) if args.processes else PROCESSES

    main(dsets, max_timesteps, iterations, processes)
