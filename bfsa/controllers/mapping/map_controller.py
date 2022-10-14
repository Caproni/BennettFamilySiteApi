#!
# -*- coding: utf-8 -*-
"""
╔═╗╦ ╦╔╦╗  ╔╦╗┬┌─┐┬┌┬┐┌─┐┬
║ ╦╠═╣ ║║   ║║││ ┬│ │ ├─┤│
╚═╝╩ ╩═╩╝  ═╩╝┴└─┘┴ ┴ ┴ ┴┴─┘

Created on 2022-10-13
@author: Edmund Bennett
@email: edmund.bennett@ghd.com
"""

from fastapi import APIRouter

from bfsa.controllers.environment import Environment as Base
from bfsa.utils.return_json import return_json
from bfsa.utils.logger import logger as log


router = APIRouter()

environment = Base()


@router.get("/api/mapboxKey")
async def get_mapbox_key():
    log.info("Calling get_mapbox_key")
    return return_json(
        message="Mapbox key successfully obtained",
        success=True,
        content="pk.eyJ1IjoiaGVsbGVxdWluIiwiYSI6ImNrb2ZtOGp4NTBnbGYybnAybXVrMTZuaWIifQ.Xe98acRuNfv3A7uxefmstg",
    )
