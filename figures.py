import os
from configparser import ConfigParser
from glob import glob
from typing import List, Optional

import pandas as pd

from directories import stats_dir
from logger import logger
from plots import plot

config = ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))


def csvfiles_to_df(csv_filenames: List, column_names: Optional[List] = None,
                   column_key_increment: int = 0, normalise: bool = False):
    if len(csv_filenames) == 0:
        return
    i: int = 0
    df_hist = None
    for csv_filename in csv_filenames:
        df = pd.read_csv(csv_filename, sep=';')
        column_key = df.columns[0]
        df = df.sort_values(column_key)
        df[column_key] = df[column_key] + column_key_increment
        df = df.set_index(column_key)
        if normalise:
            df = df / int(df.sum())  # Normalise
        if i == 0:
            df_hist = df
        else:
            df_hist = pd.merge(df_hist, df, how='outer', on=column_key)
        i += 1
    if not column_names:
        column_names = [os.path.splitext(os.path.basename(filename))[0] for filename in csv_filenames]
    df_hist.columns = column_names
    return df_hist


if __name__ == '__main__':
    df_datasets_stats = pd.read_csv(glob(f'{stats_dir}/datasets_stats.csv')[0], sep=';')
    df_datasets_stats = df_datasets_stats.set_index('dataset')
    df_degrees_stats = pd.read_csv(glob(f'{stats_dir}/degrees_stats.csv')[0], sep=';').dropna(subset=['maximal: max'])
    df_degrees_stats = df_degrees_stats.set_index('dataset')

    logger.info("Generating histogram of nodes per simplex")
    csv_file_names = glob(f'{stats_dir}/*_simplices_q_dist.csv')
    datasets = []
    [datasets.append(os.path.split(filename)[1].split('_')[0]) for filename in csv_file_names]
    df_sn_hist = csvfiles_to_df(csv_filenames=csv_file_names, column_names=datasets, column_key_increment=1,
                                normalise=True)
    nodes_max = float(df_datasets_stats.loc[:, 'nodes per simplex: max'].max())
    nodes_99 = float(df_datasets_stats.loc[:, 'nodes per simplex: percentile 99'].max())
    if nodes_99 / nodes_max < .8:
        xlim = (0, int(nodes_99))
    else:
        xlim = (0, int(nodes_max))
    fig_sn = plot(df_sn_hist,
                  xlabel='nodes per simplex',
                  ylabel='probability',
                  figname='nodes_per_simplex',
                  xlim=xlim)

    logger.info("Generating distribution of nodes per simplex")
    df_sn_dist_cumsum = df_sn_hist.cumsum()
    fig_sn_cumsum = plot(df_sn_dist_cumsum,
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
    [datasets.append(os.path.split(filename)[1].split('_')[0]) for filename in csv_file_names]
    df_fn_hist = csvfiles_to_df(csv_filenames=csv_file_names, column_names=datasets, column_key_increment=1,
                                normalise=True)
    nodes_max = float(df_datasets_stats.loc[:, 'nodes per facet: max'].max())
    nodes_99 = float(df_datasets_stats.loc[:, 'nodes per facet: percentile 99'].max())
    if nodes_99 / nodes_max < .8:
        xlim = (0, int(nodes_99))
    else:
        xlim = (0, int(nodes_max))
    fig_fn = plot(df_fn_hist,
                  xlabel='nodes per facet',
                  ylabel='probability',
                  figname='nodes_per_facet',
                  xlim=xlim)

    logger.info("Generating distribution of nodes per simplex")
    df_fn_dist_cumsum = df_fn_hist.cumsum()
    fig_fn_cumsum = plot(df_fn_dist_cumsum,
                         xlabel='nodes per facet',
                         ylabel='normalised cumulative sum',
                         figname='nodes_per_facet_cumsum',
                         drawstyle="steps-post",
                         markers=False,
                         xlim=(0, None),
                         ylim=(0, 1)
                         )

    csv_file_names = glob(f'{stats_dir}/*_q0_faces*.csv')
    datasets = df_degrees_stats.index.unique()

    for dataset in datasets:
        columnnames = []
        csv_file_names = glob(f'{stats_dir}/{dataset}_q0_faces_classical_degree_dist.csv')
        columnnames.append(f'classical node degree')
        df_degrees_hist = csvfiles_to_df(csv_filenames=csv_file_names, normalise=True, column_names=columnnames)

        logger.info(f"{dataset}:Generating degrees distributions (classical node degree): linear")
        prob_max_values = df_degrees_hist.max().sort_values()
        prob_max_max = float(prob_max_values.iloc[-1])
        prob_second_max = float(prob_max_values.iloc[-2]) if len(prob_max_values) > 1 else 0
        min_threshold = prob_max_max/15
        df_degrees_hist_linear_plot = df_degrees_hist[df_degrees_hist > min_threshold].dropna(how='all')
        i = 1e-4
        while df_degrees_hist_linear_plot.isnull().sum(axis=0).max() == len(
                df_degrees_hist_linear_plot):  # while there are nan columns
            df_degrees_hist_linear_plot = df_degrees_hist[df_degrees_hist > min_threshold - i].dropna(how='all')
            i += 1e-4
        x_lim = (0, len(df_degrees_hist_linear_plot))
        y_lim = (0, None)
        if 0 < prob_second_max < prob_max_max / 3:
            y_lim = (0, prob_second_max)
        plot(
            df_degrees_hist,
            title=dataset,
            figname=f'{dataset}_classical_node_degree',
            xlabel='degree',
            ylabel='probability',
            xlim=x_lim,
            ylim=y_lim,
            linestyles_cycle=['-'],
            linewidths_cycle=[1],
            markers_cycle=['o'],
            subdirectory='degrees'
        )

        columnnames = []
        csv_file_names = glob(f'{stats_dir}/{dataset}_q0_faces_classical_degree_dist.csv')
        columnnames.append(f'classical node deg.: $k$')
        i : int = 0
        q_p = None  # most probable q
        q_m = None  # median q
        for filename in sorted(glob(f'{stats_dir}/{dataset}_q*_faces_maximal_degree_u_dist.csv')):
            aux: List = os.path.splitext(os.path.basename(filename))[0].split('_')
            q = int(aux[1][1])
            # columnnames.append(f'maximal simplicial upper degree: {q}-simplices')
            if q == 0:
                columnnames.append(f'node-to-facets deg.:  $k^F$')
            else:
                if not q_m:
                    q_m = q
                    q_p = q
                else:
                    if q >= q_m:
                        q_p = q
                    else:
                        q_p = q_m
                        q_m = q

                csv_file_names.append(filename)
                columnnames.append(f'max. up. simp. deg. ${q}$-simplices:  $k_U^*({q})$')

        title : str = f'{dataset}. '
        if q_p == q_m:
            title += f'$q_m = q_p = {q_p}$'
        else:
            title += f'$q_m = {q_m}$, $q_p = {q_p}$'

        for filename in sorted(glob(f'{stats_dir}/{dataset}_q*_faces_maximal_degree_dist.csv')):
            aux: List = os.path.splitext(os.path.basename(filename))[0].split('_')
            q = int(aux[1][1])
            csv_file_names.append(filename)
            # columnnames.append(f'maximal simplicial degree: {aux[1][1]}-simplices')
            if q > 0:
                columnnames.append(f'max. simp. deg. ${q}$-simplices:  $k^*({q})$')

        df_degrees_hist = csvfiles_to_df(csv_filenames=csv_file_names, normalise=True,
                                         column_names=columnnames)

        logger.info(f"{dataset}:Generating degrees distributions (classical node + maximal simplicial): loglog")
        plot(
            df_degrees_hist,
            title=title,
            figsize=[6, 4.5],
            figname=f'{dataset}_degrees_loglog',
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

        logger.info(f"{dataset}:Generating degrees distributions (classical node + maximal simplicial): linear")
        prob_max_values = df_degrees_hist.max().sort_values()
        prob_max_max = float(prob_max_values.iloc[-1])
        prob_second_max = float(prob_max_values.iloc[-2]) if len(prob_max_values) > 1 else 0
        df_degrees_hist_linear_plot = df_degrees_hist[df_degrees_hist > min_threshold].dropna(how='all')
        i = 1e-4
        while df_degrees_hist_linear_plot.isnull().sum(axis=0).max() == len(df_degrees_hist_linear_plot):  # while there are nan columns
            df_degrees_hist_linear_plot = df_degrees_hist[df_degrees_hist > min_threshold - i].dropna(how='all')
            i += 1e-4
        x_lim = (0, len(df_degrees_hist_linear_plot))
        y_lim = (0, None)
        if 0 < prob_second_max < prob_max_max / 3:
            y_lim = (0, 2 * prob_second_max)
        plot(
            df_degrees_hist,
            title=title,
            figname=f'{dataset}_degrees',
            xlabel='degree',
            ylabel='probability',
            xlim=x_lim,
            ylim=y_lim,
            linestyles_cycle=['-'],
            linewidths_cycle=[1],
            markers_cycle=['o'],
            subdirectory='degrees'
        )

        logger.info(f"{dataset}: Done!")
