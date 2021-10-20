import os
from itertools import islice, cycle
from typing import List, Tuple, Optional

import matplotlib.pyplot as plt
import numpy as np

from directories import figures_dir


def plot(df,
         figname: str = 'figure',
         xlabel: Optional[str] = None,
         ylabel: Optional[str] = None,
         markers: bool = True,
         drawstyle: str = 'default',
         title: Optional[str] = None,
         linewidths_cycle: Optional[List[float]] = None,
         linestyles_cycle: Optional[List[str]] = None,
         markers_cycle: Optional[List[str]] = None,
         xlim: Optional[Tuple[Optional[int], Optional[int]]] = None,
         ylim: Optional[Tuple[Optional[int], Optional[int]]] = None,
         figsize: Optional[List[int]] = None,
         logx: bool = False,
         logy: bool = False,
         get_figure: bool = False,
         subdirectory: Optional[str] = None,
         legend_loc: str = 'best'
         ):
    if markers_cycle is None:
        markers_cycle = ['o', 'v', '^', '<', '>']
    if linewidths_cycle is None:
        linewidths_cycle = [1]
    if linestyles_cycle is None:
        linestyles_cycle = ['solid', 'dashed', 'dotted']
    if figsize is None:
        figsize = [8, 6]
    plt.rcParams["figure.figsize"] = figsize
    colormap = plt.cm.get_cmap('Accent')
    colors_cycle = colormap(np.linspace(0, 1, 7))
    colors = list(islice(cycle(colors_cycle), len(df.columns)))
    linewidths = list(islice(cycle(linewidths_cycle), len(df.columns)))
    linestyles = list(islice(cycle(linestyles_cycle), len(df.columns)))
    if not markers:
        markers_cycle = [None]
    markers = list(islice(cycle(markers_cycle), len(df.columns)))

    fig, ax = plt.subplots()
    for col, color, lw, ls, marker in zip(df.columns, colors, linewidths, linestyles, markers):
        df_col = df[col].dropna().sort_index()
        df_col.plot(drawstyle=drawstyle, color=tuple(color), lw=lw, ls=ls, marker=marker, ax=ax, logx=logx,
                    logy=logy)
    if xlim:
        ax.set_xlim(xlim)
    if ylim:
        ax.set_ylim(ylim)
    if title:
        ax.set_title(title)
    ax.grid()
    ax.legend(loc=legend_loc)
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)

    if subdirectory:
        degree_figures_dir = os.path.join(figures_dir, 'degrees')
        if not os.path.exists(degree_figures_dir):
            os.makedirs(degree_figures_dir)
        fig.savefig(os.path.join(degree_figures_dir, f'{figname}.pdf'))
    else:
        fig.savefig(os.path.join(figures_dir, f'{figname}.pdf'))

    if get_figure:
        return fig
    else:
        plt.close(fig)
