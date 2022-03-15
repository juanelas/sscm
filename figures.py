"""Generates figures from csv datasets already generated with stats.py"""

from plots.datasets_stats import datasets_stats
from plots.degrees_stats import degrees_stats

if __name__ == '__main__':
    datasets_stats()
    degrees_stats()
