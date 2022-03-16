"""Converts a python list to a postgresql array string"""

from typing import List

def list_to_pg_arr(python_list: List, cast: str = None) -> str:
    """Converts a python list to a postgresql array string"""
    pg_array: str = str(python_list).replace('[', '{').replace(']', '}')
    if cast:
        pg_array += f'::{cast}'
    return pg_array
