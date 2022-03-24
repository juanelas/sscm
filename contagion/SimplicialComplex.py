import os

import pandas as pd
from directories import simplicialcomplex_dir, stats_dir


class SimplicialComplex:
    nodes: pd.DataFrame
    edges: pd.DataFrame
    triangles: pd.DataFrame
    k: float
    k_delta: float

    def __init__(self, nodes: pd.DataFrame, edges: pd.DataFrame, triangles: pd.DataFrame, k: float, k_delta: float) -> None:
        self.nodes = nodes
        self.edges = edges
        self.triangles = triangles
        self.k = k
        self.k_delta = k_delta


def from_simplicial_csvs(dataset: str):
    def pgarray_str_to_nparray(pg_array: str):
        return ([int(val) for val in pg_array[1:-1].split(',')])

    def __get_faces(csvpath: str):
        return pd.read_csv(csvpath, sep=';', header=None, names=['nodes'], converters={'nodes': pgarray_str_to_nparray})

    def __check_csv(csvpath: str):
        if not os.path.isfile(csvpath) or os.stat(csvpath).st_size == 0:
            raise Exception(
                f'no computed nodes for dataset {dataset} at {csvpath}')

    nodes_csv = os.path.join(simplicialcomplex_dir, f'{dataset}_q0_faces.csv')
    __check_csv(nodes_csv)
    edges_csv = os.path.join(simplicialcomplex_dir, f'{dataset}_q1_faces.csv')
    __check_csv(edges_csv)
    triangles_csv = os.path.join(
        simplicialcomplex_dir, f'{dataset}_q2_faces.csv')
    __check_csv(triangles_csv)
    degrees_csv = os.path.join(stats_dir, 'degrees_stats.csv')
    __check_csv(degrees_csv)

    nodes = __get_faces(nodes_csv)['nodes']
    edges = __get_faces(edges_csv)['nodes']
    triangles = __get_faces(triangles_csv)['nodes']
    degrees = pd.read_csv(degrees_csv, sep=';')
    k = float(degrees.loc[degrees['dataset'] ==
              dataset].loc[degrees['q'] == 0]['node_to_qfaces_degree[1]: avg'])

    k_delta = float(degrees.loc[degrees['dataset'] ==
                    dataset].loc[degrees['q'] == 0]['node_to_qfaces_degree[2]: avg'])

    return SimplicialComplex(nodes, edges, triangles, k, k_delta)
