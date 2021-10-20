#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 15 13:04:03 2019

@author: juan
"""
import os
from logger import logger
from argparse import ArgumentParser
from configparser import ConfigParser
from time import time
from typing import List

from database import get_datasets_names_from_db
from database.instance import db


config = ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))


def process_dataset(dataset: str, reset=False) -> None:
    if reset:
        db.execute_queries_from_path('./sql/facets/reset.sql', [dataset])

    db.vacuum(f'ANALYZE "{dataset}".simplices')
    logger.info(f'{dataset}: Computing unique simplices from input simplices...')
    if not db.execute_queries(f'''SELECT to_regclass('"{dataset}".usimplices');''', return_rows=True)[0][0]:
        start = time()
        db.execute_queries_from_path('./sql/facets/00_usimplices.sql', [dataset])
        end = time()
        logger.info(f'{dataset}: Done in {(end - start):.1f} seconds')
        db.vacuum(f'ANALYZE "{dataset}".usimplices')
    else:
        logger.info(f'{dataset}: Already (previously) processed. Doing nothing.')

    logger.info(f'{dataset}: Computing usimplices-nodes bidirectional relationship...')
    if not db.execute_queries(f'''SELECT to_regclass('"{dataset}".nodes');''', return_rows=True)[0][0]:
        start = time()
        db.execute_queries_from_path('./sql/facets/01_usimplices_nodes.sql', [dataset])
        end = time()
        logger.info(f'{dataset}: Done in {(end - start):.1f} seconds')
    else:
        logger.info(f'{dataset}: Already (previously) processed. Doing nothing.')

    logger.info(f'{dataset}: Computing distinct nodes (dnodes)...')
    if not db.execute_queries(f'''SELECT to_regclass('"{dataset}".dnodes');''', return_rows=True)[0][0]:
        start = time()
        db.execute_queries_from_path('./sql/facets/02_dnodes.sql', [dataset])
        end = time()
        logger.info(f'{dataset}: Done in {(end - start):.1f} seconds')
        db.vacuum(f'ANALYZE "{dataset}".usimplices')
    else:
        logger.info(f'{dataset}: Already (previously) processed. Doing nothing.')

    logger.info(f'{dataset}: Computing facets...')
    if not db.execute_queries(f'''SELECT to_regclass('"{dataset}".facets');''', return_rows=True)[0][0]:
        start = time()
        db.execute_queries_from_path('./sql/facets/03_facets.sql', [dataset])
        end = time()
        logger.info(f'{dataset}: Done in {(end - start):.1f} seconds')
    else:
        logger.info(f'{dataset}: Already (previously) processed. Doing nothing.')

    logger.info(f'{dataset}: Computing facets-nodes bidirectional relationship...')
    if not db.execute_queries(f'''SELECT to_regclass('"{dataset}".facets_nodes');''', return_rows=True)[0][0]:
        start = time()
        db.execute_queries_from_path('./sql/facets/04_facets_nodes.sql', [dataset])
        end = time()
        logger.info(f'{dataset}: Done in {(end - start):.1f} seconds')
        db.vacuum(f'ANALYSE "{dataset}".nodes')
        db.vacuum(f'ANALYSE "{dataset}".dnodes')
    else:
        logger.info(f'{dataset}: Already (previously) processed. Doing nothing.')


def main(datasets: List[str] = None, reset: bool = False):
    db.connect()
    db.execute_queries_from_path('./sql/facets/common.sql', [])
    if not datasets:
        datasets = get_datasets_names_from_db()

    for dataset in datasets:
        try:
            logger.info(f"Processing simplices for dataset {dataset}")
            process_dataset(dataset, reset)
        except ValueError as error:
            logger.error(error)
    db.disconnect()
    logger.info("All done!")


if __name__ == "__main__":
    # execute only if run as a script

    parser: ArgumentParser = ArgumentParser(description='Compute facets from simplices')
    parser.add_argument("-d",
                        "--datasets",
                        help="a dataset or a comma-separated list of datasets to load")
    parser.add_argument("-f",
                        "--force",
                        help="force recomputing of all tables",
                        action="store_true")

    args = parser.parse_args()

    if args.datasets:
        dsets = args.datasets.split(',')
    else:
        dsets = None

    resetFacets: bool = False
    if args.force:
        resetFacets: bool = True

    main(dsets, resetFacets)
