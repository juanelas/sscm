import json
import os
import pickle
import random
from itertools import combinations
from typing import Dict, List, Sequence, Set, Tuple

import pandas as pd
from directories import (db_simplicialcomplex_dir, iacopini_json_cliques,
                         ramdom_simplicialcomplex_dir, stats_dir)


Edge = Tuple[int, int]
Triangle = Tuple[int, int, int]


class Node():
    node_id: int
    triangle_neighbours: List[Edge]
    neighbours: List[int]

    def __init__(self, node_id: int) -> None:
        self.node_id = node_id
        self.triangle_neighbours = []
        self.neighbours = []

    def add_neighbours(self, qface):
        q = len(qface) - 1
        if q == 1:  # edge
            self.neighbours.append(
                qface[0] if qface[0] != self.node_id else qface[1])
        elif q > 1:  # triangle or more
            self.triangle_neighbours.extend(
                [tuple(node for node in qface if node != self.node_id)])
        else:
            raise Exception('Only up to 2-faces (triangles) supported by now')


class SimplicialComplex:
    node_ids: List[int]
    edges: List[Edge]
    triangles: List[Triangle]
    k: float
    k_delta: float
    _avg_k: float
    _avg_k_delta: float
    _nodes: Dict[int, Node]

    def __init__(self, nodes: List[int], edges: List[Edge], triangles: List[Triangle], k: float = None, k_delta: float = None) -> None:
        self.node_ids = nodes
        self.edges = edges
        self.triangles = triangles
        self.k = k
        self.k_delta = k_delta
        self._avg_k = None
        self._avg_k_delta = None
        self._nodes = {}

        if self.k is None:
            self.k = self.avg_k
        if self.k_delta is None:
            self.k_delta = self.avg_k_delta

    def _add_neighbours(self, node_ids: Tuple):
        for node in node_ids:
            if node not in self._nodes:
                self._nodes[node] = Node(node)
            self._nodes[node].add_neighbours(node_ids)

    @property
    def nodes(self):
        if not self._nodes:
            for edge in self.edges:
                self._add_neighbours(edge)
            for triangle in self.triangles:
                self._add_neighbours(triangle)
            for node in self.node_ids:
                if node not in self._nodes:
                    self._nodes[node] = Node(node)

        return self._nodes

    @property
    def N(self) -> int:
        return len(self.node_ids)

    @property
    def avg_k(self) -> float:
        if self._avg_k is None:
            self._avg_k = 1.*sum([len(node.neighbours)
                                 for node in self.nodes.values()])/self.N
        return self._avg_k

    @property
    def avg_k_delta(self) -> float:
        if self._avg_k_delta is None:
            self._avg_k_delta = 1.*sum([len(node.triangle_neighbours)
                                        for node in self.nodes.values()])/self.N
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
                "nodes": self.node_ids,
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

    # degrees = pd.read_csv(degrees_csv, sep=';')
    # k = float(degrees.loc[degrees['dataset'] ==
    #           dataset].loc[degrees['q'] == 0]['node_to_qfaces_degree[1]: avg'])

    # k_delta = float(degrees.loc[degrees['dataset'] ==
    #                 dataset].loc[degrees['q'] == 0]['node_to_qfaces_degree[2]: avg'])

    return SimplicialComplex(nodes, edges, triangles)


def from_random(N: int, k1: float, k2: float):

    p2 = (2.*k2)/((N-1.)*(N - 2))
    p1 = (k1 - 2.*k2)/(N - 1 - 2.*k2)
    if (p1 < 0) or (p2 < 0):
        raise ValueError(
            f'Negative probability!\n\tp1={p1}\n\tp2={p2}\n\tk1={k1}\n\tk2={k2}')

    if (p1 > 1) or (p2 > 1):
        raise ValueError(
            f'Probability > 1 !\n\tp1={p1}\n\tp2={p2}\n\tk1={k1}\n\tk2={k2}')

    print(f'Generating random simplicial complex with \n\tp1={p1}\n\tp2={p2}\n\tk1={k1}\n\tk2={k2}')
    
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

    # return SimplicialComplex(nodes, edges, triangles, k1, k2)
    return SimplicialComplex(nodes, edges, triangles)


def from_pickle_file(filepath):
    with open(filepath, 'rb') as file:
        sc_data = pickle.load(file)
        return SimplicialComplex(sc_data['nodes'], sc_data['edges'], sc_data['triangles'], sc_data['k'], sc_data['k_delta'])


def from_random_sc_file(filename):
    filepath = os.path.join(ramdom_simplicialcomplex_dir, f'{filename}.pickle')
    if not os.path.isfile(filepath):
        raise Exception(f'{filepath} is not a regular file')

    return from_pickle_file(filepath)


def from_iacopini_cliques(dataset, n_minutes=5, thr=.8, realization=0):
    filepath = os.path.join(
        iacopini_json_cliques, f'random_{str(n_minutes)}_{str(thr)}min_cliques_{dataset}.json')

    with open(filepath, 'r', encoding='utf8') as file:
        cliques_list = json.load(file)

        # # considering one realization of the SCM
        # realization_number = random.choice(range(len(cliques_list)))
        # cliques = cliques_list[realization_number]
        cliques = cliques_list[realization]

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
