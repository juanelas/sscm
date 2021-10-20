import argparse
import os
import pickle
import sys

from psycopg2.extras import execute_values

sys.path.append('../')
from configparser import ConfigParser
from typing import Dict, List, Set, Tuple
from logger import logger

from tqdm import tqdm

from arxiv.arxiv_classes.arxiv import Author, Paper
from arxiv.arxiv_db import arxiv_db

config = ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))

_arxiv_papers: List[Tuple[str, List[str], List[str]]] = []  # (title, authors, dates)
_papers: Dict[str, Paper] = {}
_authors: Dict[str, Author] = {}
_discarded_papers: List[Tuple[str, List[str], List[str], str]] = []  # (title, authors, dates, reason)
_discarded_authors: Set[Tuple[str, str]] = set()


def _to_list(input_value):
    if type(input_value) == list:
        return input_value
    else:
        return [input_value]


def _are_equal_lists(list1: List, list2: List):
    if len(list1) != len(list2):
        return False
    for i in range(len(list1)):
        if list1[i] != list2[i]:
            return False
    return True


def init_db_schema(dataset: str) -> None:
    logger.info(f'{dataset:} Initializing schema {dataset} on db "{config["Database"]["dbname"]}"')
    arxiv_db.create_schema(dataset)
    arxiv_db.execute_queries_from_path(os.path.abspath('./sql/00_prepare_arxiv_db.sql'), [dataset])


def load_arxiv_files(basedir, dir_files, dataset):
    __parts: List[str] = dir_files[0].split('of')
    total = int(__parts[1][:-7])

    # Add the papers
    with tqdm(total=total, desc=f"{dataset}: Processing papers/authors from harvested ArXiv files") as pbar:
        for filename in dir_files:
            with open(os.path.join(basedir, filename), 'rb') as file:
                records = pickle.load(file)
                for record in records['record']:
                    if 'metadata' in record:
                        title = record['metadata']['oai_dc:dc']['dc:title']
                        record_authors = _to_list(record['metadata']['oai_dc:dc']['dc:creator'])
                        dates = _to_list(record['metadata']['oai_dc:dc']['dc:date'])
                        _arxiv_papers.append((title, record_authors, dates))
                        paper_authors: Set[Author] = set()
                        for record_author in record_authors:
                            try:
                                author = Author(record_author)
                                paper_authors.add(author)
                            except ValueError:
                                _discarded_authors.add((record_author, title))
                        if len(paper_authors) > 0:
                            paper = Paper(title, [author.id for author in paper_authors], dates)
                            repeated = False
                            if paper.id in _papers:
                                if not _are_equal_lists(paper.author_ids, _papers[paper.id].author_ids):
                                    paper_id = paper.id
                                    paper.id = paper_id + '_alt'
                                    i = 2
                                    while paper.id in _papers:
                                        paper.id = paper_id + f'_alt{i}'
                                        i += 1
                                    _papers[paper.id] = paper
                                else:
                                    repeated = True
                                    if not _are_equal_lists(paper.dates, _papers[paper.id].dates):
                                        _papers[paper.id].dates.extend(paper.dates)
                                        _papers[paper.id].dates = sorted(set(_papers[paper.id].dates))
                                    else:
                                        _discarded_papers.append((title, record_authors, dates, "repeated papers"))
                            else:
                                _papers[paper.id] = paper

                            if not repeated:
                                for author in paper_authors:
                                    if author.id not in _authors:
                                        _authors[author.id] = author
                                    _authors[author.id].paper_ids.add(paper.id)
                                    _authors[author.id].alt_names.update(author.alt_names)
                        else:
                            _discarded_papers.append((title, record_authors, dates, 'no valid authors'))
                    pbar.update(1)


