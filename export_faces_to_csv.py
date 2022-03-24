import os
import sys
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from typing import List

from database import get_datasets_names_from_db
from database.instance import db
from directories import simplicialcomplex_dir
from logger import logger
from stats import get_dataset_qs


def main(datasets: List[str], qs: List[int] = None):
    for dataset in datasets:
        db_qs = get_dataset_qs(dataset)
        qs_gen = (q for q in qs if q in db_qs) if qs else (q for q in db_qs)
        for q in qs_gen:
            csvfilename = os.path.join(
                simplicialcomplex_dir, f"{dataset}_q{q}_faces.csv")
            logger.info('%s: Exporting %d-faces to %s',
                        dataset, q, csvfilename)
            db.execute_queries(
                f'''COPY "{dataset}".q{q}_faces (face) TO '{csvfilename}' WITH (FORMAT CSV, DELIMITER ';');''')
            logger.info('%s: Done exporting %d-faces to %s',
                        dataset, q, csvfilename)


if __name__ == "__main__":
    # execute only if run as a script

    db_datasets = get_datasets_names_from_db()

    parser: ArgumentParser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter,
                                            description=f'''ouput requested dataset qfaces with degrees'stats to a csv file at directoy {simplicialcomplex_dir}. You can edit output dir in config.ini

Available datasets:
{str(db_datasets)[1:-1].replace(', ', ',')}''')
    parser.add_argument("-d",
                        "--datasets",
                        help=f"a dataset or a comma-separated list of datasets to load. Available datasets: {db_datasets}")
    parser.add_argument("-l",
                        "--listdatasets",
                        help="do nothing but get the list available datasets to load from db",
                        action="store_true")
    parser.add_argument("-q",
                        help="get only the provided list of q-faces (if available), with Q a comma separated list of q (int)")

    args = parser.parse_args()

    if args.listdatasets:
        print(",".join(get_datasets_names_from_db()))
        sys.exit()

    dsets: List[str] = args.datasets.split(',') if args.datasets else None

    if not dsets:
        dsets = get_datasets_names_from_db()

    qs_list: List[int] = [int(q)
                          for q in args.q.split(',')] if args.q else None

    main(dsets, qs_list)
