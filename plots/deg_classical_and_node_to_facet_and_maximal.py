"""Plots figures wrt statistics of the different degrees"""
import os
import re
from glob import glob

import pandas as pd
from directories import stats_dir
from logger import logger

from plots import csvfiles_to_df, plot


def classical_and_node_to_facets_and_maximal_degree(dataset: str, df_datasets: pd.DataFrame):
    """Statistics of the different degrees of a given dataset"""

    columnnames = []

    # median of q
    q_m = int(df_datasets['nodes per facet: median']) - 1

    # most frequent value of q
    q_p = int(df_datasets['nodes per facet: most frequent value']) - 1

    csv_file_names = [
        f'{stats_dir}/{dataset}_q0_faces_node_to_qfaces_degree[1]_dist.csv']
    columnnames.append('classical node deg.: $k$')

    i: int = 0
    # q_p = None  # most probable q
    # q_m = None  # median q
    for filename in sorted(glob(f'{stats_dir}/{dataset}_q*_faces_maximal_degree_u_dist.csv')):
        q = int(re.match(r'.*_q(?P<q>\d+)_faces',
                os.path.basename(filename)).group('q'))

        csv_file_names.append(filename)
        if q == 0:
            columnnames.append('node-to-facets deg.:  $k^F$')
        else:
            columnnames.append(
                f'max. up. simp. deg. ${q}$-simplices:  $k_U^*({q})$')

    title: str = f'{dataset}. '
    if q_p == q_m:
        title += f'$q_m = q_p = {q_p}$'
    else:
        title += f'$q_m = {q_m}$, $q_p = {q_p}$'

    for filename in sorted(glob(f'{stats_dir}/{dataset}_q*_faces_maximal_degree_dist.csv')):
        q = int(re.match(r'.*_q(?P<q>\d+)_faces',
                os.path.basename(filename)).group('q'))

        if q > 0:
            columnnames.append(
                f'max. simp. deg. ${q}$-simplices:  $k^*({q})$')
            csv_file_names.append(filename)

    df_degrees_hist = csvfiles_to_df(csv_filenames=csv_file_names, normalise=True,
                                     column_names=columnnames)

    logger.info(
        "%s: Generating degrees distributions (classical node + node to facet + maximal simplicial): loglog",
        dataset)
    plot(
        df_degrees_hist,
        title=title,
        figsize=[6, 4.5],
        figname=f'{dataset}_classical_and_node_to_facet_and_maximal_loglog',
        xlabel='degree',
        ylabel='probability',
        logx=True,
        logy=True,
        legend_loc='upper right',
        subdirectory='degrees',
        linestyles_cycle=['dotted'],
        linewidths_cycle=[.75],
        markers_cycle=['.']
    )

    logger.info(
        "%s: Generating degrees distributions (classical node + node to facet + maximal simplicial): linear",
        dataset)
    prob_max_values = df_degrees_hist.max().sort_values()
    prob_max_max = float(prob_max_values.iloc[-1])
    prob_second_max = float(
        prob_max_values.iloc[-2]) if len(prob_max_values) > 1 else 0
    min_threshold = prob_max_max/15
    df_degrees_hist_linear_plot = df_degrees_hist[df_degrees_hist > min_threshold].dropna(
        how='all')
    i = 1e-4
    while df_degrees_hist_linear_plot.isnull().sum(axis=0).max() == \
            len(df_degrees_hist_linear_plot):  # while there are nan columns
        df_degrees_hist_linear_plot = df_degrees_hist[df_degrees_hist >
                                                      min_threshold - i].dropna(how='all')
        i += 1e-4
    x_lim = (0, len(df_degrees_hist_linear_plot))
    y_lim = (0, None)
    if 0 < prob_second_max < prob_max_max / 3:
        y_lim = (0, 2 * prob_second_max)
    plot(
        df_degrees_hist,
        title=title,
        figname=f'{dataset}_classical_and_node_to_facet_and_maximal',
        xlabel='degree',
        ylabel='probability',
        xlim=x_lim,
        ylim=y_lim,
        linestyles_cycle=['-'],
        linewidths_cycle=[1],
        markers_cycle=['o'],
        subdirectory='degrees'
    )
