#!
# -*- coding: utf-8 -*-
"""
Created on 2022-07-16
@author: Edmund Bennett
@email: bennettedmund@gmail.com
"""

from typing import Dict, Any
from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel

from bfsa.db.environment import Environment
from bfsa.db.client import Client, get_blob_credentials
from bfsa.blob.blob_service_client import upload_blob, delete_blob
from bfsa.sql.create_select import create_select
from bfsa.utils.return_json import return_json
from bfsa.utils.create_guid import create_guid
from bfsa.utils.logger import logger as log


router = APIRouter()


class IngredientModel(BaseModel):
    """
    Pydantic model for ingredient
    """
    name: str
    description: str


@router.post("/api/createIngredient")
def create_ingredient(
    ingredient: IngredientModel,
):
    """
    Add ingredient object to database
    """
    log.info("Calling create_ingredient")

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

    ingredient_dict = dict(ingredient)
    ingredient_dict.update({"id": create_guid()})
    ingredient_dict.update({"partitionKey": "ingredients"})

    try:
        success = client.insert_data(
            [ingredient_dict],
        )
        if not success:
            log.critical(f"Failed to insert ingredient. Check logs for details.")
            return return_json(
                message="Failed to insert ingredient.",
                success=False,
            )
    except Exception as e:
        log.critical(f"Failed to insert ingredient. Error: {e}")
        return return_json(
            message="Failed to insert ingredient.",
            success=False,
        )

    return return_json(
        message="Successfully inserted ingredient.",
        success=True,
    )


@router.put("/api/putIngredientImage")
def put_ingredient_image(
    ingredient_id: str,
    image: UploadFile = File(...),
):
    """
    Put ingredient image
    """
    log.info("Calling put_ingredient_image")

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

    blob_credentials = get_blob_credentials()

    try:
        blob_url = upload_blob(
            connection=blob_credentials["credentials"],
            container="recipe-photos",
            guid=ingredient_id,
            file=image,
            overwrite=True,
        )

    except Exception as e:
        log.critical(f"Failed to insert ingredient image. Error: {e}")
        return return_json(
            message="Failed to insert ingredient image.",
            success=False,
        )

    response = read_ingredients(where={"id": ingredient_id})

    if response["success"]:
        content = response["content"]
        if content:
            ingredient_dict = content[0]
            if "blob_url" in ingredient_dict.keys() and ingredient_dict["blob_url"] == blob_url:
                return return_json(
                    message="Successfully updated ingredient image.",
                    success=True,
                )

            ingredient_dict.update({"blob_url": blob_url})

            try:
                cosmos_success = client.update_data(
                    item={"id": ingredient_id, "partitionKey": "ingredients"},
                    body=ingredient_dict,
                    upsert=False,
                )
                if not cosmos_success:
                    log.critical(f"Failed to insert ingredient image. Check logs for details.")

            except Exception as e:
                cosmos_success = False
                log.critical(f"Failed to insert ingredient image. Error: {e}")

            if cosmos_success:
                return return_json(
                    message="Successfully inserted ingredient image.",
                    success=True,
                )

    # Are you still here? Then blob insertion succeeded but Cosmos insertion failed
    # roll back by deleting blob

    try:
        response = delete_ingredient_image(
            photo_id=ingredient_id,
        )
        # TODO: indicate whether roll back was successful
        return return_json(
            message="Failed to insert ingredient image.",
            success=False,
        )
    except Exception as e:
        log.critical(f"Failed to insert ingredient image. Check blob storage for orphaned blobs. Error: {e}")
        return return_json(
            message="Failed to insert ingredient image.",
            success=False,
        )


@router.get("/api/deleteIngredientImage")
def delete_ingredient_image(
    ingredient_id: str,
):
    log.info("Calling delete_ingredient_image")

    blob_credentials = get_blob_credentials()

    try:
        success = delete_blob(
            connection=blob_credentials["credentials"],
            container="recipe-photos",
            url="",
        )

    except Exception as e:
        log.critical(f"Failed to delete ingredient image. Error: {e}")
        return return_json(
            message="Failed to delete ingredient image.",
            success=False,
        )

    return return_json(
        message="Successfully deleted ingredient image.",
        success=True,
    )


@router.get("/api/readIngredients")
def read_ingredients(
    where: Dict[str, Any] = None,
):
    """
    Read ingredients
    """
    log.info("Calling read_ingredients")

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
    where.update({"partitionKey": "ingredients"})

    query = create_select(where)

    try:
        data = client.select_data(
            query=query,
        )
        if data:
            return return_json(
                message="Successfully selected ingredient data.",
                success=True,
                content=data,
            )
    except Exception as e:
        log.critical(f"Failed to select ingredient data. Error: {e}")
        return return_json(
            message="Failed to select ingredient data.",
            success=False,
        )

    log.critical(f"Failed to select ingredient data. Check logs for details.")
    return return_json(
        message="Failed to select ingredient data.",
        success=False,
    )


@router.patch("/api/updateIngredient")
def update_ingredient(
    ingredient_id: str,
    patch: Dict[str, Any],
):
    """
    Update ingredient
    """
    log.info("Calling update_ingredient")

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

    patch.update({"id": ingredient_id})
    patch.update({"partitionKey": "ingredients"})

    try:
        success = client.update_data(
            item={"id": ingredient_id, "partitionKey": "ingredients"},
            body=patch,
            upsert=False,
        )
        if not success:
            log.critical(f"Failed to update ingredient. Check logs for details.")
            return return_json(
                message="Failed to update ingredient.",
                success=False,
            )
    except Exception as e:
        log.critical(f"Failed to update ingredient. Error: {e}")
        return return_json(
            message="Failed to update ingredient.",
            success=False,
        )

    return return_json(
        message="Successfully updated ingredient.",
        success=True,
    )


@router.delete("/api/deleteIngredient")
def delete_ingredient(
    ingredient_id: str,
):
    """
    Delete ingredient
    """
    log.info("Calling delete_ingredient")

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

    response = delete_ingredient_image(
        ingredient_id=ingredient_id,
    )

    try:
        success = client.delete_data(
            item=ingredient_id,
            partition_key="ingredients",
        )
        if not success:
            log.critical(f"Failed to delete ingredient. Check logs for details.")
            return return_json(
                message="Failed to delete ingredient.",
                success=False,
            )
    except Exception as e:
        log.critical(f"Failed to delete ingredient. Error: {e}")
        return return_json(
            message="Failed to delete ingredient.",
            success=False,
        )

    return return_json(
        message="Successfully deleted ingredient.",
        success=True,
    )
