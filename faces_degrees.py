"""Computes q-faces and associated degrees"""

import os
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from configparser import ConfigParser
from itertools import combinations
from time import time
from typing import List, Set

from psycopg2.extras import execute_values
from scipy.special import comb
from tqdm import tqdm

from database import get_datasets_names_from_db
from database.instance import db
from database.list_to_pg_array import list_to_pg_arr
from logger import logger

config = ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), './config.ini'))


def prepare_dataset(dataset: str) -> None:
    """Prepares the DB for inserting q-faces"""
    dirname: str = os.path.abspath('./sql/faces')
    db.execute_queries_from_path(os.path.join(
        dirname, '00_functions.sql'), [dataset])

    logger.info("%s: db %s ready for q-faces computation",
                dataset, config['SimplicialDB']['dbname'])


def create_q_faces(dataset, q: int, reset=False, only_distinct_faces=False, batch_size: int = 1000):
    """Creates the q faces"""
    nodes_table: str = 'dnodes' if only_distinct_faces else 'nodes'

    logger.info("%s: Computing %d-faces...", dataset, q)

    if not reset and db.execute_queries(f'''SELECT to_regclass('"{dataset}".q{q}_faces');''', return_rows=True)[0][0] and \
            len(db.execute_queries(f'''SELECT maximal_degree FROM "{dataset}".q{q}_faces LIMIT 1;''', return_rows=True)) > 0:
        logger.info(
            '%s: Already (previously) processed. Doing nothing.', dataset)
        return

    if q == 0:
        start = time()
        db.execute_queries_from_path('./sql/faces/01_q0_faces.sql', [dataset])
        db.execute_queries(f'INSERT INTO "{dataset}".q0_faces (face, weight) ' +
                           f'SELECT array[id], 1 FROM "{dataset}".{nodes_table}')
        end = time()
        logger.info('%s: Done in %s seconds', dataset, f'{(end - start):.1f}')

        return

    db.execute_queries_from_path('./sql/faces/02_q_faces.sql', [dataset, q])
    facets = db.execute_queries(
        f'SELECT * FROM "{dataset}".facets', dict_cursor=True, return_rows=True)
    db.connect()
    cursor = db.connection.cursor()
    insert_query = f'INSERT INTO "{dataset}".q{q}_faces (face, weight) VALUES %s ON CONFLICT DO NOTHING'

    q_key: str = 'dq' if only_distinct_faces else 'q'
    node_ids_key: str = 'dnode_ids' if only_distinct_faces else 'node_ids'

    gen = (int(facet[q_key]) for facet in facets if facet[q_key] >= q)
    total = int(sum([comb(facet_q + 1, q + 1) for facet_q in gen]))
    if total > int(config['SimplicialDB']['max_qfaces']):
        logger.warning(
            "%d %d-faces greater than max allowed (%s) -> NOT COMPUTING",
            total, q, config['SimplicialDB']['max_qfaces'])
        cursor.close()
        return

    logger.info(
        "%s: Inserting %d-faces on database %s:", dataset, q, config['SimplicialDB']['dbname'])
    with tqdm(total=total, ncols=80) as pbar:
        gen = (facet[node_ids_key] for facet in facets if facet['q'] >= q)
        j: int = 0
        query_values: Set = set()
        page_size = batch_size + 1 if batch_size > 100 else 100
        for facet_node_ids in gen:
            for face in combinations(facet_node_ids, q + 1):
                pg_face_arr = list_to_pg_arr(sorted(face))
                if only_distinct_faces:  # THIS IS TOO SLOW!!!! Must be redesigned!!
                    count = db.execute_queries(
                        f'''SELECT count(DISTINCT unnest) FROM (
                        SELECT unnest(node_ids) FROM "{dataset}".dnodes WHERE id = ANY('{pg_face_arr}')
                        )t''',
                        return_rows=True)[0][0]
                    weight = comb(int(count), q + 1)
                else:
                    weight = 1
                query_values.add((pg_face_arr, weight))
                j += 1
                if j == batch_size:
                    execute_values(cursor, insert_query,
                                   query_values, page_size=page_size)
                    j = 0
                    query_values.clear()
                    pbar.update(batch_size)
        if j > 0:
            execute_values(cursor, insert_query,
                           query_values, page_size=page_size)
            pbar.update(j)
    cursor.close()


