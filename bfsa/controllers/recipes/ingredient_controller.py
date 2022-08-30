#!
# -*- coding: utf-8 -*-
"""
Created on 2022-07-16
@author: Edmund Bennett
@email: bennettedmund@gmail.com
"""

from typing import Dict, Any
from fastapi import APIRouter
from pydantic import BaseModel

from bfsa.db.environment import Environment
from bfsa.db.client import Client
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
