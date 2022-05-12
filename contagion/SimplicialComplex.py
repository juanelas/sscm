import json
import os
import pickle
import random
from itertools import combinations
from typing import Dict, List, Set, Tuple

import pandas as pd
from directories import (db_simplicialcomplex_dir, iacopini_json_cliques,
                         ramdom_simplicialcomplex_dir, stats_dir)


class SimplicialComplex:
    nodes: List[int]
    edges: List[Tuple[int, int]]
    triangles: List[Tuple[int, int, int]]
    _k: float
    _k_delta: float
    _avg_k: float
    _avg_k_delta: float
    _node_neighbours: Dict[int, Set[int]]

    def __init__(self, nodes: List[int], edges: List[Tuple[int, int]], triangles: List[Tuple[int, int, int]], k: float = None, k_delta: float = None) -> None:
        self.nodes = nodes
        self.edges = edges
        self.triangles = triangles
        self.k = k
        self.k_delta = k_delta
        self._avg_k = None
        self._avg_k_delta = None
        self._node_neighbours = {}

        if self.k is None:
            self.k = self.avg_k
        if self.k_delta is None:
            self.k_delta = self.avg_k_delta

    def _add_neighbours(self, neighbours: Set[int]):
        for node in neighbours:
            node_neighbours = [
                neighbour for neighbour in neighbours if neighbour is not node]
            if node not in self._node_neighbours:
                self._node_neighbours[node] = set(node_neighbours)
            else:
                self._node_neighbours[node].update(set(node_neighbours))

    @property
    def node_neighbours(self):
        if not self._node_neighbours:
            for edge in self.edges:
                self._add_neighbours(set(edge))
            for triangle in self.triangles:
                self._add_neighbours(set(triangle))

        return self._node_neighbours

    @property
    def N(self):
        return len(self.nodes)

    @property
    def avg_k(self):
        if self._avg_k is None:
            self._avg_k = 1.*sum([len(v)
                                 for v in self.node_neighbours.values()])/self.N
        return self._avg_k

    @property
    def avg_k_delta(self):
        if self._avg_k_delta is None:
            self._avg_k_delta = 3.*len(self.triangles)/self.N
        return self._avg_k_delta

    def to_pickle_file(self, file, overwrite=False):
        def check_and_rename(file):
            original_file = file
            add = 1
            while (os.path.isfile(file)):
                split = original_file.split(".")
                file_name = '.'.join(split[:-1]) + '_' + str(add)
                file = '.'.join([file_name, split[-1]])
                add += 1

            return file

        filepath = check_and_rename(file) if overwrite is False else file

        with open(filepath, 'wb') as file:
            pickle.dump({
                "nodes": self.nodes,
                "edges": self.edges,
                "triangles": self.triangles,
                "k": self.k,
                "k_delta": self.k_delta
            }, file)
            return filepath


def from_simplicial_csvs(dataset: str):
    def pgarray_str_to_nparray(pg_array: str):
        return ([int(val) for val in pg_array[1:-1].split(',')])

    def __get_faces(csvpath: str):
        return pd.read_csv(csvpath, sep=';', header=None, names=['nodes'], converters={'nodes': pgarray_str_to_nparray})

    def __check_csv(csvpath: str):
        if not os.path.isfile(csvpath) or os.stat(csvpath).st_size == 0:
            raise Exception(
                f'no computed nodes for dataset {dataset} at {csvpath}')

    q0_faces_csv = os.path.join(
        db_simplicialcomplex_dir, f'{dataset}_q0_faces.csv')
    __check_csv(q0_faces_csv)
    edges_csv = os.path.join(db_simplicialcomplex_dir,
                             f'{dataset}_q1_faces.csv')
    __check_csv(edges_csv)
    triangles_csv = os.path.join(
        db_simplicialcomplex_dir, f'{dataset}_q2_faces.csv')
    __check_csv(triangles_csv)
    degrees_csv = os.path.join(stats_dir, 'degrees_stats.csv')
    __check_csv(degrees_csv)

    q0_faces = __get_faces(q0_faces_csv)['nodes']
    nodes = [q0_face[0] for q0_face in q0_faces]
    edges = list(map(tuple, __get_faces(edges_csv)['nodes'].values.tolist()))
    triangles = list(map(tuple, __get_faces(
        triangles_csv)['nodes'].values.tolist()))

    degrees = pd.read_csv(degrees_csv, sep=';')
    k = float(degrees.loc[degrees['dataset'] ==
              dataset].loc[degrees['q'] == 0]['node_to_qfaces_degree[1]: avg'])

    k_delta = float(degrees.loc[degrees['dataset'] ==
                    dataset].loc[degrees['q'] == 0]['node_to_qfaces_degree[2]: avg'])

    return SimplicialComplex(nodes, edges, triangles, k, k_delta)


def from_random(N: int, k: float, k_delta: float):
    p2 = (2.*k_delta)/((N-1.)*(N-2.))
    p1 = (k - 2.*k_delta)/((N-1.) - 2.*k_delta)
    if (p1 < 0) or (p2 < 0):
        raise ValueError('Negative probability!')

    nodes: List[int] = list(range(N))
    edges: List[Tuple[int, int]] = []
    triangles: List[Tuple[int, int, int]] = []

    for edge in combinations(nodes, 2):
        if random.random() <= p1:
            edges.append(edge)

    for triangle in combinations(nodes, 3):
        if random.random() <= p2:
            triangles.append(triangle)
            edges.extend([
                (triangle[0], triangle[1]),
                (triangle[0], triangle[2]),
                (triangle[1], triangle[2]),
            ])

    edges = list(set(edges))

    return SimplicialComplex(nodes, edges, triangles, k, k_delta)


def from_pickle_file(filepath):
    with open(filepath, 'rb') as file:
        sc_data = pickle.load(file)
        return SimplicialComplex(sc_data['nodes'], sc_data['edges'], sc_data['triangles'], sc_data['k'], sc_data['k_delta'])


def from_random_sc_file(filename):
    filepath = os.path.join(ramdom_simplicialcomplex_dir, f'{filename}.pickle')
    if not os.path.isfile(filepath):
        raise Exception(f'{filepath} is not a regular file')

    return from_pickle_file(filepath)


def from_iacopini_cliques(dataset, n_minutes=5, thr=.8):
    filepath = os.path.join(
        iacopini_json_cliques, f'random_{str(n_minutes)}_{str(thr)}min_cliques_{dataset}.json')

    with open(filepath, 'r', encoding='utf8') as file:
        cliques_list = json.load(file)
        # considering one realization of the SCM
        realization_number = random.choice(range(len(cliques_list)))
        cliques = cliques_list[realization_number]

        nodes: List[int] = []
        edges: List[Tuple[int, int]] = []
        triangles: List[Tuple[int, int, int]] = []

        for qface in cliques:
            qface.sort()
            q = len(qface) - 1

            if q == 1:  # if it is an edge
                n1, n2 = qface
                edges.append((n1, n2))
                nodes.extend([n1, n2])

            elif q == 2:  # a triangle
                n1, n2, n3 = qface
                triangles.append((n1, n2, n3))
                edges.extend([
                    (n1, n2),
                    (n1, n3),
                    (n2, n3)
                ])
                nodes.extend([n1, n2, n3])

        nodes = list(set(nodes))
        edges = list(set(edges))
        triangles = list(set(triangles))

    return SimplicialComplex(nodes, edges, triangles)
