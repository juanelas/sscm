"""Statatistics about datasets and computed degrees"""

import os
from configparser import ConfigParser
from typing import Dict, List

import numpy as np

from database import get_datasets_names_from_db
from database.instance import db
from database.list_to_pg_array import list_to_pg_arr
from directories import stats_dir
from logger import logger

config = ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))


def datasets_stats(datasets=None):
    """Creates materialized view dataset_stats on the DB holding dataset's statistics"""

    logger.info("Creating materialized view datasets_stats...")
    if not datasets:
        datasets = get_datasets_names_from_db('facets')

    # print(datasets)

    with open('./sql/stats/dataset_stats.sql', encoding='utf-8') as file:
        stats_query: str = file.read()

    datasets_query: str = '\nUNION ALL\n'.join([stats_query.format(dataset) for dataset in datasets]) + \
                          ' ORDER BY dataset'

    queries: List[str] = [
        'DROP MATERIALIZED VIEW IF EXISTS datasets_stats',
        f'CREATE MATERIALIZED VIEW datasets_stats AS {datasets_query}',
        f'''COPY (SELECT * FROM datasets_stats) TO '{os.path.join(stats_dir, "datasets_stats.csv")}'
        WITH (FORMAT CSV, DELIMITER ';', HEADER);'''
    ]

    db.execute_queries(queries)
    logger.info("Done")


def export_distribution_to_csv(dataset, tablename, columnname):
    """Exports distribution of a fiven dataset, table and column to a csv file"""

    logger.info("%s: Exporting distribution of %s to csv", dataset, tablename)
    query = f'SELECT {columnname}, count({columnname}) FROM "{dataset}".{tablename} ' + \
            f'GROUP BY {columnname} ORDER BY {columnname}'
    db.execute_queries(
        f'''COPY ({query})
        TO '{os.path.join(stats_dir, f'{dataset}_{tablename}_{columnname}_dist.csv')}'
        WITH (FORMAT CSV, DELIMITER ';', HEADER)''')
    logger.info('%s: Done', dataset)


def export_degrees_to_csv(dataset: str, q: int):
    """Exports computed degrees hists to csv files"""

    logger.info(
        "%s: Exporting distribution of degrees for %d-simplices to csv", dataset, q)

    degrees = get_dataset_degrees(dataset)

    table_name = f'q{q}_faces'
    column_names = [degree[0] for degree in degrees["q_degrees"]]
    if q == 0:
        column_names += [degree[0] for degree in degrees["q0_extra_degrees"]]

    for column_name in column_names:
        query = f'''
            SELECT 
                {column_name} AS degree,
                sum(weight) AS count
            FROM "{dataset}".{table_name}
            GROUP BY {column_name}
            ORDER BY {column_name}'''
        row = db.execute_queries(
            f'SELECT {column_name} FROM "{dataset}".{table_name} LIMIT 1', return_rows=True)
        if len(row) > 0 and row[0][0] is not None:
            db.execute_queries(f"COPY ({query}) TO '" +
                               os.path.join(stats_dir,
                                            f"{dataset}_{table_name}_{column_name}_dist.csv") +
                               "' WITH (FORMAT CSV, DELIMITER ';', HEADER);")
    logger.info("%s: Done", dataset)


def degrees_sql(dataset: str, q: int, degrees: List[str], percentiles: List[float]) -> str:
    """Returns a prepared SQL query for returning degrees stats for s given dataset and q"""

    # {0} - degree name in db, {1} human readable name of the degree, {2} percentiles
    degree_columns_sql: str = ''',
       min({0})::int                                               AS "{1}: min",
       max({0})::int                                               AS "{1}: max",
       avg({0})::float                                             AS "{1}: avg",
       mode() WITHIN GROUP (ORDER BY {0})                          AS "{1}: most frequent value",
       stddev({0})::float                                          AS "{1}: stddev",
       percentile_disc('{2}'::float[]) WITHIN GROUP (ORDER BY {0}) AS "{1} percentiles {2}"
    '''
    # {0} - dataset, {1} q, {2} degrees_columns
    stats_sql: str = '''SELECT '{0}' AS dataset, {1} AS q {2} FROM "{0}".q{1}_faces'''

    percentiles_str: str = list_to_pg_arr(percentiles)

    degrees_columns_sql: str = ''
    for degree in degrees:
        degrees_columns_sql += degree_columns_sql.format(
            # In the end, we use the degree name as the human-readable name of the degree
            degree[0], degree[0], percentiles_str)

    return stats_sql.format(dataset, q, degrees_columns_sql)


