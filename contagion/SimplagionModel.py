import random
from typing import List

import numpy as np

from contagion.SimplicialComplex import SimplicialComplex

class SimplagionModel():
    simplicial_complex: SimplicialComplex
    initial_rate_of_infected_nodes: float
    initial_infected_nodes: set
    infected: set
    rhos: List[float]
    stationary: bool

    def __init__(self, simplicial_complex: SimplicialComplex):
        # parameters
        self.simplicial_complex = simplicial_complex
        self.initial_no_infected_nodes = 0
        self.initial_rate_of_infected_nodes = 0

        self.initial_infected_nodes = set()
        # going to use this to store the nodes that are infected in every time step
        self.infected = set()

        # and here we're going to store the density (rho) of nodes infected in every time step
        self.rhos = []

        self.stationary = False

    def initial_infections(self, initial_rate_of_infected_nodes):
        self.initial_rate_of_infected_nodes = initial_rate_of_infected_nodes
        initial_no_infected_nodes = int(
            initial_rate_of_infected_nodes * len(self.simplicial_complex.nodes))

        # Compute the initial infected nodes as random
        while len(self.initial_infected_nodes) < initial_no_infected_nodes:
            # select one to infect among the supsceptibles
            node_to_infect = random.choice(self.simplicial_complex.nodes)
            self.initial_infected_nodes.add(node_to_infect)

    def run(self, max_timesteps: int, beta: float, beta_delta: float, mu: float, sigma: float = None, sigma_delta: float = None):
        if sigma and sigma_delta:
            self.stationary = True

        # reset
        self.rhos = [self.initial_rate_of_infected_nodes]
        self.infected = self.initial_infected_nodes.copy()

        timestep = 1  # The first timesteps is already genrated with the initial set of infected nodes

        while len(self.infected) > 0 and len(self.infected) < len(self.simplicial_complex.nodes) \
                and timestep < max_timesteps:
            newly_infected = set()

            # EDGE CONTAGION
            for edge in self.simplicial_complex.edges:
                node1, node2 = edge
                if node1 in self.infected:
                    if node2 not in self.infected:
                        # infect n2 with probability beta
                        if random.random() <= get_beta(beta, self.stationary, sigma):
                            newly_infected.add(node2)
                else:
                    if node2 in self.infected:
                        # infect n1 with probability beta
                        if random.random() <= get_beta(beta, self.stationary, sigma):
                            newly_infected.add(node1)

            # TRIANGLE CONTAGION
            for triangle in self.simplicial_complex.triangles:
                node1, node2, node3 = triangle
                if node1 in self.infected:
                    if node2 in self.infected:
                        if node3 not in self.infected:
                            # infect n3 with probability beta_delta
                            if random.random() <= get_beta(beta_delta, self.stationary, sigma_delta):
                                newly_infected.add(node3)
                    else:
                        if node3 in self.infected:
                            # infect n2 with probability beta_delta
                            if random.random() <= get_beta(beta_delta, self.stationary, sigma_delta):
                                newly_infected.add(node2)
                else:
                    if (node2 in self.infected) and (node3 in self.infected):
                        # infect n1 with probability beta2
                        if random.random() <= get_beta(beta_delta, self.stationary, sigma_delta):
                            newly_infected.add(node1)

            # RECOVERIES
            newly_recovered = set()

            for node in self.infected:
                if random.random() <= mu:
                    newly_recovered.add(node)

            # Remove the recovered nodes from the infected set
            for recovered_node in newly_recovered:
                self.infected.remove(recovered_node)

            # Update the nodes that have been infected
            self.infected.update(newly_infected)

            # then track the density of infected nodes in every timestep
            self.rhos.append(
                len(self.infected) / len(self.simplicial_complex.nodes))

            # every 100 timesteps we check if stationary, and stop the simulation if it is
            # if timestep % 100 == 0 and len(self.rhos) > 50 and statistics.stdev(self.rhos[-50:]) < .01:
            #     timestep = max_timesteps

            # increment the timestep
            timestep += 1


def bounded_normal_random_sample(mean: float = None, std_dev: float = None):
    if mean is None:
        mean = 1
    if std_dev is None:
        std_dev = 1

    ret = np.random.normal(mean, std_dev)
    while ret < 0:
        ret = np.random.normal(mean, std_dev)

    return np.random.normal(mean, std_dev)


def get_beta(beta: float, stationary: bool = False, sigma: float = None):
    if stationary is False:
        return beta

    return bounded_normal_random_sample(beta, sigma)
