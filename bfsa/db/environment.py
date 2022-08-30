#!
# -*- coding: utf-8 -*-
"""
Created on 2022-07-17
@author: Edmund Bennett
@email: bennettedmund@gmail.com
"""

from typing import Dict
from json import load

from bfsa.utils.get_vault_secret import get_vault_secret
from bfsa.utils.logger import logger as log


class Environment:
    PATH_TO_CONFIG = "credentials/db_config.json"

    @classmethod
    def load_db_credentials(cls) -> Dict[str, str]:
        log.info("Calling load_db_credentials")
        with open(Environment.PATH_TO_CONFIG, "r") as config_file:
            db_config = load(config_file)
            db_config["key"] = get_vault_secret("bennett-family-cosmos-connection-string")
            return db_config


if __name__ == "__main__":
    pass
