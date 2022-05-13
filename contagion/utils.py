import os
import pickle
from glob import glob
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd
from directories import (contagion_results_dir, iacopini_json_cliques,
                         ramdom_simplicialcomplex_dir, stats_dir)

from contagion.SimplicialComplex import (SimplicialComplex,
                                         from_iacopini_cliques,
                                         from_random_sc_file,
                                         from_simplicial_csvs)


def find_cut(rhos_array):
    # First index with non-zero value >1
    cut = min(np.argwhere(np.count_nonzero(rhos_array, axis=0) > 1))[0]
    return cut


def parse_results(results):

    # evolution of rho over timestep for every SimplagionModel executed for each lambda_delta, rho_0, and lambda
    # rhos: Dict[Dict[Dict[List[float]]]] = {
    #   lambda_delta: {
    #       rho_0: {
    #           lambda: [float]
    #       }
    #   }
    # }

    # stationary value of rho for every SimplagionModel executed for each lambda_delta, rho_0, and lambda
    # stationary_rhos: Dict[Dict[Dict[float]]] = {{
    #   lambda_delta: {
    #       rho_0: {
    #           lambda: float
    #       }
    #   }
    # }

    # result: {
    #     "rhos": rhos,
    #     "stationary_rhos": stationary_rhos,
    #     "k": float,
    #     "k_delta": float,
    #     "lambdas": List[floats],
    #     "rho0s_per_lambda_delta": Dict[List[float]],
    #     "mu": float
    # }
    # results: List[result]

    # Average evolution of rho over timestep for each lambda_delta, rho_0, lambda, iteration
    rhos = __init_rhos(results)

    # stationary value of rho for each lambda_delta, rho_0, lambda, iteration
    stationary_rhos = __init_stationary_rhos(results)

    k = results[0]['k']
    k_delta = results[0]['k_delta']
    lambdas = list(results[0]['lambdas'])
    sigma = results[0].get('sigma')
    sigma_delta = results[0].get('sigma_delta')
    rho0s_per_lambda_delta = results[0]['rho0s_per_lambda_delta']
    mu = results[0]['mu']

    # if cut is False:
    #     avg_stationary_rhos = np.mean(stationary_rhos_array, axis=0)
    #     avg_rhos = np.mean(rhos_array, axis=0)
    #     #std_rhos = np.std(rhos_array, axis=0)

    # else:
    #     cut_point = find_cut(stationary_rhos_array)
    #     cut_stationary_rhos_array = []

    #     for stationary_rhos in stationary_rhos_lists:
    #         clean_rhos = []
    #         for i, rr in enumerate(stationary_rhos):
    #             if i < cut_point:
    #                 clean_rhos.append(rr)
    #             elif rr == 0:
    #                 clean_rhos.append(np.nan)
    #             else:
    #                 clean_rhos.append(rr)
    #         cut_stationary_rhos_array.append(clean_rhos)

    #     cut_stationary_rhos_array = np.array(cut_stationary_rhos_array)
    #     avg_stationary_rhos = np.nanmean(cut_stationary_rhos_array, axis=0)
    #     avg_rhos = np.mean(rhos_array, axis=0)
    #     #std_rhos = np.nanstd(rhos_array, axis=0)

    return rhos, stationary_rhos, k, k_delta, lambdas, sigma, sigma_delta, rho0s_per_lambda_delta, mu


def get_rho_MF(l, lD):
    in_sqrt = (l-lD)**2 - 4.*lD*(1-l)
    if in_sqrt < 0:
        return 0

    rho1 = (lD-l + np.sqrt(in_sqrt))/(2*lD)
    if rho1 > 0:
        return rho1
    else:
        return 0


def get_stationary_rho(rhos_list: List[float], last_k_values=100):
    if len(rhos_list) == 0:
        return 0

    rhos_arr = np.array(rhos_list)

    if rhos_arr[-1] == 1:
        return 1
    elif rhos_arr[-1] == 0:
        return 0
    else:
        avg = np.mean(rhos_arr[-last_k_values:])
        # if there are no infected left nan->0
        return np.nan_to_num(avg)


def __init_rhos(results):
    # Average evolution of rho over timestep for each lambda_delta, rho_0, lambda, iteration
    rhos = __init_array(results, default_value=[])

    # max_timesteps (the number of timesteps in the longest iteration) for each lambda_delta, rho_0, lambda
    max_timesteps = 0

    # Let's us compute the max timesteps for the different iterations of each parameters combination
    for iteration_result in results:
        for lambda_delta, rho_0s in iteration_result['rhos'].items():
            for rho_0, lambdas in rho_0s.items():
                for lambda1, iteration_rhos in lambdas.items():
                    if len(iteration_rhos) > max_timesteps:
                        max_timesteps = len(iteration_rhos)

    # and finally lets add the rhos of the different iterations
    for lambda_delta, rho_0s in rhos.items():
        for rho_0, lambdas in rho_0s.items():
            for lambda1, lambda1_rhos in lambdas.items():
                for iteration_result in results:
                    iteration_rhos = iteration_result['rhos'][lambda_delta][rho_0][lambda1]
                    for i in range(len(iteration_rhos), max_timesteps):
                        iteration_rhos.append(iteration_rhos[-1])
                    lambda1_rhos.append(iteration_rhos)

    return rhos


