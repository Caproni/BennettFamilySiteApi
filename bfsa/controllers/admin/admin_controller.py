#!
# -*- coding: utf-8 -*-
"""
Created on 2022-07-16
@author: Edmund Bennett
@email: bennettedmund@gmail.com
"""

from typing import Dict, Any
from fastapi import APIRouter

from bfsa.controllers.media import media_controller
from bfsa.utils.return_json import return_json
from bfsa.utils.logger import logger as log


router = APIRouter()


@router.patch("/api/updateManyMedia")
def update_many_media(
    where: Dict[str, Any],
    patch: Dict[str, Any],
):
    """
    Update many media
    """
    log.info("Calling update_many_media")
    media = None
    try:
        media = media_controller.read_media(where=where)
    except Exception as e:
        log.critical(f"Error calling read_media. Error: {e}")

    for i, medium in enumerate(media["media"]):
        guid = medium["id"]
        medium.update(patch)
        try:
            media_controller.update_media(
                guid,
                medium,
            )
        except Exception as e:
            log.error(
                f"Error calling update_media on media with id: {guid} and index: {i}. Error: {e}"
            )

    return return_json(
        message="Successfully updated multiple media documents.",
        success=True,
    )
