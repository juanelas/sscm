#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 15 13:04:03 2019

@author: juan
"""
import os
from argparse import ArgumentParser
from configparser import ConfigParser
import sys
from time import time
from typing import List

from database import get_datasets_names_from_db
from database.instance import db
from logger import logger

config = ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))


def process_dataset(dataset: str, reset=False) -> None:
    """Computes usimplices, dnodes, and facaet for a given dataset"""
    if reset:
        db.execute_queries_from_path('./sql/facets/reset.sql', [dataset])

    db.vacuum(f'ANALYZE "{dataset}".simplices')
    logger.info(
        '%s: Computing unique simplices from input simplices...', dataset)
    if not db.execute_queries(f'''SELECT to_regclass('"{dataset}".usimplices');''',
                              return_rows=True)[0][0]:
        start = time()
        db.execute_queries_from_path(
            './sql/facets/00_usimplices.sql', [dataset])
        end = time()
        logger.info('%s: Done in %s seconds', dataset, f'{(end - start):.1f}')
        db.vacuum(f'ANALYZE "{dataset}".usimplices')
    else:
        logger.info('%s: Already (previously) processed. Doing nothing.', dataset)

    logger.info('%s: Computing usimplices-nodes bidirectional relationship...', dataset)
    if not db.execute_queries(f'''SELECT to_regclass('"{dataset}".nodes');''',
                              return_rows=True)[0][0]:
        start = time()
        db.execute_queries_from_path(
            './sql/facets/01_usimplices_nodes.sql', [dataset])
        end = time()
        logger.info('%s: Done in %s seconds', dataset, f'{(end - start):.1f}')
    else:
        logger.info('%s: Already (previously) processed. Doing nothing.', dataset)

    logger.info('%s: Computing facets...', dataset)
    if not db.execute_queries(f'''SELECT to_regclass('"{dataset}".facets');''',
                              return_rows=True)[0][0]:
        start = time()
        db.execute_queries_from_path('./sql/facets/02_facets.sql', [dataset])
        end = time()
        logger.info('%s: Done in %s seconds', dataset, f'{(end - start):.1f}')
    else:
        logger.info('%s: Already (previously) processed. Doing nothing.', dataset)

    logger.info('%s: Computing distinct nodes (dnodes)...', dataset)
    if not db.execute_queries(f'''SELECT to_regclass('"{dataset}".dnodes');''',
                              return_rows=True)[0][0]:
        start = time()
        db.execute_queries_from_path('./sql/facets/03_dnodes.sql', [dataset])
        end = time()
        logger.info('%s: Done in %s seconds', dataset, f'{(end - start):.1f}')
        db.vacuum(f'ANALYSE "{dataset}".nodes')
        db.vacuum(f'ANALYSE "{dataset}".dnodes')
    else:
        logger.info('%s: Already (previously) processed. Doing nothing.', dataset)

    # logger.info(f'{dataset}: Computing facets-nodes bidirectional relationship...')
    # if not db.execute_queries(f'''SELECT to_regclass('"{dataset}".facets_nodes');''',
    #                           return_rows=True)[0][0]:
    #     start = time()
    #     db.execute_queries_from_path('./sql/facets/04_facets_nodes.sql', [dataset])
    #     end = time()
    #     logger.info('%s: Done in %s seconds', dataset, f'{(end - start):.1f}')
    #     db.vacuum(f'ANALYSE "{dataset}".nodes')
    #     db.vacuum(f'ANALYSE "{dataset}".dnodes')
    # else:
    #     logger.info('%s: Already (previously) processed. Doing nothing.', dataset)


def main(datasets: List[str] = None, reset: bool = False):
    """The main method"""
    db.connect()

    db.execute_queries_from_path('./sql/facets/common.sql', [])
    if not datasets:
        datasets = get_datasets_names_from_db()

    print(datasets)

    for dataset in datasets:
        try:
            logger.info("Processing simplices for dataset %s", dataset)
            process_dataset(dataset, reset)
        except ValueError as error:
            logger.error(error)
    db.vacuum("FULL")
    db.disconnect()
    logger.info("All done!")


if __name__ == "__main__":
    # execute only if run as a script

    parser: ArgumentParser = ArgumentParser(
        description='Compute facets from simplices')
    parser.add_argument("-d",
                        "--datasets",
                        help="a dataset or a comma-separated list of datasets to load")
    parser.add_argument("-f",
                        "--force",
                        help="force recomputing of all tables",
                        action="store_true")
    parser.add_argument("-l",
                        "--listdatasets",
                        help="do nothing but get the list available datasets to load from db",
                        action="store_true")

    args = parser.parse_args()

    if args.listdatasets:
        print(",".join(get_datasets_names_from_db()))
        sys.exit()

    dsets: List[str] = args.datasets.split(',') if args.datasets else None

    resetFacets: bool = True if args.force else False

    main(dsets, resetFacets)
