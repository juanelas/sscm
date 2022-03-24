import os
import pickle
import sys
from argparse import ArgumentParser
from glob import glob
from multiprocessing import Pool
from typing import List

import numpy as np
import pandas as pd

from contagion.run_simulation import run_simulation
from contagion.SimplicialComplex import from_simplicial_csvs
from directories import contagion_results_dir, stats_dir
from logger import logger

# Infection parameters
mu = 0.05
lambdas = np.arange(0.2, 2.21, .1) # from 0.2 to 2.2 every 0.1. I use 2.21 because final is not included
lambda_deltas = [0, 0.8, 2.5, 2.5]
# initial conditions (rate of infected)
initial_infected_rates = [.01, .01, .01, .4]

# Simulation Parameters
MAX_TIMESTEPS = 6000
ITERATIONS = 100
PROCESSES = 6


def main(datasets, max_timesteps=MAX_TIMESTEPS, iterations=ITERATIONS, processes=PROCESSES):
    for dataset in datasets:
        simplicial_complex = from_simplicial_csvs(dataset)
        simulation_parameters = list(
            zip(lambda_deltas, initial_infected_rates))
        for i in range(len(simulation_parameters)):
            lambda_delta, initial_infected_rate = simulation_parameters[i]
            logger.info(
                f'lambda_delta: {lambda_delta}, initial_infected_rate: {initial_infected_rate}')

            # Preparing arguments for the parallel processing
            arguments = []
            description = f'{dataset} {i + 1}/{len(simulation_parameters)}'
            for iteration in range(iterations):
                arguments.append([f'{description}: it{iteration}/{iterations}', simplicial_complex,
                                 lambdas, lambda_delta, mu, initial_infected_rate, max_timesteps])

            ################################ Running in parallel
            pool = Pool(processes=processes)
            results = pool.map(run_simulation, arguments)

            # Saving
            filename = f'{dataset}_mu{mu}_lambdaD{lambda_delta}_infectedRate{initial_infected_rate}.p'
            pickle.dump(results, open(os.path.join(
                contagion_results_dir, filename), "wb"))


if __name__ == "__main__":
    # execute only if run as a script

    parser: ArgumentParser = ArgumentParser(
        description='Run the contagion model on dataset')
    parser.add_argument("-d",
                        "--datasets",
                        help="a dataset or a comma-separated list of datasets to load")
    parser.add_argument("-t",
                        "--timesteps",
                        help="the maximum amount of time steps to simulate")
    parser.add_argument("-i",
                        "--iterations",
                        help="the amount of iterations to run")
    parser.add_argument("-p",
                        "--processes",
                        help="the amount of parallel processes to use for computation")
    parser.add_argument("-l",
                        "--listdatasets",
                        help="do nothing but get the list available datasets to load from db",
                        action="store_true")

    args = parser.parse_args()

    if args.listdatasets:
        df_datasets_stats = pd.read_csv(
            glob(f'{stats_dir}/datasets_stats.csv')[0], sep=';')
        df_datasets_stats = df_datasets_stats.set_index('dataset')
        datasets = df_datasets_stats.index
        print(",".join(datasets))
        sys.exit()

    dsets: List[str] = args.datasets.split(',') if args.datasets else None

    max_timesteps = int(args.timesteps) if args.timesteps else MAX_TIMESTEPS

    iterations = int(args.iterations) if args.iterations else ITERATIONS

    processes = int(args.processes) if args.processes else PROCESSES

    main(dsets, max_timesteps, iterations, processes)
