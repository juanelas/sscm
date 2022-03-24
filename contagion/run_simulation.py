from typing import List

from logger import logger

from .SimplagionModel import SimplagionModel
from .utils import get_stationary_rho


def run_simulation(args):
    description, simplicial_complex, lambdas, lambda_delta, mu, initial_rate_of_infected_nodes, max_timesteps = args

    k = simplicial_complex.k
    k_delta = simplicial_complex.k_delta

    betas = 1.*(mu/k)*lambdas
    beta_delta = 1.*(mu/k_delta)*lambda_delta

    # here I'll store the evolution of rho over timestep for every SimplagionModel executed for each beta
    rhos: List[List[float]] = []

    # here I'll store the stainary value of rho for every SimplagionModel executed for each beta
    stationary_rhos: List[float] = []

    simplagion_model = SimplagionModel(simplicial_complex)
    simplagion_model.initial_infections(
        initial_rate_of_infected_nodes=initial_rate_of_infected_nodes)
    
    for i in range(len(betas)):
        beta = betas[i]
        logger.info(
            f'[{description} {i + 1}/{len(betas)}] Running model with beta={beta:.6f}, beta_delta={beta_delta:.6f}, mu={mu}, ini_rho={initial_rate_of_infected_nodes}')

        simplagion_model.run(max_timesteps, beta, beta_delta, mu)
        rho = get_stationary_rho(simplagion_model.rhos, last_k_values=100)
        stationary_rhos.append(rho)
        rhos.append(simplagion_model.rhos)

    logger.info('[%s] Simulation finished', description)

    return {
        "rhos": rhos,
        "stationary_rhos": stationary_rhos,
        "k": simplicial_complex.k,
        "k_delta": simplicial_complex.k_delta,
        "lambdas": lambdas,
        "lambda_delta": lambda_delta,
        "mu": mu
    }
