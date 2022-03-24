from typing import List
import numpy as np


def find_cut(rhos_array):
    # First index with non-zero value >1
    cut = min(np.argwhere(np.count_nonzero(rhos_array, axis=0) > 1))[0]
    return cut


def parse_results(results):

    stationary_rhos_lists, rhos_lists = [], []

    ### Let's us make all the simulations have the same timesteps
    max_timesteps = 0
    for iteration_result in results:
        for lambda1_simulation in iteration_result['rhos']:
            if len(lambda1_simulation) > max_timesteps:
                max_timesteps = len(lambda1_simulation)
    for iteration_result in results:
        stationary_rhos_lists.append(iteration_result['stationary_rhos'])
        for lambda1_simulation in iteration_result['rhos']:
            for i in range(len(lambda1_simulation), max_timesteps):
                lambda1_simulation.append(lambda1_simulation[-1])
        rhos_lists.append(iteration_result['rhos'])

    stationary_rhos_array = np.array(stationary_rhos_lists)
    avg_stationary_rhos = np.mean(stationary_rhos_array, axis=0)
    
    rhos_array = np.array(rhos_lists)
    avg_rhos = np.mean(rhos_array, axis=0)

    k = results[0]['k']
    k_delta = results[0]['k_delta']
    lambdas = list(results[0]['lambdas'])
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

    return avg_stationary_rhos, k, k_delta, avg_rhos, lambdas, mu

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
