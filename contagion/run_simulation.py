from typing import Dict, List

import numpy as np
from logger import logger

from .SimplagionModel import SimplagionModel
from .utils import get_stationary_rho


def run_simulation(args):
    description, simplicial_complex, lambdas, sigma, sigma_delta, mu, rho0s_per_lambda_delta, max_timesteps = args

    k = simplicial_complex.k
    k_delta = simplicial_complex.k_delta

    betas = 1.*(mu/k)*np.array(lambdas)

    # evolution of rho over timestep for every SimplagionModel executed for each lambda_delta, rho_0, and lambda
    rhos: Dict[Dict[Dict[List[float]]]] = {}

    # stationary value of rho for every SimplagionModel executed for each lambda_delta, rho_0, and lambda
    stationary_rhos: Dict[Dict[Dict[float]]] = {}

    total_runs = np.sum(
        [len(rho0s) for rho0s in rho0s_per_lambda_delta.values()]) * len(lambdas)
    i = 1

    for lambda_delta, rho_0s in rho0s_per_lambda_delta.items():
        rhos[lambda_delta] = {}
        stationary_rhos[lambda_delta] = {}

        beta_delta = 1.*(mu/k_delta)*lambda_delta

        for rho_0 in rho_0s:
            rhos[lambda_delta][rho_0] = {}
            stationary_rhos[lambda_delta][rho_0] = {}

            simplagion_model = SimplagionModel(simplicial_complex)
            simplagion_model.initial_infections(
                initial_rate_of_infected_nodes=rho_0)

            for idx, beta in enumerate(betas):
                lambda1 = lambdas[idx]

                simplagion_model.run(max_timesteps, beta, beta_delta, mu, sigma, sigma_delta)

                rho = get_stationary_rho(
                    simplagion_model.rhos, last_k_values=100)
                stationary_rhos[lambda_delta][rho_0][lambda1] = rho

                rhos[lambda_delta][rho_0][lambda1] = simplagion_model.rhos

                logger.debug('%s - %d/%d -> lambda=%s, lambda_delta=%s, rho_0=%s', description,
                             i, total_runs, f'{lambda1:.2f}', f'{lambda_delta:.2f}', f'{rho_0:.2f}')
                i += 1

    logger.debug('%s. Finished', description)

    return {
        "rhos": rhos,
        "stationary_rhos": stationary_rhos,
        "k": simplicial_complex.k,
        "k_delta": simplicial_complex.k_delta,
        "lambdas": lambdas,
        "sigma": sigma,
        "sigma_delta": sigma_delta,
        "rho0s_per_lambda_delta": rho0s_per_lambda_delta,
        "mu": mu
    }
