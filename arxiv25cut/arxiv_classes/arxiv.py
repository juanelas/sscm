import re
import sys

sys.path.append('../')
from unidecode import unidecode

from classes.classes import UniqueObject, Node, Facet
from typing import List, Set


def _initials(words: List[str]) -> str:
    words_arr = [word[0] for word in words]
    return ". ".join(words_arr).strip() + "."


class Author(UniqueObject):
    def __init__(self, name: str) -> None:
        try:
            normalised_name = self.normalise_name(name)
            super().__init__(normalised_name)
            self.alt_names: Set[str] = set()
            self.paper_ids: Set = set()
            self.alt_names.add(name)
        except ValueError:
            raise

    @staticmethod
    def normalise_name(author: str) -> str:
        author: str = unidecode(author).lower()
        author: str = re.sub(r"[^a-z,'\"\-. ]+", r'', author)
        author = re.sub(r'[.\-]', ' ', author).strip().title()
        if author is '':
            raise ValueError(author)

        normalised_name: str = ''
        author_names: list = author.split(",")
        author_names = [name.strip() for name in author_names]

        # If no comma separated names, let us split the words in author_names
        if len(author_names) is 1 and author_names[0]:
            lastname_words = author_names[0].split()  #
            if len(lastname_words) == 1:
                # If only one word with more than 2 letters then that is the name; else discard author
                if len(lastname_words[0]) >= 2:
                    normalised_name = lastname_words[0]
            elif len(lastname_words[-1]) > 1:  # If more than one word
                lastname = lastname_words[-1]  # lastname is the last word
                firstname = _initials(lastname_words[0:-1])  # and firstname the previous words
                normalised_name = f"{lastname}, {firstname}"
            else:
                normalised_name = author_names[0]
        else:
            if len(author_names[0]) >= 2:
                lastname: str = author_names[0]
                firstname_words = author_names[1].split()
                if len(firstname_words) > 1:
                    if len(firstname_words[0]) == 1:
                        firstname_words[0] += '.'
                    firstname = f'{firstname_words[0]} {_initials(firstname_words[1:])}'
                else:
                    firstname = author_names[1]
                    if len(author_names[1]) == 1:
                        firstname += '.'
                normalised_name = f"{lastname}, {firstname}"
            elif len(author_names[1]) >= 2:
                lastname: str = author_names[1]
                firstname: str = _initials(author_names[0].split())
                normalised_name = f"{lastname}, {firstname}"

        if normalised_name is '':
            raise ValueError(author)

        return normalised_name


class AuthorNode(Node):
    def __init__(self, author: Author) -> None:
        super().__init__(author.id)
        self.paper_ids = author.paper_ids


class Paper(UniqueObject):
    def __init__(self, paper_title: str, author_ids: List, dates: List[str]):
        super().__init__(self.get_id(paper_title))
        self.author_ids: List = author_ids
        self.dates: List[str] = sorted(dates)

    @staticmethod
    def get_id(title: str) -> str:
        return title.translate(str.maketrans({'\n': None, '\t': ' ', '\r': None}))


class PaperFacet(Facet):
    def __init__(self, paper: Paper):
        super().__init__(paper.author_ids)
        self.paper_ids: Set = set()
