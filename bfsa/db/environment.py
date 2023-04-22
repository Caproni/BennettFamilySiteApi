#!
# -*- coding: utf-8 -*-
"""
Created on 2022-07-17
@author: Edmund Bennett
@email: bennettedmund@gmail.com
"""

from typing import Dict
from json import load

from bfsa.db.client import Client
from bfsa.controllers.environment import Environment as BaseEnvironment
from bfsa.utils.get_vault_secret import get_vault_secret
from bfsa.utils.logger import logger as log
from bfsa.utils.return_json import return_json


base = BaseEnvironment()


class Environment:
    PATH_TO_CONFIG = "credentials/db_config.json"

    @classmethod
    def load_db_credentials(cls) -> Dict[str, str]:
        log.info("Calling load_db_credentials")
        with open(Environment.PATH_TO_CONFIG, "r") as config_file:
            db_config = load(config_file)
            db_config["key"] = get_vault_secret(
                "bennett_family_cosmos_connection_string",
                production=base["IS_PROD"],
            )
            return db_config


def client_factory() -> Client:
    db_config = Environment.load_db_credentials()

    try:
        return Client(
            endpoint=db_config["uri"],
            key=db_config["key"],
            database_name=db_config["db"],
            container_name=db_config["collection"],
        )
    except Exception as e:
        log.critical(f"Error connecting to database. Error: {e}")
        return return_json(
            message="Error connecting to database.",
            success=False,
        )


if __name__ == "__main__":
    pass
