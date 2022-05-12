from typing import Dict, List
import numpy as np


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
    sigma = results[0]['sigma']
    sigma_delta = results[0]['sigma_delta']
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
                    stationary_rhos[lambda_delta][rho_0][lambda1].append(iteration_stationary_rho)

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
