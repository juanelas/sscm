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
from logger import logger

config = ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), './config.ini'))


def list_to_postgresql_arr(a: List, cast: str = None) -> str:
    ret: str = str(a).replace('[', '{').replace(']', '}')
    if cast:
        ret += f'::{cast}'
    return ret


def prepare_dataset(dataset: str) -> None:
    dirname: str = os.path.abspath('./sql/faces')
    db.execute_queries_from_path(os.path.join(dirname, '00_functions.sql'), [dataset])

    logger.info(
        f"{dataset}: db {config['SimplicialDB']['dbname']} ready for q-faces computation")


def create_q_faces(dataset, q: int, reset=False, only_distinct_faces=False, batch_size: int = 1000):
    nodes_table: str = 'dnodes' if only_distinct_faces else 'nodes'

    logger.info(f"{dataset}: Computing {q}-faces...")

    if not reset and db.execute_queries(f'''SELECT to_regclass('"{dataset}".q{q}_faces');''', return_rows=True)[0][0] \
            and len(db.execute_queries(f'''SELECT maximal_degree FROM "{dataset}".q{q}_faces LIMIT 1;''',
                                       return_rows=True)) > 0:
        logger.info(f'{dataset}: Already (previously) processed. Doing nothing.')
        return

    if q is 0:
        start = time()
        db.execute_queries_from_path(f'./sql/faces/01_q0_faces.sql', [dataset])
        db.execute_queries(f'INSERT INTO "{dataset}".q0_faces (face, weight) ' +
                           f'SELECT array[id], 1 FROM "{dataset}".{nodes_table}')
        end = time()
        logger.info(f'{dataset}: Done in {(end - start):.1f} seconds')

        return

    db.execute_queries_from_path(f'./sql/faces/02_q_faces.sql', [dataset, q])
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
            f"{total} {q}-faces greater than max allowed ({config['SimplicialDB']['max_qfaces']}) -> NOT COMPUTING")
        cursor.close()
        return

    logger.info(f"{dataset}: Inserting {q}-faces on database {config['SimplicialDB']['dbname']}:")
    with tqdm(total=total, ncols=80) as pbar:
        gen = (facet[node_ids_key] for facet in facets if facet['q'] >= q)
        j: int = 0
        query_values: Set = set()
        page_size = batch_size + 1 if batch_size > 100 else 100
        for facet_node_ids in gen:
            for face in combinations(facet_node_ids, q + 1):
                pg_face_arr = list_to_postgresql_arr(sorted(face))
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
                    execute_values(cursor, insert_query, query_values, page_size=page_size)
                    j = 0
                    query_values.clear()
                    pbar.update(batch_size)
        if j > 0:
            execute_values(cursor, insert_query, query_values, page_size=page_size)
            pbar.update(j)
    cursor.close()


def compute_q_faces_degrees(dataset: str, q: int):
    logger.info(f'{dataset}: Computing {q}-faces'' degrees')
    try:
        if db.execute_queries(f'''SELECT maximal_degree FROM "{dataset}".q{q}_faces LIMIT 1''', return_rows=True)[0][0]:
            logger.info(f'{dataset}: Already (previously) processed. Doing nothing.')
            return
    except IndexError:
        logger.info(f'{dataset}: Not processing (previously discarded for exceeding max_qfaces.')
        return
    db.vacuum(f'ANALYZE "{dataset}".q{q}_faces')
    start = time()
    if q == 0:
        db.execute_queries_from_path('./sql/faces/03_q0_faces_degrees.sql', [dataset])
    else:
        db.execute_queries_from_path('./sql/faces/04_q_faces_degrees.sql', [dataset, q])
    end = time()
    logger.info(f'{dataset}: Done in {(end - start):.1f} seconds')
    db.vacuum(f'ANALYZE "{dataset}".q{q}_faces')


def get_facets_median_q(dataset: str) -> int:
    query = f'SELECT cast(percentile_disc(0.5) WITHIN GROUP (ORDER BY q) AS int) FROM "{dataset}".facets'
    median: int = db.execute_queries([query], return_rows=True)[0][0]
    return median


def get_facets_most_frequent_q(dataset: str) -> int:
    query = f'SELECT cast(mode() WITHIN GROUP (ORDER BY q) AS int) FROM "{dataset}".facets'
    val: int = db.execute_queries([query], return_rows=True)[0][0]
    return val


def main(datasets: List[str] = None, q_list: List[int] = None, q_auto: bool = False, reset: bool = False,
         only_distinct_faces=False):
    if not datasets:
        datasets = get_datasets_names_from_db()
    print(datasets)
    db.connect()

    for dataset in datasets:
        prepare_dataset(dataset)
        if q_auto:
            median: int = get_facets_median_q(dataset)
            if (median > 6):
                logger.info(f'computed median of q is too big: {median}! Assuming median=6')
                median = 6
            most_frequent_q: int = get_facets_most_frequent_q(dataset)
            q_list = sorted({0, most_frequent_q, median})
            logger.info(
                f'{dataset}: q-auto selected [0, facet_most_frequent_q, facet_median_q] = {q_list}')
        if q_list:
            for q in q_list:
                create_q_faces(dataset, q=q, reset=reset, only_distinct_faces=only_distinct_faces)
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
                         help="compute q-faces for q=0 and the median and the most probable values of q")
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

    main(dsets, qs, q_auto=args.q_auto, reset=resetFaces, only_distinct_faces=distinct_faces)
