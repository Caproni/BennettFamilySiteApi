#!
# -*- coding: utf-8 -*-
"""
Created on 2022-08-21
@author: Edmund Bennett
@email: bennettedmund@gmail.com
"""

from fastapi import APIRouter
from pydantic import BaseModel

from bfsa.controllers.environment import Environment
from bfsa.utils.get_vault_secret import get_vault_secret
from bfsa.utils.return_json import return_json
from bfsa.utils.logger import logger as log


router = APIRouter()


class AuthenticationModel(BaseModel):
    """
    Pydantic model for authentication
    """
    username: str
    password: str


@router.post("/api/authenticate")
def authenticate(
    authentication: AuthenticationModel,
):
    """
    Authenticate as site admin
    """
    log.info("Calling authenticate")

    environment = Environment()

    secret = get_vault_secret(
        "bennett_family_admin_password",
        production=environment["IS_PROD"],
    )

    if authentication.username == "admin" and secret is not None and authentication.password == secret:
        return return_json(
            message="Successfully authenticated.",
            success=True,
        )

    return return_json(
        message="Credentials incorrect. Could not authenticate.",
        success=False,
    )
