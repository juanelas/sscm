import random
import statistics
from typing import List

from contagion.SimplicialComplex import SimplicialComplex


class SimplagionModel():
    simplicial_complex: SimplicialComplex
    initial_rate_of_infected_nodes: float
    initial_infected_nodes: set
    infected: set
    rhos: List[float]

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

    def initial_infections(self, initial_rate_of_infected_nodes):
        self.initial_rate_of_infected_nodes = initial_rate_of_infected_nodes
        initial_no_infected_nodes = int(
            initial_rate_of_infected_nodes * len(self.simplicial_complex.nodes))

        #Compute the initial infected nodes as random
        while len(self.initial_infected_nodes) < initial_no_infected_nodes:
            # select one to infect among the supsceptibles
            node_to_infect = random.choice(
                self.simplicial_complex.nodes)[0]
            self.initial_infected_nodes.add(node_to_infect)

    def run(self, max_timesteps: int, beta: float, beta_delta: float, mu: float):

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
                        # infect n2 with probability beta1
                        if random.random() <= beta:
                            newly_infected.add(node2)
                else:
                    if node2 in self.infected:
                        # infect n1 with probability beta1
                        if random.random() <= beta:
                            newly_infected.add(node1)

            # TRIANGLE CONTAGION
            for triangle in self.simplicial_complex.triangles:
                node1, node2, node3 = triangle
                if node1 in self.infected:
                    if node2 in self.infected:
                        if node3 not in self.infected:
                            # infect n3 with probability beta2
                            if random.random() <= beta_delta:
                                newly_infected.add(node3)
                    else:
                        if node3 in self.infected:
                            # infect n2 with probability beta2
                            if random.random() <= beta_delta:
                                newly_infected.add(node2)
                else:
                    if (node2 in self.infected) and (node3 in self.infected):
                        # infect n1 with probability beta2
                        if random.random() <= beta_delta:
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

            # then track the number of infected nodes in every timestep
            self.rhos.append(
                len(self.infected) / len(self.simplicial_complex.nodes))

            # every 100 timesteps we check if stationary, and stop the simulation if it is
            if timestep % 100 == 0 and len(self.rhos) > 50 and statistics.stdev(self.rhos[-50:]) < .01:
                timestep = max_timesteps

            # increment the timestep
            timestep += 1
