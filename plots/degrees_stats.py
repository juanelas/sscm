"""Plots figures wrt statistics of the different degrees"""

from glob import glob

import pandas as pd
from directories import stats_dir
from logger import logger

from .deg_classical import classical_degree
from .deg_classical_and_node_to_facet_and_maximal import classical_and_node_to_facets_and_maximal_degree
from .deg_classical_and_node_to_qfaces import classical_and_node_to_qfaces_degree


def dataset_degrees_stats(dataset: str, df_dataset_stats: pd.DataFrame,
                          df_degrees_stats: pd.DataFrame):
    """Statistics of the different degrees of a given dataset"""

    classical_degree(dataset)
    classical_and_node_to_facets_and_maximal_degree(dataset, df_dataset_stats)
    classical_and_node_to_qfaces_degree(dataset, df_degrees_stats)

    logger.info("%s: Done!", dataset)


def degrees_stats():
    """Statistics of the different degrees"""

    df_datasets_stats = pd.read_csv(
        glob(f'{stats_dir}/datasets_stats.csv')[0], sep=';')
    df_datasets_stats = df_datasets_stats.set_index('dataset')

    df_degrees_stats = pd.read_csv(glob(
        f'{stats_dir}/degrees_stats.csv')[0], sep=';').dropna(subset=['maximal_degree: max'])
    df_degrees_stats = df_degrees_stats.set_index('dataset')

    datasets = df_datasets_stats.index

    for dataset in datasets:
        dataset_degrees_stats(
            dataset, df_datasets_stats.loc[dataset], df_degrees_stats.loc[dataset])
