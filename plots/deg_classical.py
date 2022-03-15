"""Plots figures wrt statistics of the different degrees"""
from glob import glob

from directories import stats_dir
from logger import logger
from plots import csvfiles_to_df, plot


def classical_degree(dataset: str):
    """Statistics of the different degrees of a given dataset"""

    columnnames = []
    csv_file_names = glob(f'{stats_dir}/{dataset}_q0_faces_classical_degree_dist.csv')
    columnnames.append('classical node degree')
    df_degrees_hist = csvfiles_to_df(
        csv_filenames=csv_file_names, normalise=True, column_names=columnnames)

    logger.info(
        "%s: Generating degrees distributions (classical node degree): linear", dataset)
    prob_max_values = df_degrees_hist.max().sort_values()
    prob_max_max = float(prob_max_values.iloc[-1])
    prob_second_max = float(
        prob_max_values.iloc[-2]) if len(prob_max_values) > 1 else 0
    min_threshold = prob_max_max/15
    df_degrees_hist_linear_plot = df_degrees_hist[df_degrees_hist > min_threshold].dropna(
        how='all')
    i = 1e-4
    while df_degrees_hist_linear_plot.isnull().sum(axis=0).max() == len(
            df_degrees_hist_linear_plot):  # while there are nan columns
        df_degrees_hist_linear_plot = df_degrees_hist[df_degrees_hist >
                                                      min_threshold - i].dropna(how='all')
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
