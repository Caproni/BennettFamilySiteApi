#!
# -*- coding: utf-8 -*-
"""
Created on 2022-08-28
@author: Edmund Bennett
@email: bennettedmund@gmail.com
"""

from typing import Union
from os import getenv


class Environment:
    IS_PROD = "IS_PROD"

    _environment = {}

    def __init__(self):
        self._environment[Environment.IS_PROD] = (
            True if getenv(Environment.IS_PROD) == "1" else False
        )

    def __getitem__(self, key: str) -> Union[bool, str]:
        try:
            return self._environment[key]
        except KeyError as _:
            raise EnvironmentError(f"{key} is an unsupported environment variable")

    def __str__(self) -> str:
        res = "Environment:\n"
        for key, value in self._environment:
            res += f"{key}: {value}\n"

        return res



if __name__ == "__main__":
    pass
