#!
# -*- coding: utf-8 -*-
"""
Created on 2022-07-16
@author: Edmund Bennett
@email: bennettedmund@gmail.com
"""

from typing import Dict, Any, Optional
from io import BytesIO
from fastapi import APIRouter, UploadFile, File

from bfsa.db.environment import client_factory
from bfsa.db.client import get_blob_credentials
from bfsa.controllers.environment import Environment as Base
from bfsa.blob.blob_service_client import upload_blob, delete_blob
from bfsa.sql.create_select import create_select
from bfsa.utils.return_json import return_json
from bfsa.utils.create_guid import create_guid
from bfsa.utils.logger import logger as log


router = APIRouter()

environment = Base()

#    @       @
#     @     @
#   @@@@@@@@@@@
#  @@@ @@@@@ @@@
# @@@@@@@@@@@@@@@
# @  @@@@@@@@@  @
# @  @       @  @
#     @@   @@


@router.post("/api/createContent")
def create_content(
    name: str,
    file_format: str,
    file: UploadFile = File(...),
    height: Optional[float] = None,
    width: Optional[float] = None,
    description: Optional[str] = None,
    camera_details: Optional[str] = None,
    taken_by: Optional[str] = None,
    taken_date: Optional[str] = None,
):
    """
    Add content object to database
    """
    log.info("Calling create_content")

    allowed_media_extensions = ["png", "bmp", "jpg", "jpeg", "mp4"]

    # check inputs

    if file.filename == "":
        return return_json(
            "No file selected for uploading.",
            success=False,
        )

    if (
        file
        and "." in file.filename
        and file.filename.rsplit(".", 1)[1].lower() not in allowed_media_extensions
    ):
        return return_json(
            "Invalid image file.",
            success=False,
        )

    # pre-amble

    client = client_factory()

    # insert data - blob first then metadata

    guid = create_guid()

    blob_credentials = get_blob_credentials()

    try:
        blob_url = upload_blob(
            connection=blob_credentials["credentials"],
            container="media",
            guid=guid,
            filename=file.filename,
            file=BytesIO(await file.read()),
            overwrite=False,
        )

    except Exception as e:
        log.critical(f"Failed to insert content. Error: {e}")
        return return_json(
            message="Failed to insert content.",
            success=False,
        )

    content_dict = {
        "name": name,
        "description": description,
        "file_format": file_format,
        "height": height,
        "width": width,
        "camera_details": camera_details,
        "taken_by": taken_by,
        "taken_date": taken_date,
        "blob_url": blob_url,
        "id": guid,
        "partitionKey": "photo",
    }

    try:
        cosmos_success = client.insert_data(
            [content_dict],
        )
        if not cosmos_success:
            log.critical(f"Failed to insert content. Check logs for details.")

    except Exception as e:
        cosmos_success = False
        log.critical(f"Failed to insert content. Error: {e}")

    if cosmos_success:
        return return_json(
            message="Successfully inserted content.",
            success=True,
        )

    # Are you still here? Then blob insertion succeeded but Cosmos insertion failed
    # roll back by deleting blob

    try:
        response = delete_content(
            content_id=guid,
        )
        # TODO: indicate whether roll back was successful
        return return_json(
            message="Failed to insert content.",
            success=False,
        )
    except Exception as e:
        log.critical(
            f"Failed to insert content. Check blob storage for orphaned blobs. Error: {e}"
        )
        return return_json(
            message="Failed to insert content.",
            success=False,
        )


@router.get("/api/readContent")
def read_content(
    where: Dict[str, Any] = None,
):
    """
    Read content
    """
    log.info("Calling read_content")

    client = client_factory()

    if where is None:
        where = {}
    where.update({"partitionKey": "photo"})

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


@router.patch("/api/updateContentMetadata")
def update_content_metadata(
    content_id: str,
    patch: Dict[str, Any],
):
    """
    Update content metadata
    """
    log.info("Calling update_content_metadata")

    client = client_factory()

    patch.update({"id": content_id})
    patch.update({"partitionKey": "photo"})

    try:
        success = client.update_data(
            item={"id": content_id, "partitionKey": "photo"},
            body=patch,
            upsert=False,
        )
        if not success:
            log.critical(f"Failed to update content metadata. Check logs for details.")
            return return_json(
                message="Failed to update content metadata.",
                success=False,
            )
    except Exception as e:
        log.critical(f"Failed to update content metadata. Error: {e}")
        return return_json(
            message="Failed to update content metadata.",
            success=False,
        )

    return return_json(
        message="Successfully updated content metadata.",
        success=True,
    )


@router.delete("/api/deleteContent")
def delete_content(
    content_id: str,
):
    """
    Delete content
    """
    log.info("Calling delete_content")

    client = client_factory()

    blob_credentials = get_blob_credentials()

    try:
        content_details = read_content(where={"id": content_id})
    except Exception as e:
        log.critical(f"Failed to read content. Error: {e}")
        return return_json(
            message="Failed to read content.",
            success=False,
        )

    try:
        success = client.delete_data(
            item=content_id,
            partition_key="photo",
        )
        if not success:
            log.critical(f"Failed to delete content. Check logs for details.")
            return return_json(
                message="Failed to delete content.",
                success=False,
            )

        blob_delete_success = delete_blob(
            connection=blob_credentials["credentials"],
            container="media",
            url=content_details["content"][0]["blob_url"],
        )

        if blob_delete_success:
            ...

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
