#!
# -*- coding: utf-8 -*-
"""
Created on 2022-11-06
@author: Edmund Bennett
@email: bennettedmund@gmail.com
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter
import requests
from pydantic import BaseModel

from bfsa.controllers.environment import Environment
from bfsa.utils.return_json import return_json
from bfsa.utils.get_vault_secret import get_vault_secret
from bfsa.utils.logger import logger as log


router = APIRouter()


@router.post("/api/tmdb/discover")
def discover(
    query: str,
):
    """
    Discover endpoint from tmdb
    """
    log.info("Calling discover")

    environment = Environment()

    get_vault_secret(
        secret_name="",
        production=environment["IS_PROD"],
    )

    return return_json(
        "Successfully queried movie database.",
        success=True,
        content=None,
    )


if __name__ == "__main__":
    pass
