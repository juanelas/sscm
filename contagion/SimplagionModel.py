import random
from typing import Dict, List

import numpy as np

from contagion.SimplicialComplex import Node, SimplicialComplex


class ContagionNode(Node):
    beta: float
    beta_delta: float
    mu: float
    sigma: float
    sigma_delta: float
    bounded_beta: bool
    infected: bool

    def __init__(self, node: Node, beta: float, beta_delta: float, mu: float, sigma: float = None, sigma_delta: float = None, bounded_beta: bool = True) -> None:
        super().__init__(node.node_id)
        self.neighbours = node.neighbours
        self.triangle_neighbours = node.triangle_neighbours

        self.beta = beta
        self.beta_delta = beta_delta
        self.mu = mu
        self.sigma = sigma
        self.sigma_delta = sigma_delta
        self.bounded_beta = bounded_beta
        self.infected = False


def node_recover(node: ContagionNode) -> bool:
    if random.random() <= node.mu:
        node.infected = False
        return True
    return False


def is_infected(node: ContagionNode, beta: float, beta_delta: float, nodes: Dict[int, ContagionNode]) -> bool:
    if node.infected is True:
        raise Exception('Node %d already infected!', node.node_id)

    infected_neighbours = [
        neighbour for neighbour in node.neighbours if nodes[neighbour].infected is True]
    for infected_neighbour in infected_neighbours:
        if random.random() < beta:
            return True

    infected_triangle_neighbours = [
        edge for edge in node.triangle_neighbours if nodes[edge[0]].infected is True and nodes[edge[1]].infected is True]
    for infected_triangle in infected_triangle_neighbours:
        if random.random() < beta_delta:
            return True

    return False


class SimplagionModel():
    simplicial_complex: SimplicialComplex

    beta: float
    beta_delta: float
    mu: float
    sigma: float
    sigma_delta: float
    bounded_beta: bool

    nodes: Dict[int, ContagionNode]

    initial_rate_of_infected_nodes: float

    # going to use this to store the number of nodes that are infected in every time step
    no_infected_nodes: List[int]
    rhos: List[float]

    def __init__(self, simplicial_complex: SimplicialComplex, beta: float, beta_delta: float, mu: float, sigma: float = None, sigma_delta: float = None, bounded_beta=True):
        # parameters
        self.simplicial_complex = simplicial_complex

        self.beta = beta
        self.beta_delta = beta_delta
        self.mu = mu
        self.sigma = sigma
        self.sigma_delta = sigma_delta
        self.bounded_beta = bounded_beta

        self.nodes = {}
        for node_id, node in simplicial_complex.nodes.items():
            self.nodes[node_id] = ContagionNode(
                node, beta, beta_delta, mu, sigma, sigma_delta, bounded_beta)

        self.initial_rate_of_infected_nodes = 0

        # going to use this to store the number of nodes that are infected in every time step
        self.no_infected_nodes = [0]
        self.rhos = [0]

    def initial_infections(self, initial_rate_of_infected_nodes):
        self.initial_rate_of_infected_nodes = initial_rate_of_infected_nodes

        initial_no_infected_nodes = int(
            initial_rate_of_infected_nodes * self.simplicial_complex.N)

        # Compute the initial infected nodes as random
        while self.no_infected_nodes[0] < initial_no_infected_nodes:
            # select one to infect among the supsceptibles
            node_to_infect = random.choice(self.simplicial_complex.node_ids)
            if self.nodes[node_to_infect].infected is False:
                self.no_infected_nodes[0] += 1
                self.nodes[node_to_infect].infected = True

        self.rhos[0] = self.no_infected_nodes[0] / self.simplicial_complex.N

    def run(self, max_timesteps: int):
        timestep = 1

        while self.no_infected_nodes[-1] > 0 and self.no_infected_nodes[-1] < self.simplicial_complex.N and timestep < max_timesteps:
            beta = get_beta(beta=self.beta, sigma=self.sigma,
                            bounded=self.bounded_beta)
            beta_delta = get_beta(
                beta=self.beta_delta, sigma=self.sigma_delta, bounded=self.bounded_beta)

            non_infected_nodes = [
                node for node in self.nodes.values() if node.infected is False]

            infected_nodes = [
                node for node in self.nodes.values() if node.infected is True]

            newly_infected = list(filter(lambda x: is_infected(
                x, beta, beta_delta, self.nodes), non_infected_nodes))

            # for node in newly_infected:
            #     if node.infected is False:
            #         print("NORRRR")
            #     if self.nodes[node.node_id].infected is False:
            #         print('NORRRR')

            self.no_infected_nodes.append(
                self.no_infected_nodes[timestep - 1] + len(newly_infected))

            # RECOVERIES
            # newly_recovered = set()

            # for node in self.infected:
            #     if random.random() <= mu:
            #         newly_recovered.add(node)

            # # Remove the recovered nodes from the infected set
            # for recovered_node in newly_recovered:
            #     self.infected.remove(recovered_node)

            # # Update the nodes that have been infected
            # self.infected.update(newly_infected)

            recovered = list(filter(node_recover, infected_nodes))

            # Update the nodes that have been infected
            for node in newly_infected:
                node.infected = True

            # for node in recovered:
            #     if self.nodes[node.node_id].infected is True:
            #         print("NORRRR: bad recovery")

            self.no_infected_nodes[timestep] -= len(recovered)

            # update rhos
            self.rhos.append(
                self.no_infected_nodes[timestep] / self.simplicial_complex.N)

            # every 100 timesteps we check if stationary, and stop the simulation if it is
            # if timestep % 100 == 0 and len(self.rhos) > 50 and statistics.stdev(self.rhos[-50:]) < .01:
            #     timestep = max_timesteps

            # increment the timestep
            timestep += 1


def bounded_normal_random_sample(mean: float = None, std_dev: float = None, bounded: bool = True):
    if mean is None:
        mean = 1
    if std_dev is None:
        std_dev = 1

    if mean > 1 or mean < 0:
        raise Exception('beta mean MUST be 0<=mean<=1. It is a probability!!')

    ret = np.random.normal(mean, std_dev)

    if bounded:
        while ret < 0 or ret > 1:
            ret = np.random.normal(mean, std_dev)

    return ret


def get_beta(beta: float, sigma: float = None, bounded: bool = True):
    if sigma is None:
        return beta

    return bounded_normal_random_sample(beta, sigma, bounded)
