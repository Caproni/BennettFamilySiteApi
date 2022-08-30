#!
# -*- coding: utf-8 -*-
"""
Created on 2022-08-07
@author: Edmund Bennett
@email: bennettedmund@gmail.com
"""

from typing import Dict, Any


def create_select(where: Dict[str, Any] = None) -> str:
    """
    Constructs an SQL SELECT query with optional where clause
    :param where:
    :return:
    """
    query = "SELECT * FROM c"
    if where is not None:
        for i, (k, v) in enumerate(where.items()):
            if i == 0:
                query += f" WHERE c.{k} = '{v}'"
            else:
                query += f" AND c.{k} = '{v}'"
    return query


if __name__ == "__main__":
    pass
