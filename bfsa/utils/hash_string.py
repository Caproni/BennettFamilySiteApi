#!
# -*- coding: utf-8 -*-
"""
Created on 2022-11-28
@author: Edmund Bennett
@email: bennettedmund@gmail.com
"""

import hashlib


def hash_string(hashable_input: str, characters: int = None) -> str:
    hashed_input = hashlib.sha256(hashable_input.encode("utf8")).hexdigest()
    return hashed_input[:characters] if hashed_input is not None else hashed_input


if __name__ == "__main__":
    pass
