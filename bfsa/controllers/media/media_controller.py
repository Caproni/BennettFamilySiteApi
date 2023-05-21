#!
# -*- coding: utf-8 -*-
"""
Created on 2022-07-16
@author: Edmund Bennett
@email: bennettedmund@gmail.com
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter
from pydantic import BaseModel

from bfsa.db.environment import client_factory
from bfsa.sql.create_select import create_select
from bfsa.utils.return_json import return_json
from bfsa.utils.create_guid import create_guid
from bfsa.utils.logger import logger as log


router = APIRouter()


class MediaModel(BaseModel):
    """
    Pydantic model for media
    """

    director: Optional[str]
    title: str
    publisher: Optional[str]
    actors: Optional[str]
    format: Optional[str]
    release_year: Optional[int]
    series_or_film: Optional[str]
    fiction: Optional[str]
    episodes: Optional[str]
    duration_in_minutes: Optional[int]
    language: Optional[str]
    location: Optional[str]


@router.post("/api/createMedia")
def create_media(
    media: MediaModel,
):
    """
    Add media object to database
    """
    log.info("Calling create_media")

    client = client_factory()

    media_dict = dict(media)
    media_dict.update({"id": create_guid()})
    media_dict.update({"partitionKey": "media"})

    try:
        success = client.insert_data(
            [media_dict],
        )
        if not success:
            log.critical(f"Failed to insert media. Check logs for details.")
            return return_json(
                message="Failed to insert media.",
                success=False,
            )
    except Exception as e:
        log.critical(f"Failed to insert media. Error: {e}")
        return return_json(
            message="Failed to insert media.",
            success=False,
        )

    return return_json(
        message="Successfully inserted media.",
        success=True,
    )


@router.get("/api/readMedia")
def read_media(
    where: Dict[str, Any] = None,
):
    """
    Read media
    """
    log.info("Calling read_media")

    client = client_factory()

    if where is None:
        where = {}
    where.update({"partitionKey": "media"})

    query = create_select(where)

    try:
        data = client.select_data(
            query=query,
        )
        if data:
            return return_json(
                message="Successfully selected media data.",
                success=True,
                content=data,
            )
    except Exception as e:
        log.critical(f"Failed to select media data. Error: {e}")
        return return_json(
            message="Failed to select media data.",
            success=False,
        )

    log.critical(f"Failed to select media data. Check logs for details.")
    return return_json(
        message="Failed to select media data.",
        success=False,
    )


@router.patch("/api/updateMedia")
def update_media(
    media_id: str,
    patch: Dict[str, Any],
):
    """
    Update media
    """
    log.info("Calling update_media")

    client = client_factory()

    patch.update({"id": media_id})
    patch.update({"partitionKey": "media"})

    try:
        success = client.update_data(
            item={"id": media_id, "partitionKey": "media"},
            body=patch,
            upsert=False,
        )
        if not success:
            log.critical(f"Failed to update media. Check logs for details.")
            return return_json(
                message="Failed to update media.",
                success=False,
            )
    except Exception as e:
        log.critical(f"Failed to update media. Error: {e}")
        return return_json(
            message="Failed to update media.",
            success=False,
        )

    return return_json(
        message="Successfully updated media.",
        success=True,
    )


@router.delete("/api/deleteMedia")
def delete_media(
    media_id: str,
):
    """
    Delete media
    """
    log.info("Calling delete_media")

    client = client_factory()

    try:
        success = client.delete_data(
            item=media_id,
            partition_key="media",
        )
        if not success:
            log.critical(f"Failed to delete media. Check logs for details.")
            return return_json(
                message="Failed to delete media.",
                success=False,
            )
    except Exception as e:
        log.critical(f"Failed to delete media. Error: {e}")
        return return_json(
            message="Failed to delete media.",
            success=False,
        )

    return return_json(
        message="Successfully deleted media.",
        success=True,
    )
