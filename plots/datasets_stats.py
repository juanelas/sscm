"""Generates figures regarding datasets' statistics (nodes, simplices, facets)"""

import os
from glob import glob

import pandas as pd
from directories import stats_dir
from logger import logger

from . import csvfiles_to_df, plot


def datasets_stats():
    """Generates figures regarding datasets' statistics (nodes, simplices, facets)"""
    df_datasets_stats = pd.read_csv(
        glob(f'{stats_dir}/datasets_stats.csv')[0], sep=';')
    df_datasets_stats = df_datasets_stats.set_index('dataset')

    logger.info("Generating histogram of nodes per simplex")
    csv_file_names = glob(f'{stats_dir}/*_simplices_q_dist.csv')
    datasets = []
    for filename in csv_file_names:
        datasets.append(os.path.split(filename)[1].split('_')[0])
    df_sn_hist = csvfiles_to_df(csv_filenames=csv_file_names, column_names=datasets,
                                column_key_increment=1, normalise=True)
    nodes_max = float(df_datasets_stats.loc[:, 'nodes per simplex: max'].max())
    nodes_99 = float(
        df_datasets_stats.loc[:, 'nodes per simplex: percentile 99'].max())
    if nodes_99 / nodes_max < .8:
        xlim = (0, int(nodes_99))
    else:
        xlim = (0, int(nodes_max))
    plot(df_sn_hist,
         xlabel='nodes per simplex',
         ylabel='probability',
         figname='nodes_per_simplex',
         xlim=xlim)

    logger.info("Generating distribution of nodes per simplex")
    df_sn_dist_cumsum = df_sn_hist.cumsum()
    plot(df_sn_dist_cumsum,
         xlabel='nodes per simplex',
         ylabel='normalised cumulative sum',
         figname='nodes_per_simplex_cumsum',
         drawstyle="steps-post",
         markers=False,
         xlim=(0, None),
         ylim=(0, 1)
         )

    logger.info("Generating histogram of nodes per facet")
    csv_file_names = glob(f'{stats_dir}/*_facets_q_dist.csv')
    datasets = []
    for filename in csv_file_names:
        datasets.append(os.path.split(filename)[1].split('_')[0])

    df_fn_hist = csvfiles_to_df(csv_filenames=csv_file_names, column_names=datasets,
                                column_key_increment=1, normalise=True)
    nodes_max = float(df_datasets_stats.loc[:, 'nodes per facet: max'].max())
    nodes_99 = float(
        df_datasets_stats.loc[:, 'nodes per facet: percentile 99'].max())
    if nodes_99 / nodes_max < .8:
        xlim = (0, int(nodes_99))
    else:
        xlim = (0, int(nodes_max))
    plot(df_fn_hist,
         xlabel='nodes per facet',
         ylabel='probability',
         figname='nodes_per_facet',
         xlim=xlim)

    logger.info("Generating distribution of nodes per facet")
    df_fn_dist_cumsum = df_fn_hist.cumsum()
    plot(df_fn_dist_cumsum,
         xlabel='nodes per facet',
         ylabel='normalised cumulative sum',
         figname='nodes_per_facet_cumsum',
         drawstyle="steps-post",
         markers=False,
         xlim=(0, None),
         ylim=(0, 1)
         )
