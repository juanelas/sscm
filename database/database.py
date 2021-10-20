import errno
import glob
import os
import sys
from configparser import ConfigParser
from typing import Dict, List

import psycopg2
import psycopg2.extensions
import psycopg2.extras

sys.path.append('../')
from logger import logger

config = ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), '../config.ini'))

class Database:
    """PostgreSQL Database class."""

    def __init__(self, db_config: Dict = None):
        self.config: Dict = {}
        self.connection = None
        if db_config:
            self.init(db_config)

    def init(self, db_config: Dict, drop_db_first=False):
        if "dbname" in db_config:
            self.config['dbname'] = db_config['dbname']

        if "host" in db_config:
            self.config['host'] = db_config['host']

        if "port" in db_config:
            self.config['port'] = db_config['port']

        if "user" in db_config:
            self.config['user'] = db_config['user']

        if "password" in db_config:
            self.config['password'] = db_config['password']

        self.create_db(drop_db_first=drop_db_first)

    def connect(self) -> bool:
        if not self.config:
            raise Exception('You should init the database with db.init(db_config: {})')
        try:
            if self.connection is None:
                self.connection = psycopg2.connect(**self.config)
                cursor = self.connection.cursor()
                # Print PostgreSQL Connection properties
                logger.debug(self.connection.get_dsn_parameters())

                # Print PostgreSQL version
                cursor.execute("SELECT version();")
                dbrecord = cursor.fetchone()
                logger.debug("Database connection opened successfully: {}".format(dbrecord))
                cursor.close()

                psycopg2.extras.register_uuid()
                return True
            else:
                return False
        except (Exception, psycopg2.Error) as error:
            logger.error(f"Error while connecting to PostgreSQL db: {self.config['dbname']}", error)
            sys.exit()

    def create_db(self, drop_db_first=False) -> None:
        if not self.config:
            raise Exception('You should init the database with db.init(db_config: {})')
        if self.connection is None:
            admin_config: Dict = self.config.copy()
            admin_config['dbname'] = 'postgres'
            self.connection = psycopg2.connect(**admin_config)
            self.connection.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = self.connection.cursor()
            cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s;", (self.config['dbname'],))
            exists = cursor.fetchone()
            if not exists:
                cursor.execute('CREATE DATABASE "{}";'.format(self.config['dbname']))
            elif drop_db_first:
                cursor.execute('DROP DATABASE "{}";'.format(self.config['dbname']))
                cursor.execute('CREATE DATABASE "{}";'.format(self.config['dbname']))
            cursor.close()
            self.disconnect(commit=False)
            if not exists:
                logger.debug("Database '{}' created".format(self.config['dbname']))
            else:
                logger.debug("Database '{}' already exists. No need to create".format(self.config['dbname']))

    def create_schema(self, schema_name: str) -> None:
        if not self.config:
            raise Exception('You should init the database with db.init(db_config: {})')
        previously_disconnected = self.connect()
        cursor = self.dict_cursor()
        cursor.execute('DROP SCHEMA IF EXISTS "{0}" CASCADE; CREATE SCHEMA "{0}";'.format(schema_name, ))
        cursor.close()
        logger.debug("Created SCHEMA: {}".format(schema_name))
        if previously_disconnected:
            self.disconnect()

    def execute_queries(self, queries, dict_cursor: bool = False, return_rows: bool = False,
                        column_names_as_first_row: bool = False):
        if not self.config:
            raise Exception('You should init the database with db.init(db_config: {})')
        previously_disconnected = self.connect()
        if dict_cursor:
            cursor = self.dict_cursor()
        else:
            cursor = self.connection.cursor()

        if not isinstance(queries, list):
            queries = [queries]
        ret: List = []
        for query in queries:
            try:
                logger.debug("Executing query:\n{}".format(query.lstrip()))
                cursor.execute(query)
                # logger.debug("Executed query: {} ...".format(query.lstrip()[0:80]))

                if return_rows:
                    rows: List = []
                    if column_names_as_first_row:
                        columns = tuple([d.name for d in cursor.description])
                        rows.append(columns)
                    fecthed = cursor.fetchall()
                    rows.extend(fecthed)
                    ret.append(rows)
            except (Exception, psycopg2.Error) as error:
                self.disconnect()
                raise Exception(error)

        cursor.close()
        self.connection.commit()
        if previously_disconnected:
            self.disconnect()

        if return_rows:
            if len(queries) > 1:
                return ret
            else:
                return ret[0]

    def execute_queries_from_path(self, path: str, formats: List[str]):
        if not self.config:
            raise Exception('You should init the database with db.init(db_config: {})')
        if os.path.isdir(path):
            files = sorted(glob.glob(f'{path}/*.sql'))
        else:
            files = [path]
        queries: List = []
        for name in files:
            try:
                with open(name) as f:
                    queries.append(f.read().format(*formats))
            except IOError as exc:
                if exc.errno != errno.EISDIR:
                    raise
        self.execute_queries(queries)

    def disconnect(self, commit: bool = True) -> None:
        if self.connection:
            if commit:
                self.connection.commit()
            self.connection.close()
            self.connection = None
            logger.debug("Database connection closed")

    def dict_cursor(self, name: str = None) -> psycopg2.extras.DictCursor:
        """Returns a dict cursor"""
        if not self.config:
            raise Exception('You should init the database with db.init(db_config: {})')
        previously_disconnected = self.connect()
        cursor = self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor, name=name)
        if previously_disconnected:
            self.disconnect()
        return cursor

    def vacuum(self, parameters: str = None) -> None:
        if not self.config:
            raise Exception('You should init the database with db.init(db_config: {})')
        previously_disconnected = self.connect()
        self.connection.commit()
        old_isolation_level = self.connection.isolation_level
        self.connection.set_isolation_level(0)
        sql = f"VACUUM {parameters};"
        cursor = self.connection.cursor()
        logger.debug(sql)
        cursor.execute(sql)
        self.connection.set_isolation_level(old_isolation_level)
        logger.debug("Database VACUUMed")
        if previously_disconnected:
            self.disconnect()


if __name__ == "__main__":
    # execute only if run as a script
    db: Database = Database()
    db.init(config['SimplicialDB'])
    db.connect()
    cur = db.dict_cursor()
    cur.execute("SELECT version();")
    record = cur.fetchone()
    logger.debug("First record: {}".format(record))
    cur.close()
    db.disconnect()
