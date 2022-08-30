#!
# -*- coding: utf-8 -*-
"""
Created on 2022-07-16
@author: Edmund Bennett
@email: bennettedmund@gmail.com
"""

from typing import Dict, Any, List
from fastapi import APIRouter
from pydantic import BaseModel

from bfsa.db.environment import Environment
from bfsa.db.client import Client
from bfsa.sql.create_select import create_select
from bfsa.utils.return_json import return_json
from bfsa.utils.create_guid import create_guid
from bfsa.utils.logger import logger as log


router = APIRouter()


class RecipeModel(BaseModel):
    """
    Pydantic model for recipe
    """
    name: str
    description: str
    duration_in_minutes: int
    added_date: str
    source: str
    steps: List[str]
    equipment: List[str]
    tags: List[str]


@router.post("/api/createRecipe")
def create_recipe(
    recipe: RecipeModel,
):
    """
    Add recipe object to database
    """
    log.info("Calling create_recipe")

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

    recipe_dict = dict(recipe)
    recipe_dict.update({"id": create_guid()})
    recipe_dict.update({"partitionKey": "recipes"})

    try:
        success = client.insert_data(
            [recipe_dict],
        )
        if not success:
            log.critical(f"Failed to insert recipe. Check logs for details.")
            return return_json(
                message="Failed to insert recipe.",
                success=False,
            )
    except Exception as e:
        log.critical(f"Failed to insert recipe. Error: {e}")
        return return_json(
            message="Failed to insert recipe.",
            success=False,
        )

    return return_json(
        message="Successfully inserted recipe.",
        success=True,
    )


@router.get("/api/readRecipes")
def read_recipes(
    where: Dict[str, Any] = None,
):
    """
    Read recipes
    """
    log.info("Calling read_recipes")

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
    where.update({"partitionKey": "recipes"})

    query = create_select(where)

    try:
        data = client.select_data(
            query=query,
        )
        if data:
            return return_json(
                message="Successfully selected recipe data.",
                success=True,
                content=data,
            )
    except Exception as e:
        log.critical(f"Failed to select recipe data. Error: {e}")
        return return_json(
            message="Failed to select recipe data.",
            success=False,
        )

    log.critical(f"Failed to select recipe data. Check logs for details.")
    return return_json(
        message="Failed to select recipe data.",
        success=False,
    )


@router.patch("/api/updateRecipe")
def update_recipe(
    recipe_id: str,
    patch: Dict[str, Any],
):
    """
    Update recipe
    """
    log.info("Calling update_recipe")

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

    patch.update({"id": recipe_id})
    patch.update({"partitionKey": "recipes"})

    try:
        success = client.update_data(
            item={"id": recipe_id, "partitionKey": "recipes"},
            body=patch,
            upsert=False,
        )
        if not success:
            log.critical(f"Failed to update recipe. Check logs for details.")
            return return_json(
                message="Failed to update recipe.",
                success=False,
            )
    except Exception as e:
        log.critical(f"Failed to update recipe. Error: {e}")
        return return_json(
            message="Failed to update recipe.",
            success=False,
        )

    return return_json(
        message="Successfully updated recipe.",
        success=True,
    )


@router.delete("/api/deleteRecipe")
def delete_recipe(
    recipe_id: str,
):
    """
    Delete recipe
    """
    log.info("Calling delete_recipe")

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
            item=recipe_id,
            partition_key="recipes",
        )
        if not success:
            log.critical(f"Failed to delete recipe. Check logs for details.")
            return return_json(
                message="Failed to delete recipe.",
                success=False,
            )
    except Exception as e:
        log.critical(f"Failed to delete recipe. Error: {e}")
        return return_json(
            message="Failed to delete recipe.",
            success=False,
        )

    return return_json(
        message="Successfully deleted recipe.",
        success=True,
    )
