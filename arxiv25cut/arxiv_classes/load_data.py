import configparser
import os
import pickle
from glob import glob

config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), '../config.ini'))


class SimplicialDict(dict):
    # subject can be: 'authors', 'papers', 'nodes', 'facets'
    def __init__(self, subject: str):
        super().__init__()
        self.subject = subject

    def load(self, dataset: str):
        self.clear()
        with open(os.path.join(config['Simplicial']['basedir'], f'{dataset}_{self.subject}.pickle'), 'rb') as file:
            self.update(pickle.load(file))

class SimplicialList(list):
    # subject can be: 'arxivpapers'
    def __init__(self, subject: str):
        super().__init__()
        self.subject = subject

    def load(self, dataset: str):
        self.clear()
        with open(os.path.join(config['Simplicial']['basedir'], f'{dataset}_{self.subject}.pickle'), 'rb') as file:
            self.extend(pickle.load(file))


def available_datasets(subject):
    available_filenames = glob(f"{config['Simplicial']['basedir']}/*_{subject}.pickle")
    datasets = set([available_filename.split('/')[-1].split('_')[0] for available_filename in available_filenames])
    return datasets


arxiv_papers: SimplicialList = SimplicialList('arxivpapers')
authors: SimplicialDict = SimplicialDict('authors')
papers: SimplicialDict = SimplicialDict('papers')
nodes: SimplicialDict = SimplicialDict('nodes')
facets: SimplicialDict = SimplicialDict('facets')

if __name__ == '__main__':
    print(available_datasets('authors'))