def get_dataset_qs(dataset: str) -> List[int]:
    """Returns the values of q for the computed q-faces"""
    query: str = f'''SELECT substring(tablename FROM 'q#"%#"#_%' FOR '#') ::INTEGER AS q
    FROM pg_catalog.pg_tables
	WHERE tablename LIKE 'q%\_faces' AND schemaname='{dataset}' ORDER BY q'''
    rows = db.execute_queries(query, return_rows=True, dict_cursor=True)
    if len(rows) == 0:
        raise Exception(f'no q-faces for dataset {dataset}')

    nprows = np.array(rows)
    return nprows[:, 0].tolist()


def get_dataset_degrees(dataset: str) -> Dict:
    """Returns the degrees already computed for this dataset"""
    qs: List[int] = get_dataset_qs(dataset)
    q_degrees: List[List[str]] = [
        ['maximal_degree', 'maximal'],
        ['maximal_degree_u', 'maximal upper'],
        ['weighted_maximal_degree', 'weighted maximal']
    ]
    q0_extra_degrees: List[List[str]] = []
    for q in qs:
        q0_extra_degrees.append([f'node_to_qfaces_degree[{q}]', f'node to {q}-faces'])

    return {"q_degrees": q_degrees, "q0_extra_degrees": q0_extra_degrees}


def degrees_stats(percentiles: str = '{.5,.9,.99}', reset=False):
    """Computes statistics wrt the conmputed q-faces"""

    datasets = get_datasets_names_from_db('q0_faces')

    for dataset in datasets:
        qs: List[int] = get_dataset_qs(dataset)
        degrees = get_dataset_degrees(dataset)

        for q in qs:
            qfaces_tablename = f'q{q}_faces'

            logger.info(
                "%s: Generating statistics for %d-faces' degrees", dataset, q)

            queries: List[str] = []

            # {0} dataset; {1} qfaces_table_name; {2} degree
            index_template: str = 'CREATE INDEX IF NOT EXISTS {1}_{2} ON "{0}".{1} ({2});'

            for degree in degrees["q_degrees"]:
                queries.append(index_template.format(
                    dataset, qfaces_tablename, degree[0]))

            if q == 0:
                for degree in degrees["q0_extra_degrees"]:
                    if "[" not in degree[0]:
                        queries.append(index_template.format(dataset, qfaces_tablename, degree[0]))

            db.execute_queries(queries)

            if q == 0:
                query = degrees_sql(
                    dataset, q, degrees["q_degrees"] + degrees["q0_extra_degrees"], percentiles)
            else:
                query = degrees_sql(
                    dataset, q, degrees["q_degrees"], percentiles)

            rows = db.execute_queries(
                "SELECT FROM pg_catalog.pg_tables WHERE tablename = 'degrees_stats'",
                return_rows=True, dict_cursor=True)

            with db.connection.cursor() as cursor:
                if len(rows) > 0:
                    if len(db.execute_queries(
                            f"SELECT dataset FROM degrees_stats WHERE dataset = '{dataset}' AND q = {q}",
                            return_rows=True)) > 0:
                        if reset:
                            cursor.execute(
                                'DELETE FROM degrees_stats WHERE dataset = %s AND q = %s', (dataset, q))
                            cursor.execute(
                                f'INSERT INTO degrees_stats {query}')
                    else:
                        cursor.execute(f'INSERT INTO degrees_stats {query}')
                else:
                    cursor.execute(f'CREATE TABLE degrees_stats AS {query}')

            export_degrees_to_csv(dataset, q)

    db.execute_queries("COPY degrees_stats TO '" + os.path.join(stats_dir, "degrees_stats.csv") +
                       "' WITH (FORMAT CSV, DELIMITER ';', HEADER);")


def main():
    """main method"""
    db.connect()

    datasets_stats()
    for dataset in get_datasets_names_from_db('simplices'):
        export_distribution_to_csv(dataset, 'simplices', 'q')
    for dataset in get_datasets_names_from_db('facets'):
        export_distribution_to_csv(dataset, 'facets', 'q')

    degrees_stats(percentiles='{.5,.75,.9,.99,.999}', reset=True)

    db.disconnect()


if __name__ == '__main__':
    main()
