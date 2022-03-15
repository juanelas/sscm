"""Plots figures wrt statistics of the different degrees"""
import os
import re
from glob import glob

import pandas as pd
from directories import stats_dir
from logger import logger

from plots import csvfiles_to_df, plot


def classical_and_node_to_qfaces_degree(dataset: str, df_datasets: pd.DataFrame):
    """Statistics of the different degrees of a given dataset"""

    columnnames = []

    csv_file_names = glob(
        f'{stats_dir}/{dataset}_q0_faces_classical_degree_dist.csv')
    columnnames.append('classical node deg.: $k^1$')

    vlines = []
    vlines_value_name = {}  # Value is a 10 decimal precission string of the value

    for filename in sorted(glob(f'{stats_dir}/{dataset}_q0_faces_node_to_qfaces_degree*.csv')):
        q = int(re.match(r'.*(?P<q>\d)', os.path.basename(filename)).group('q'))
        if q > 1:
            csv_file_names.append(filename)
            if q == 2:
                columnnames.append(f'node-to-triangles deg.:  $k^{q}$')
            elif q == 3:
                columnnames.append(f'node-to-tetrahedra deg.:  $k^{q}$')
            else:
                columnnames.append(f'node-to-{q}-faces deg.:  $k^{q}$')

        avg = df_datasets[[
            f'node_to_qfaces_degree[{q}]: avg']].loc[df_datasets['q'] == 0].loc[dataset][0]
        value = f'{avg:.10f}'.rstrip('0').rstrip(
            '.') if '.' in f'{avg:.10f}' else f'{avg:.10f}'
        if value in vlines_value_name:
            vlines_value_name[value] += f' \\langle k^{q} \\rangle = '
        else:
            vlines_value_name[value] = f'$\\langle k^{q} \\rangle = '

        median = int(df_datasets[[f'node_to_qfaces_degree[{q}] percentiles ' +
                                  '{.5,.75,.9,.99,.999}']
                                 ].loc[df_datasets['q'] == 0]
                     .loc[dataset][0][1:-1].split(',')[0])
        value = f'{median:.10f}'.rstrip('0').rstrip(
            '.') if '.' in f'{median:.10f}' else f'{median:.10f}'
        if value in vlines_value_name:
            vlines_value_name[value] = vlines_value_name[value] + f' \\overline{{k^{q}}} = '
        else:
            vlines_value_name[value] = f'$\\overline{{k^{q}}} = '

    for value in vlines_value_name:
        vlines.append([float(value), vlines_value_name[value] +
                       (f'{float(value):.2f}'.rstrip('0').rstrip(
                           '.') if '.' in f'{float(value):.10f}' else f'{float(value):.10f}')
                       + '$'])

    def sorter(e):
        return e[0]

    vlines.sort(key=sorter)

    title: str = f'{dataset}. classical and node-to-qfaces degrees'

    df_degrees_hist = csvfiles_to_df(csv_filenames=csv_file_names, normalise=True,
                                     column_names=columnnames)

    logger.info(
        "%s: Generating degrees distributions (classical node  + node-to-qfaces): loglog", dataset)
    plot(
        df_degrees_hist,
        title=title,
        figsize=[6, 4.5],
        figname=f'{dataset}_classical_and_node_to_qfaces_loglog',
        xlabel='degree',
        ylabel='probability',
        logx=True,
        logy=True,
        legend_loc='upper right',
        subdirectory='degrees',
        linestyles_cycle=['dotted'],
        linewidths_cycle=[.75],
        markers_cycle=['.'],
        vlines=vlines
    )

    logger.info(
        "%s: Generating degrees distributions (classical node  + node-to-qfaces): linear", dataset)
    prob_max_values = df_degrees_hist.max().sort_values()
    prob_max_max = float(prob_max_values.iloc[-1])
    prob_second_max = float(
        prob_max_values.iloc[-2]) if len(prob_max_values) > 1 else 0
    min_threshold = prob_max_max/15
    df_degrees_hist_linear_plot = df_degrees_hist[df_degrees_hist > min_threshold].dropna(
        how='all')
    i = 1e-4
    # while there are nan columns
    while df_degrees_hist_linear_plot.isnull().sum(axis=0).max()\
            == len(df_degrees_hist_linear_plot):
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
        figname=f'{dataset}_classical_and_node_to_qfaces',
        xlabel='degree',
        ylabel='probability',
        xlim=x_lim,
        ylim=y_lim,
        linestyles_cycle=['-'],
        linewidths_cycle=[1],
        markers_cycle=['o'],
        vlines=vlines,
        subdirectory='degrees'
    )
