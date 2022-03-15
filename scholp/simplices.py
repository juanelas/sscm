import os
import sys
from argparse import ArgumentParser
from configparser import ConfigParser
from glob import glob
from typing import List, Tuple

from psycopg2.extras import execute_values
from tqdm import tqdm

sys.path.append('../')
from scholp.scholp_db import scholp_db
from logger import logger

config = ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), '.', 'config.ini'))


class ScholpSimplices:
    def __init__(self, dataset: str = None):
        self._open: bool = False
        self._pos: int = 0
        self._simplices_no_nodes_file = None
        self._simplices_nodes_file = None
        self._len = 0
        if dataset:
            self.load_dataset(dataset)

    def load_dataset(self, dataset: str):
        dset_dir = os.path.join(config['Scholp']['basedir'], dataset)
        self._simplices_no_nodes_file = open(os.path.join(dset_dir, f'{dataset}-nverts.txt'), 'rb')
        self._simplices_nodes_file = open(os.path.join(dset_dir, f'{dataset}-simplices.txt'), 'rb')
        self._len = sum(1 for line in self._simplices_no_nodes_file)
        self.restart()
        self._open = True

    def __iter__(self):
        if not self._open:
            raise Exception("You should first load a dataset with .load_dataset(dataset: str)")
        self.restart()
        return self

    def __next__(self):
        if not self._open:
            raise StopIteration
        line = self._simplices_no_nodes_file.readline()
        if not line:
            raise StopIteration
        simplex_no_nodes = int(line)
        return [int(self._simplices_nodes_file.readline()) for i in range(simplex_no_nodes)]

    def __len__(self) -> int:
        return self._len

    def restart(self):
        self._simplices_no_nodes_file.seek(0)
        self._simplices_nodes_file.seek(0)

    def close(self):
        self._simplices_nodes_file.close()
        self._simplices_no_nodes_file.close()
        self._len = 0
        self._open = False


def get_dataset_names():
    dataset_dirs = glob(os.path.join(config['Scholp']['basedir'], "*", ""))
    datasets = []
    [datasets.append(os.path.basename(dataset_dir[0:-1])) for dataset_dir in dataset_dirs]
    return sorted(datasets)


def load_dataset_onto_db(dataset: str, batch_size: int = 500) -> None:
    page_size = batch_size + 1 if batch_size > 100 else 100

    print(f'{dataset:} Initializing schema {dataset} on db "{config["Database"]["dbname"]}"')
    scholp_db.create_schema(dataset)
    scholp_db.execute_queries_from_path(os.path.abspath('./sql/00_simplices.sql'), [dataset])

    raw_simplices = ScholpSimplices(dataset)
    insert_query: str = f'INSERT INTO "{dataset}".simplices (node_ids) VALUES %s'
    cursor = scholp_db.connection.cursor()
    j: int = 0
    query_values: List[Tuple[List[int]]] = []
    total = len(raw_simplices)
    
    print(f"{dataset}: Inserting simplices from dataset")
    with tqdm(total=total) as pbar:
        for simplex in raw_simplices:
            query_values.append((simplex,))
            j += 1
            if j == batch_size:
                execute_values(cursor, insert_query, query_values, page_size=page_size)
                j = 0
                query_values.clear()
                pbar.update(batch_size)
        if j > 0:
            execute_values(cursor, insert_query, query_values, page_size=page_size)
            pbar.update(j)


def main(datasets=None):
    scholp_db.init(config['Database'], drop_db_first=False)
    scholp_db.connect()
    if not datasets:
        datasets = get_dataset_names()

    for dataset in datasets:
        try:
            load_dataset_onto_db(dataset)
            # print(dset)
        except ValueError as error:
            logger.error(error)
    scholp_db.disconnect()
    logger.info("All done!")


if __name__ == "__main__":
    # execute only if run as a script

    parser: ArgumentParser = ArgumentParser(description='Load ScHoLP datasets into PostgreSQL')
    parser.add_argument("-d",
                        "--datasets",
                        help="a dataset or a comma-separated list of datasets to load")

    args = parser.parse_args()

    if args.datasets:
        dsets = args.datasets.split(',')
    else:
        dsets = None

    main(dsets)
