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

from bfsa.db.environment import Environment
from bfsa.db.client import Client
from bfsa.sql.create_select import create_select
from bfsa.utils.return_json import return_json
from bfsa.utils.create_guid import create_guid
from bfsa.utils.logger import logger as log


router = APIRouter()


class ContentModel(BaseModel):
    """
    Pydantic model for content
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
    media: ContentModel,
):
    """
    Add content object to database
    """
    log.info("Calling create_media")

    db_config = Environment.load_db_credentials()

    try:
        client = Client(
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

    media_dict = dict(media)
    media_dict.update({"id": create_guid()})
    media_dict.update({"partitionKey": "content"})

    try:
        success = client.insert_data(
            [media_dict],
        )
        if not success:
            log.critical(f"Failed to insert content. Check logs for details.")
            return return_json(
                message="Failed to insert content.",
                success=False,
            )
    except Exception as e:
        log.critical(f"Failed to insert content. Error: {e}")
        return return_json(
            message="Failed to insert content.",
            success=False,
        )

    return return_json(
        message="Successfully inserted content.",
        success=True,
    )


@router.get("/api/readMedia")
def read_media(
    where: Dict[str, Any] = None,
):
    """
    Read content
    """
    log.info("Calling read_media")

    db_config = Environment.load_db_credentials()

    try:
        client = Client(
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

    if where is None:
        where = {}
    where.update({"partitionKey": "content"})

    query = create_select(where)

    try:
        data = client.select_data(
            query=query,
        )
        if data:
            return return_json(
                message="Successfully selected content data.",
                success=True,
                content=data,
            )
    except Exception as e:
        log.critical(f"Failed to select content data. Error: {e}")
        return return_json(
            message="Failed to select content data.",
            success=False,
        )

    log.critical(f"Failed to select content data. Check logs for details.")
    return return_json(
        message="Failed to select content data.",
        success=False,
    )


@router.patch("/api/updateMedia")
def update_media(
    media_id: str,
    patch: Dict[str, Any],
):
    """
    Update content
    """
    log.info("Calling update_media")

    db_config = Environment.load_db_credentials()

    try:
        client = Client(
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

    patch.update({"id": media_id})
    patch.update({"partitionKey": "content"})

    try:
        success = client.update_data(
            item={"id": media_id, "partitionKey": "content"},
            body=patch,
            upsert=False,
        )
        if not success:
            log.critical(f"Failed to update content. Check logs for details.")
            return return_json(
                message="Failed to update content.",
                success=False,
            )
    except Exception as e:
        log.critical(f"Failed to update content. Error: {e}")
        return return_json(
            message="Failed to update content.",
            success=False,
        )

    return return_json(
        message="Successfully updated content.",
        success=True,
    )


@router.delete("/api/deleteMedia")
def delete_media(
    media_id: str,
):
    """
    Delete content
    """
    log.info("Calling delete_media")

    db_config = Environment.load_db_credentials()

    try:
        client = Client(
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

    try:
        success = client.delete_data(
            item=media_id,
            partition_key="content",
        )
        if not success:
            log.critical(f"Failed to delete content. Check logs for details.")
            return return_json(
                message="Failed to delete content.",
                success=False,
            )
    except Exception as e:
        log.critical(f"Failed to delete content. Error: {e}")
        return return_json(
            message="Failed to delete content.",
            success=False,
        )

    return return_json(
        message="Successfully deleted content.",
        success=True,
    )
