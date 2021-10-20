import os
import sys
from configparser import ConfigParser

sys.path.append('../')
from database.database import Database

config = ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), '../config.ini'))


def get_datasets_names_from_db(tablename_to_check: str = 'simplices'):
    db = Database()
    db.init(config['SimplicialDB'])
    sql = f'''
        SELECT DISTINCT schemaname FROM pg_catalog.pg_tables WHERE tablename = '{tablename_to_check}'
        UNION
        SELECT DISTINCT schemaname FROM pg_catalog.pg_views WHERE viewname = '{tablename_to_check}'
    '''
    rows = db.execute_queries(sql, return_rows=True)
    db.disconnect()
    datasets = [row[0] for row in rows]
    return datasets


if __name__ == "__main__":
    # execute only if run as a script
    print(get_datasets_names_from_db())
