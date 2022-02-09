import os
from configparser import ConfigParser

from database import get_datasets_names_from_db
from database.instance import db
from directories import stats_dir
from logger import logger

config = ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))


def datasets_stats(datasets=None):
    logger.info("Creating materialized view datasets_stats...")
    if not datasets:
        datasets = get_datasets_names_from_db('facets')

    print(datasets)
    
    with open('./sql/stats/dataset_stats.sql') as f:
        stats_query: str = f.read()

    datasets_query: str = '\nUNION ALL\n'.join([stats_query.format(dataset) for dataset in datasets]) + \
                          ' ORDER BY dataset'

    db.execute_queries([
        'DROP MATERIALIZED VIEW IF EXISTS datasets_stats',
        f'CREATE MATERIALIZED VIEW datasets_stats AS {datasets_query}',
        f'''COPY (SELECT * FROM datasets_stats) TO '{os.path.join(stats_dir, "datasets_stats.csv")}' ''' +
        f"WITH (FORMAT CSV, DELIMITER ';', HEADER);"
    ])
    logger.info("Done")


def export_distribution_to_csv(dataset, tablename, columnname):
    logger.info(f"{dataset}: Exporting distribution of {tablename} to csv")
    query = f'SELECT {columnname}, count({columnname}) FROM "{dataset}".{tablename} ' + \
            f'GROUP BY {columnname} ORDER BY {columnname}'
    db.execute_queries(
        f'''COPY ({query}) TO '{os.path.join(stats_dir, f'{dataset}_{tablename}_{columnname}_dist.csv')}'
            WITH (FORMAT CSV, DELIMITER ';', HEADER)''')
    logger.info(f'{dataset}: Done')


def export_degrees_to_csv(dataset: str, q: int):
    logger.info(f"{dataset}: Exporting distribution of degrees for {q}-simplices to csv")
    table_name = f'q{q}_faces'
    # column_names = ['maximal_degree', 'maximal_degree_u', 'weighted_maximal_degree', 'weighted_maximal_degree_u']
    column_names = ['maximal_degree', 'maximal_degree_u', 'weighted_maximal_degree']
    if q == 0:
        column_names.append('classical_degree')

    for column_name in column_names:
        query = f'''
            SELECT 
                {column_name} AS degree,
                sum(weight) AS count
            FROM "{dataset}".{table_name}
            GROUP BY {column_name}
            ORDER BY {column_name}'''
        row = db.execute_queries(f'SELECT {column_name} FROM "{dataset}".{table_name} LIMIT 1', return_rows=True)
        if len(row) > 0 and row[0][0] is not None:
            db.execute_queries(f"COPY ({query}) TO '" +
                               os.path.join(stats_dir, f"{dataset}_{table_name}_{column_name}_dist.csv") +
                               f"' WITH (FORMAT CSV, DELIMITER ';', HEADER);")
    logger.info(f"{dataset}: Done")


def degrees_stats(percentiles: str = '{.5,.9,.99}', reset=False):
    with open('./sql/stats/degrees.sql') as f:
        stats_sql: str = f.read()
    with open('./sql/stats/degrees_q0_faces.sql') as f:
        stats_sql_q0_faces: str = f.read()

    rows = db.execute_queries(
        "SELECT schemaname AS dataset, tablename AS qfaces_tablename FROM pg_catalog.pg_tables " +
        f"WHERE tablename LIKE 'q_\_faces' ORDER BY dataset, qfaces_tablename", return_rows=True, dict_cursor=True)

    if len(rows) == 0:
        return

    for row in rows:
        dataset = row['dataset']
        qfaces_tablename = row['qfaces_tablename']
        q = int(row['qfaces_tablename'][1])

        logger.info(f'{dataset}: Generating statistics for {q}-faces'' degrees')

        queries = [f'''
        CREATE INDEX IF NOT EXISTS {qfaces_tablename}_maximal_degree 
            ON "{dataset}".{qfaces_tablename} (maximal_degree);
        ''',
                            f'''
        CREATE INDEX IF NOT EXISTS {qfaces_tablename}_maximal_degree_u 
            ON "{dataset}".{qfaces_tablename} (maximal_degree_u);
        ''',
                            f'''
        CREATE INDEX IF NOT EXISTS {qfaces_tablename}_weighted_maximal_degree 
            ON "{dataset}".{qfaces_tablename} (weighted_maximal_degree);
        '''
        #                     f'''
        # CREATE INDEX IF NOT EXISTS {qfaces_tablename}_weighted_maximal_degree_u 
        #     ON "{dataset}".{qfaces_tablename} (weighted_maximal_degree_u);
        # '''
        ]

        if q == 0:
            queries.append(f'''
        CREATE INDEX IF NOT EXISTS {qfaces_tablename}_classical_degree 
            ON "{dataset}".{qfaces_tablename} (classical_degree);
        ''')

        db.execute_queries(queries)

        if q == 0:
            query = stats_sql_q0_faces.format(dataset, q, percentiles)
        else:
            query = stats_sql.format(dataset, q, percentiles)
        
        rows = db.execute_queries(
            "SELECT FROM pg_catalog.pg_tables WHERE tablename = 'degrees_stats'", return_rows=True, dict_cursor=True)
        with db.connection.cursor() as cursor:
            if len(rows) > 0:
                if len(db.execute_queries(
                        f"SELECT dataset FROM degrees_stats WHERE dataset = '{dataset}' AND q = {q}",
                        return_rows=True)) > 0:
                    if reset:
                        cursor.execute('DELETE FROM degrees_stats WHERE dataset = %s AND q = %s', (dataset, q))
                        cursor.execute(f'INSERT INTO degrees_stats {query}')
                else:
                    cursor.execute(f'INSERT INTO degrees_stats {query}')
            else:
                cursor.execute(f'CREATE TABLE degrees_stats AS {query}')

        export_degrees_to_csv(dataset, q)

    db.execute_queries("COPY degrees_stats TO '" + os.path.join(stats_dir, "degrees_stats.csv") +
                       "' WITH (FORMAT CSV, DELIMITER ';', HEADER);")


if __name__ == '__main__':
    db.connect()

    datasets_stats()
    [export_distribution_to_csv(dataset, 'simplices', 'q') for dataset in get_datasets_names_from_db('simplices')]
    [export_distribution_to_csv(dataset, 'facets', 'q') for dataset in get_datasets_names_from_db('facets')]

    degrees_stats(percentiles='{.5,.75,.9,.99,.999}', reset=True)

    db.disconnect()