def insert_papers_authors_in_db(dataset: str, batch_size: int = 1000):
    page_size = batch_size + 1 if batch_size > 100 else 100

    insert_query: str = f'INSERT INTO "{dataset}".arxiv_papers (title, authors, dates) VALUES %s'
    cursor = arxiv_db.connection.cursor()
    j: int = 0
    query_values: List = []
    total = len(_arxiv_papers)
    with tqdm(total=total, desc=f"{dataset}: Inserting original (non-filtered) arXiv papers into DB") as pbar:
        for title, paper_authors, dates in _arxiv_papers:
            dates_str = ",".join(['"{}"'.format(date) for date in dates])
            dates_str = '{' + dates_str + '}'
            query_values.append((title, paper_authors, dates_str))
            j += 1
            if j == batch_size:
                execute_values(cursor, insert_query, query_values, page_size=page_size)
                j = 0
                query_values.clear()
                pbar.update(batch_size)
        if j > 0:
            execute_values(cursor, insert_query, query_values, page_size=page_size)
            pbar.update(j)

    insert_query: str = f'INSERT INTO "{dataset}".authors (name, alt_names) VALUES %s'
    cursor = arxiv_db.connection.cursor()
    j: int = 0
    query_values: List[Tuple[str, List[str]]] = []
    total = len(_authors)
    with tqdm(total=total, desc=f"{dataset}: Inserting authors (name normalised) into DB") as pbar:
        for author in _authors.values():
            query_values.append((author.id, sorted(author.alt_names)))
            j += 1
            if j == batch_size:
                execute_values(cursor, insert_query, query_values, page_size=page_size)
                j = 0
                query_values.clear()
                pbar.update(batch_size)
        if j > 0:
            execute_values(cursor, insert_query, query_values, page_size=page_size)
            pbar.update(j)

    if len(_discarded_authors) > 0:
        insert_query: str = f'INSERT INTO "{dataset}".discarded_authors (name, paper_title) VALUES %s'
        cursor = arxiv_db.connection.cursor()
        j: int = 0
        query_values: List[Tuple[str, str]] = []
        total = len(_discarded_authors)
        with tqdm(total=total, desc=f"{dataset}: Inserting discarded authors into DB") as pbar:
            for author in _discarded_authors:
                query_values.append((author[0], author[1]))
                j += 1
                if j == batch_size:
                    execute_values(cursor, insert_query, query_values, page_size=page_size)
                    j = 0
                    query_values.clear()
                    pbar.update(batch_size)
            if j > 0:
                execute_values(cursor, insert_query, query_values, page_size=page_size)
                pbar.update(j)

    insert_query: str = f'INSERT INTO "{dataset}".papers (title, authors, dates) VALUES %s'
    cursor = arxiv_db.connection.cursor()
    j: int = 0
    query_values: List[Tuple[str, List[str], str]] = []
    total = len(_papers)
    with tqdm(total=total, desc=f"{dataset}: Inserting filtered papers into DB") as pbar:
        for paper in _papers.values():
            dates_str = ",".join(['"{}"'.format(date) for date in paper.dates])
            dates_str = '{' + dates_str + '}'
            query_values.append((paper.id, paper.author_ids, dates_str))
            j += 1
            if j == batch_size:
                execute_values(cursor, insert_query, query_values, page_size=page_size)
                j = 0
                query_values.clear()
                pbar.update(batch_size)
        if j > 0:
            execute_values(cursor, insert_query, query_values, page_size=page_size)
            pbar.update(j)

    if len(_discarded_papers):
        insert_query: str = f'INSERT INTO "{dataset}".discarded_papers (title, authors, dates, reason)' \
                            f'VALUES %s ON CONFLICT DO NOTHING'
        cursor = arxiv_db.connection.cursor()
        j: int = 0
        query_values: List[Tuple[str, List[str], str, str]] = []
        total = len(_discarded_papers)
        with tqdm(total=total, desc=f"{dataset}: Inserting discarded papers into DB") as pbar:
            for paper in _discarded_papers:
                dates_str = ",".join(['"{}"'.format(date) for date in paper[2]])
                dates_str = '{' + dates_str + '}'
                query_values.append((paper[0], paper[1], dates_str, paper[3]))
                j += 1
                if j == batch_size:
                    execute_values(cursor, insert_query, query_values, page_size=page_size)
                    j = 0
                    query_values.clear()
                    pbar.update(batch_size)
            if j > 0:
                execute_values(cursor, insert_query, query_values, page_size=page_size)
                pbar.update(j)

    logger.info(f'{dataset}: Creating papers-authors relationship bidirectional table...')
    arxiv_db.execute_queries_from_path(os.path.abspath('./sql/01_papers_authors.sql'), [dataset])

    logger.info(f"{dataset}: Completed!")

    if len(_discarded_papers) > 0:
        logger.warning(f'{len(_discarded_papers)} paper/s has/have been discarded:' +
                       f'See table {dataset}.discarded_papers on the {config["Database"]["dbname"]}' +
                       'database for more details')

    if len(_discarded_authors) > 0:
        discarded_authors_set = set()
        [discarded_authors_set.add(author) for author, paper in _discarded_authors]
        logger.warning(f'{len(discarded_authors_set)} author/s has/have been discarded:' +
                       f'\n{discarded_authors_set}\n' +
                       f'See table {dataset}.discarded_authors on the {config["Database"]["dbname"]}' +
                       'database for more details')


def create_simplicies(dataset: str) -> None:
    logger.info(f'{dataset}: Creating simplices...')
    arxiv_db.execute_queries_from_path(os.path.abspath('./sql/02_simplices.sql'), [dataset])
    return None


def load_dataset(dataset):
    basedir: str = os.path.join(config['ArXiv']['basedir'], dataset)
    dir_files: List[str] = os.listdir(basedir)  # list of directory files

    if len(dir_files) == 0:
        raise ValueError("No session to restore in {}".format(basedir))

    dir_files.sort()

    init_db_schema(dataset)

    load_arxiv_files(basedir, dir_files, dataset)

    insert_papers_authors_in_db(dataset)
    _arxiv_papers.clear()
    _papers.clear()
    _authors.clear()
    _discarded_papers.clear()
    _discarded_authors.clear()

    create_simplicies(dataset)

    logger.info(f'{dataset}: All done!')


def main(dsets=None):
    arxiv_db.init(config['Database'], drop_db_first=True)
    arxiv_db.connect()
    if not dsets:
        dsets = [os.path.split(x[0])[-1] for x in os.walk(config['ArXiv']['basedir'])][1:]

    for dataset in dsets:
        try:
            load_dataset(dataset)
        except ValueError as error:
            logger.error(error)
    arxiv_db.disconnect()
    logger.info("All done!")


if __name__ == "__main__":
    # execute only if run as a script

    parser: argparse.ArgumentParser = argparse.ArgumentParser(description='Load arXiv datasets into PostgreSQL')
    parser.add_argument("-d",
                        "--datasets",
                        help="a dataset or a comma-separated list of datasets to load")

    args = parser.parse_args()

    if args.datasets:
        datasets = args.datasets.split(',')
    else:
        datasets = None

    main(datasets)