def __init_stationary_rhos(results):
    # Average evolution of rho over timestep for each lambda_delta, rho_0, lambda, iteration
    stationary_rhos = __init_array(results, default_value=[])

    # and finally lets add the rhos of the different iterations
    for iteration_result in results:
        for lambda_delta, rho_0s in iteration_result['stationary_rhos'].items():
            for rho_0, lambdas in rho_0s.items():
                for lambda1, iteration_stationary_rho in lambdas.items():
                    stationary_rhos[lambda_delta][rho_0][lambda1].append(
                        iteration_stationary_rho)

    return stationary_rhos


def __init_array(results: List, default_value):
    # Average evolution of rho over timestep for each lambda_delta, rho_0, lambda, iteration
    array: Dict[Dict[Dict[List]]] = {}

    # Init
    for iteration_result in results:
        for lambda_delta, rho_0s in iteration_result['rhos'].items():
            array[lambda_delta] = {}
            for rho_0, lambdas in rho_0s.items():
                array[lambda_delta][rho_0] = {}

                for lambda1 in lambdas:
                    try:
                        array[lambda_delta][rho_0][lambda1] = default_value.copy()
                    except AttributeError:
                        array[lambda_delta][rho_0][lambda1] = default_value

    return array


def filename(filepath):
    return Path(filepath).stem


def get_random_simplicial_complexes():
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


def sc_from_dataset(dataset: str) -> SimplicialComplex:
    simplicialbros_datasets = get_simplicialbros_datasets()
    random_simplicial_complexes = get_random_simplicial_complexes()
    iacopini_simplicial_complexes = get_iacopini_cliques()

    if dataset in simplicialbros_datasets:
        simplicial_complex = from_simplicial_csvs(dataset)
    elif dataset in random_simplicial_complexes:
        simplicial_complex = from_random_sc_file(dataset)
    elif dataset in iacopini_simplicial_complexes:
        simplicial_complex = from_iacopini_cliques(dataset)
    else:
        raise Exception(
            f'{dataset} is not a valid dataset/random simplicial complex')

    return simplicial_complex


def get_rsc_results():
    return list(map(filename, glob(os.path.join(contagion_results_dir, 'rsc', '*.pickle'))))


def get_simplicialbros_results(database):
    return list(map(filename, glob(os.path.join(contagion_results_dir, database, '*.pickle'))))


def get_iacopini_results():
    return list(map(filename, glob(os.path.join(contagion_results_dir, 'iacopini', '*.pickle'))))


def available_results():
    results = {}

    def my_f(a):
        return a.split('/')[-2]
    databases = list(map(my_f, glob(f'{contagion_results_dir}/*/')))
    try:
        databases.remove('rsc')
        databases.remove('iacopini')
    except ValueError:
        pass

    results['rsc'] = get_rsc_results()
    results['iacopini'] = get_iacopini_results()

    for database in databases:
        results[database] = get_simplicialbros_results(database)

    contagion_results_names = []
    for db_datasets in results.values():
        contagion_results_names.extend(db_datasets)
    contagion_results_names.sort()
    
    return results, contagion_results_names


def results_from_experiment(experiment_name: str, version: int = 2):
    results, experiments = available_results()
    if experiment_name not in experiments:
        raise Exception(f'No contagion results for {experiment_name}')
    
    dataset_results_file = f'{experiment_name}.pickle'
    for database in results:
        results_dir = os.path.join(contagion_results_dir, database)
        filepath = os.path.join(results_dir, dataset_results_file)
        try:
            with open(filepath, "rb") as file_handler:
                results = pickle.load(file_handler)
                break
        except FileNotFoundError:
            pass

    if version is 0:
        rhos, stationary_rhos, k, k_delta, lambdas, sigma, sigma_delta, rho0s_per_lambda_delta, mu = parse_results(
            results)
    elif version is 1:
        sigma = sigma_delta = None
        rhos, stationary_rhos, k, k_delta, lambdas, rho0s_per_lambda_delta, mu = results
    else:
        rhos, stationary_rhos, k, k_delta, lambdas, sigma, sigma_delta, rho0s_per_lambda_delta, mu = results

    return rhos, stationary_rhos, k, k_delta, lambdas, sigma, sigma_delta, rho0s_per_lambda_delta, mu
