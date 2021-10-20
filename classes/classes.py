import hashlib
from typing import List, Set


class UniqueObject:
    def __init__(self, object_id):
        self.id = object_id

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)


class Node(UniqueObject):
    def __init__(self, node_id, facet_ids: Set = None, weight: int = 1) -> None:
        super().__init__(node_id)
        self.facet_ids: Set = facet_ids if facet_ids else set()
        self.weight = weight


class Simplex:
    def __init__(self, node_ids: List):
        self.node_ids: Set = set(node_ids)


class Facet(UniqueObject, Simplex):
    def __init__(self, simplex: Simplex) -> None:
        self.node_ids: Set = set(simplex.node_ids)
        sorted_node_ids: List = sorted(self.node_ids)
        self.id: str = _str_to_uuidstr(";".join(sorted_node_ids))

        super().__init__(self.id)


def _str_to_uuidstr(a: str) -> str:
    return hashlib.md5(a.encode('utf-8')).hexdigest()
