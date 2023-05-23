#!
# -*- coding: utf-8 -*-
"""
Created on 2022-07-16
@author: Edmund Bennett
@email: bennettedmund@gmail.com
"""

from typing import Dict, Any
from io import BytesIO
from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel

from bfsa.db.environment import client_factory
from bfsa.db.client import get_blob_credentials
from bfsa.blob.blob_service_client import upload_blob, delete_blob
from bfsa.sql.create_select import create_select
from bfsa.utils.return_json import return_json
from bfsa.utils.create_guid import create_guid
from bfsa.utils.logger import logger as log


router = APIRouter()


class EquipmentModel(BaseModel):
    """
    Pydantic model for equipment
    """

    name: str
    description: str


@router.post("/api/createEquipment")
def create_equipment(
    equipment: EquipmentModel,
):
    """
    Add equipment object to database
    """
    log.info("Calling create_equipment")

    client = client_factory()

    equipment_dict = dict(equipment)
    equipment_dict.update({"id": create_guid()})
    equipment_dict.update({"partitionKey": "equipment"})

    try:
        success = client.insert_data(
            [equipment_dict],
        )
        if not success:
            log.critical(f"Failed to insert equipment. Check logs for details.")
            return return_json(
                message="Failed to insert equipment.",
                success=False,
            )
    except Exception as e:
        log.critical(f"Failed to insert equipment. Error: {e}")
        return return_json(
            message="Failed to insert equipment.",
            success=False,
        )

    return return_json(
        message="Successfully inserted equipment.",
        success=True,
    )


@router.put("/api/putEquipmentImage")
async def put_equipment_image(
    equipment_id: str,
    image: UploadFile = File(...),
):
    """
    Put equipment image
    """
    log.info("Calling put_equipment_image")

    # check inputs

    if image.filename == "":
        return return_json(
            "No file selected for uploading.",
            success=False,
        )

    if (
        image
        and "." in image.filename
        and image.filename.rsplit(".", 1)[1].lower()
        not in ["png", "bmp", "jpg", "jpeg"]
    ):
        return return_json(
            "Invalid image file.",
            success=False,
        )

    # pre-amble

    client = client_factory()

    # insert data - blob first then metadata

    blob_credentials = get_blob_credentials()

    try:
        blob_url = upload_blob(
            connection=blob_credentials["credentials"],
            container="recipe-photos",
            guid=equipment_id,
            filename=image.filename,
            file=BytesIO(await image.read()),
            overwrite=True,
        )

    except Exception as e:
        log.critical(f"Failed to insert equipment image. Error: {e}")
        return return_json(
            message="Failed to insert equipment image.",
            success=False,
        )

    response = read_equipment(where={"id": equipment_id})

    if response["success"]:
        content = response["content"]
        if content:
            equipment_dict = content[0]
            if (
                "blob_url" in equipment_dict.keys()
                and equipment_dict["blob_url"] == blob_url
            ):
                return return_json(
                    message="Successfully updated equipment image.",
                    success=True,
                )

            equipment_dict.update({"blob_url": blob_url})

            try:
                cosmos_success = client.update_data(
                    item={"id": equipment_id, "partitionKey": "equipment"},
                    body=equipment_dict,
                    upsert=False,
                )
                if not cosmos_success:
                    log.critical(
                        f"Failed to insert equipment image. Check logs for details."
                    )

            except Exception as e:
                cosmos_success = False
                log.critical(f"Failed to insert equipment image. Error: {e}")

            if cosmos_success:
                return return_json(
                    message="Successfully inserted equipment image.",
                    success=True,
                )

    # Are you still here? Then blob insertion succeeded but Cosmos insertion failed
    # roll back by deleting blob

    try:
        response = delete_equipment_image(
            photo_id=equipment_id,
        )
        # TODO: indicate whether roll back was successful
        return return_json(
            message="Failed to insert equipment image.",
            success=False,
        )
    except Exception as e:
        log.critical(
            f"Failed to insert equipment image. Check blob storage for orphaned blobs. Error: {e}"
        )
        return return_json(
            message="Failed to insert equipment image.",
            success=False,
        )


@router.get("/api/deleteEquipmentImage")
def delete_equipment_image(
    equipment_id: str,
):
    log.info("Calling delete_equipment_image")

    blob_credentials = get_blob_credentials()

    response = read_equipment(where={"id": equipment_id})

    if response["success"]:
        target_equipment = response["content"][0]
        if "blob_url" in target_equipment.keys() and target_equipment["blob_url"]:

            try:
                success = delete_blob(
                    connection=blob_credentials["credentials"],
                    container="recipe-photos",
                    url=target_equipment["blob_url"],
                )

            except Exception as e:
                log.critical(f"Failed to delete equipment image. Error: {e}")
                return return_json(
                    message="Failed to delete equipment image.",
                    success=False,
                )
        else:
            log.info(f"No equipment image to delete.")
            return return_json(
                message="No equipment image to delete.",
                success=True,
            )

    return return_json(
        message="Successfully deleted equipment image.",
        success=True,
    )


@router.get("/api/readEquipments")
def read_equipment(
    where: Dict[str, Any] = None,
):
    """
    Read equipment
    """
    log.info("Calling read_equipment")

    client = client_factory()

    if where is None:
        where = {}
    where.update({"partitionKey": "equipment"})

    query = create_select(where)

    try:
        data = client.select_data(
            query=query,
        )
        if data:
            return return_json(
                message="Successfully selected equipment data.",
                success=True,
                content=data,
            )
    except Exception as e:
        log.critical(f"Failed to select equipment data. Error: {e}")
        return return_json(
            message="Failed to select equipment data.",
            success=False,
        )

    log.critical(f"Failed to select equipment data. Check logs for details.")
    return return_json(
        message="Failed to select equipment data.",
        success=False,
    )


@router.patch("/api/updateEquipment")
def update_equipment(
    equipment_id: str,
    patch: Dict[str, Any],
):
    """
    Update equipment
    """
    log.info("Calling update_equipment")

    client = client_factory()

    patch.update({"id": equipment_id})
    patch.update({"partitionKey": "equipment"})

    try:
        success = client.update_data(
            item={"id": equipment_id, "partitionKey": "equipment"},
            body=patch,
            upsert=False,
        )
        if not success:
            log.critical(f"Failed to update equipment. Check logs for details.")
            return return_json(
                message="Failed to update equipment.",
                success=False,
            )
    except Exception as e:
        log.critical(f"Failed to update equipment. Error: {e}")
        return return_json(
            message="Failed to update equipment.",
            success=False,
        )

    return return_json(
        message="Successfully updated equipment.",
        success=True,
    )


@router.delete("/api/deleteEquipment")
def delete_equipment(
    equipment_id: str,
):
    """
    Delete equipment
    """
    log.info("Calling delete_equipment")

    client = client_factory()

    response = delete_equipment_image(
        equipment_id=equipment_id,
    )

    if response["success"]:

        try:
            success = client.delete_data(
                item=equipment_id,
                partition_key="equipment",
            )
            if not success:
                log.critical(f"Failed to delete equipment. Check logs for details.")
                return return_json(
                    message="Failed to delete equipment.",
                    success=False,
                )
        except Exception as e:
            log.critical(f"Failed to delete equipment. Error: {e}")
            return return_json(
                message="Failed to delete equipment.",
                success=False,
            )
    else:
        log.critical(f"Failed to delete equipment blob.")
        return return_json(
            message="Failed to delete equipment blob.",
            success=False,
        )

    return return_json(
        message="Successfully deleted equipment.",
        success=True,
    )
