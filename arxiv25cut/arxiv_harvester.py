import argparse
import os
import pickle
import re
import sys
from configparser import ConfigParser
from datetime import date
from typing import List

import requests
import xmltodict
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

config = ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), '..', 'config.ini'))


def requests_retry_session(
        retries=7,
        backoff_factor=0.4,
        status_forcelist=(500, 502, 503, 504),
        session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


def restore(dataset: str) -> object:
    basedir = os.path.join(config['ArXiv']['basedir'], dataset)
    try:
        dir_files = os.listdir(basedir)  # list of directory files
    except FileNotFoundError:
        raise ValueError("No session to restore in {}".format(basedir))

    if len(dir_files) == 0:
        raise ValueError("No session to restore in {}".format(basedir))

    dir_files.sort()  # good initial sort but doesnt sort numerically very well
    last_file = dir_files[-1]
    i = int(last_file[:5])
    __parts: List[str] = last_file.split('of')
    start = int(__parts[0].split('-')[-1]) + 1
    total = int(__parts[1][:-7])
    if start < total:
        with open(os.path.join(basedir, last_file), 'rb') as file:
            # The protocol version used is detected automatically, so we do not
            # have to specify it.
            records = pickle.load(file)

        resumption_token = records['resumptionToken']['#text']

        date_from = ''
        date_until = ''
        dates = re.findall(r'\d{4}-\d{2}-\d{2}', last_file)

        if len(dates) >= 1:
            date_until = dates[-1]
            if len(dates) > 1:
                date_from = dates[0]

        if 'dateUntil' in records:
            date_until = records['dateUntil']
            date_from = records['dateFrom']

        return i, resumption_token, date_from, date_until

    raise ValueError("No session to restore in {}".format(basedir))


def get_records(dataset: str, restore_session: bool = True, date_from: str = '', date_until: str = '',
                resumption_token: str = '', i: int = 0) -> object:
    if restore_session:
        try:
            i, resumption_token, date_from, date_until = restore(dataset)
        except ValueError as err:
            print(err)
            sys.exit()

    params = {
        'verb': 'ListRecords',
        'metadataPrefix': 'oai_dc',
        'set': dataset
    }

    if date_from:
        params['from'] = date_from
    if date_until:
        params['until'] = date_until

    basedir = os.path.join(config['ArXiv']['basedir'], dataset)

    while True:
        try:
            os.makedirs(basedir, exist_ok=True)
        except OSError:
            print("Creation of the directory %s failed" % basedir)
            break

        if resumption_token:
            params = {
                'verb': 'ListRecords',
                'resumptionToken': resumption_token
            }

        r = requests_retry_session().get(config['ArXiv']['baseurl'], params=params)
        d = xmltodict.parse(r.text)
        if 'error' in d['OAI-PMH']:
            raise ValueError("{}: {}".format(d['OAI-PMH']['error']['@code'], d['OAI-PMH']['error']['#text']))

        records = d['OAI-PMH']['ListRecords']
        records['dateFrom'] = date_from
        records['dateUntil'] = date_until

        if 'resumptionToken' in records:
            start = int(records['resumptionToken']['@cursor'])
            total = int(records['resumptionToken']['@completeListSize'])
        else:
            start = 0
            total = len(records['record'])

        stop = start + len(records['record']) - 1

        records['i'] = i
        records['start'] = start
        records['stop'] = stop
        records['total'] = total

        if 'from' in params:
            path = "{}/{:0>5d}_from{}until{}_{}-{}of{}.pickle".format(basedir, i, date_from, date_until, start, stop,
                                                                      total)
        else:
            path = "{}/{:0>5d}_until{}_{}-{}of{}.pickle".format(basedir, i, date_until, start, stop, total)

        with open(path, 'wb') as file:
            # Pickle the 'data' dictionary using the highest protocol available.
            pickle.dump(records, file)

        i = i + 1
        if 'resumptionToken' not in records or '#text' not in records['resumptionToken']:
            return
        else:
            resumption_token = records['resumptionToken']['#text']


def list_datasets():
    params = {
        'verb': 'ListSets'
    }
    r = requests_retry_session().get(config['ArXiv']['baseurl'], params=params)
    datasets = xmltodict.parse(r.text)['OAI-PMH']['ListSets']['set']
    return datasets


def main():
    parser = argparse.ArgumentParser(description='Download arXiv datasets')
    parser.add_argument("-l", "--list-datasets", help="list all available arXiv datasets", action="store_true")
    parser.add_argument("-d", "--datasets", help="a dataset or a comma-separated list of datasets to download")
    parser.add_argument("-r", "--restore",
                        help="restore interrupted session instead of starting over again (no from or until needed)",
                        action="store_true")
    parser.add_argument("-f", "--from", help="date from in YYYY-MM-DD format")
    parser.add_argument("-u", "--until", help="date until in YYYY-MM-DD format")

    args = parser.parse_args()

    if args.list_datasets:
        datasets = list_datasets()
        for dataset in datasets:
            print('{:20} <- {}'.format(dataset['setSpec'], dataset['setName']))
        comma_separated_list_of_datasets = ",".join([dataset['setSpec'] for dataset in datasets])
        print(comma_separated_list_of_datasets)
        sys.exit()

    if not args.datasets:
        parser.print_help()
        sys.exit()

    datasets = args.datasets.split(',')

    if vars(args)['from']:
        date_from = vars(args)['from']
    else:
        date_from = ''

    if vars(args)['until']:
        date_until = vars(args)['until']
    else:
        date_until = date.today().strftime("%Y-%m-%d")

    for dataset in datasets:
        try:
            get_records(dataset, restore_session=args.restore, date_from=date_from, date_until=date_until)
        except ValueError as err:
            print(err)


if __name__ == "__main__":
    # execute only if run as a script
    main()