def compute_q_faces_degrees(dataset: str, q: int):
    """Computes q-faces degrees"""
    logger.info('%s: Computing %d-faces'' degrees', dataset, q)
    try:
        if db.execute_queries(f'''SELECT maximal_degree FROM "{dataset}".q{q}_faces LIMIT 1''', return_rows=True)[0][0]:
            logger.info(
                '%s: Already (previously) processed. Doing nothing.', dataset)
            return
    except IndexError:
        logger.info(
            '%s: Not processing (previously discarded for exceeding max_qfaces.', dataset)
        return
    db.vacuum(f'ANALYZE "{dataset}".q{q}_faces')
    start = time()
    if q == 0:
        db.execute_queries_from_path(
            './sql/faces/03_q0_faces_degrees.sql', [dataset])
    else:
        db.execute_queries_from_path(
            './sql/faces/04_q_faces_degrees.sql', [dataset, q])
    end = time()
    logger.info('%s: Done in %s seconds', dataset, f'{(end - start):.1f}')
    db.vacuum(f'FULL "{dataset}".q{q}_faces')


def get_facets_median_q(dataset: str) -> int:
    """return the median dimension q of the facets"""
    query = f'SELECT cast(percentile_disc(0.5) WITHIN GROUP (ORDER BY q) AS int) FROM "{dataset}".facets'
    median: int = db.execute_queries([query], return_rows=True)[0][0]
    return median


def get_facets_most_frequent_q(dataset: str) -> int:
    """returns the most frequent value of q"""
    query = f'SELECT cast(mode() WITHIN GROUP (ORDER BY q) AS int) FROM "{dataset}".facets'
    val: int = db.execute_queries([query], return_rows=True)[0][0]
    return val


def main(datasets: List[str] = None, q_list: List[int] = None, q_auto: bool = False,
         reset: bool = False, only_distinct_faces=False):
    """The main method"""
    if not datasets:
        datasets = get_datasets_names_from_db()
    print(datasets)
    db.connect()

    for dataset in datasets:
        prepare_dataset(dataset)
        if q_auto:
            median: int = get_facets_median_q(dataset)
            if median > 6:
                logger.info(
                    'computed median of q is too big: %d! Assuming median=6', median)
                median = 6
            most_frequent_q: int = get_facets_most_frequent_q(dataset)
            q_list = sorted({0, 1, most_frequent_q, median})
            logger.info(
                '%s: q-auto selected [0, 1, facet_most_frequent_q, facet_median_q] = %s',
                dataset, str(q_list))
        if q_list:
            for q in q_list:
                create_q_faces(dataset, q=q, reset=reset,
                               only_distinct_faces=only_distinct_faces)
                compute_q_faces_degrees(dataset, q=q)

    db.disconnect()


if __name__ == "__main__":
    # execute only if run as a script

    db_datasets = get_datasets_names_from_db()

    parser: ArgumentParser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter, description=f'''Compute q-faces and their associated degrees (classical, maximal, maximal_u, weighted, weighted_u).

Available datasets:
{str(db_datasets)[1:-1].replace(', ', ',')}''')
    parser.add_argument("-d",
                        "--datasets",
                        help=f"a dataset or a comma-separated list of datasets to load. Available datasets: {db_datasets}")
    q_group = parser.add_mutually_exclusive_group()
    q_group.add_argument("-q",
                         help="compute q-faces, with Q a comma separated list of q (int)")
    q_group.add_argument("-qa",
                         "--q-auto",
                         action="store_true",
                         help="compute q-faces for q=0, q=1 (classical node degree), and the median and the most probable values of q")
    parser.add_argument("--distinct-nodes",
                        help="compute only faces made up of distinct nodes",
                        action="store_true")
    parser.add_argument("-f",
                        "--force",
                        action="store_true",
                        help="force recomputing of all tables")

    args = parser.parse_args()

    dsets: List[str] = args.datasets.split(',') if args.datasets else None
    qs: List[int] = [int(q) for q in args.q.split(
        ',')] if not args.q_auto and args.q else None
    resetFaces: bool = True if args.force else False
    distinct_faces: bool = True if args.distinct_nodes else False

    main(dsets, qs, q_auto=args.q_auto, reset=resetFaces,
         only_distinct_faces=distinct_faces)
