#!
# -*- coding: utf-8 -*-
"""
Created on 2022-07-16
@author: Edmund Bennett
@email: bennettedmund@gmail.com
"""

from typing import Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, UploadFile, File

from bfsa.db.environment import Environment
from bfsa.db.client import Client, get_blob_credentials
from bfsa.controllers.environment import Environment as Base
from bfsa.blob.blob_service_client import upload_blob, delete_blob, read_blobs
from bfsa.sql.create_select import create_select
from bfsa.utils.return_json import return_json
from bfsa.utils.create_guid import create_guid
from bfsa.utils.logger import logger as log


router = APIRouter()

environment = Base()


@router.post("/api/createPhoto")
def create_photo(
    name: str,
    height: float,
    width: float,
    image: UploadFile = File(...),
    description: Optional[str] = None,
    camera_details: Optional[str] = None,
    taken_by: Optional[str] = None,
    taken_date: Optional[str] = None,
):
    """
    Add photo object to database
    """
    log.info("Calling create_photo")

    # check inputs

    if image.filename == "":
        return return_json(
            "No file selected for uploading.",
            success=False,
        )

    if (
        image
        and "." in image.filename
        and image.filename.rsplit(".", 1)[1].lower() not in ["png", "bmp", "jpg", "jpeg"]
    ):
        return return_json(
            "Invalid image file.",
            success=False,
        )

    # pre-amble

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

    # insert data - blob first then metadata

    id = create_guid()

    blob_credentials = get_blob_credentials(environment["IS_PROD"])

    try:
        blob_url = upload_blob(
            connection=blob_credentials["credentials"],
            container="photos",
            id=id,
            file=image,
            overwrite=False,
        )

    except Exception as e:
        log.critical(f"Failed to insert photo. Error: {e}")
        return return_json(
            message="Failed to insert photo.",
            success=False,
        )


    photo_dict = {
        "name": name,
        "description": description,
        "height": height,
        "width": width,
        "camera_details": camera_details,
        "taken_by": taken_by,
        "taken_date": taken_date,
        "blob_url": blob_url,
        "id": id,
        "partitionKey": "photo",
    }

    try:
        cosmos_success = client.insert_data(
            [photo_dict],
        )
        if not cosmos_success:
            log.critical(f"Failed to insert photo. Check logs for details.")

    except Exception as e:
        cosmos_success = False
        log.critical(f"Failed to insert photo. Error: {e}")

    if cosmos_success:
        return return_json(
            message="Successfully inserted photo.",
            success=True,
        )

    # Are you still here? Then blob insertion succeeded but Cosmos insertion failed
    # roll back by deleting blob

    try:
        response = delete_photo(
            photo_id=id,
        )
        # TODO: indicate whether roll back was successful
        return return_json(
            message="Failed to insert photo.",
            success=False,
        )
    except Exception as e:
        log.critical(f"Failed to insert photo. Check blob storage for orphaned blobs. Error: {e}")
        return return_json(
            message="Failed to insert photo.",
            success=False,
        )



@router.get("/api/readPhotos")
def read_photos(
    where: Dict[str, Any] = None,
):
    """
    Read photo
    """
    log.info("Calling read_photos")

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
    where.update({"partitionKey": "photo"})

    query = create_select(where)

    try:
        data = client.select_data(
            query=query,
        )
        if data:
            return return_json(
                message="Successfully selected photo data.",
                success=True,
                content=data,
            )
    except Exception as e:
        log.critical(f"Failed to select photo data. Error: {e}")
        return return_json(
            message="Failed to select photo data.",
            success=False,
        )

    log.critical(f"Failed to select photo data. Check logs for details.")
    return return_json(
        message="Failed to select photo data.",
        success=False,
    )


@router.patch("/api/updatePhotoMetadata")
def update_photo_metadata(
    photo_id: str,
    patch: Dict[str, Any],
):
    """
    Update photo
    """
    log.info("Calling update_photo_metadata")

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

    patch.update({"id": photo_id})
    patch.update({"partitionKey": "photo"})

    try:
        success = client.update_data(
            item={"id": photo_id, "partitionKey": "photo"},
            body=patch,
            upsert=False,
        )
        if not success:
            log.critical(f"Failed to update photo metadata. Check logs for details.")
            return return_json(
                message="Failed to update photo metadata.",
                success=False,
            )
    except Exception as e:
        log.critical(f"Failed to update photo metadata. Error: {e}")
        return return_json(
            message="Failed to update photo metadata.",
            success=False,
        )

    return return_json(
        message="Successfully updated photo metadata.",
        success=True,
    )


@router.delete("/api/deletePhoto")
def delete_photo(
    photo_id: str,
):
    """
    Delete photo
    """
    log.info("Calling delete_photo")

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

    blob_credentials = get_blob_credentials(environment["IS_PROD"])

    try:
        success = client.delete_data(
            item=photo_id,
            partition_key="photo",
        )
        if not success:
            log.critical(f"Failed to delete photo. Check logs for details.")
            return return_json(
                message="Failed to delete photo.",
                success=False,
            )

        blob_success = delete_blob(
            connection=blob_credentials["credentials"],
            container="photos",
            unique_name="",
        )

    except Exception as e:
        log.critical(f"Failed to delete photo. Error: {e}")
        return return_json(
            message="Failed to delete photo.",
            success=False,
        )

    return return_json(
        message="Successfully deleted photo.",
        success=True,
    )
