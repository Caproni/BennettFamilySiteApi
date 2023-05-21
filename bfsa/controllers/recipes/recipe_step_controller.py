#!
# -*- coding: utf-8 -*-
"""
Created on 2022-07-16
@author: Edmund Bennett
@email: bennettedmund@gmail.com
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter
from pydantic import BaseModel

from bfsa.db.environment import client_factory
from bfsa.sql.create_select import create_select
from bfsa.utils.return_json import return_json
from bfsa.utils.create_guid import create_guid
from bfsa.utils.logger import logger as log


router = APIRouter()


class RecipeStepModel(BaseModel):
    """
    Pydantic model for recipe step
    """

    name: str
    index: int
    recipe_id: str
    description: Optional[str]
    image: Optional[str]
    ingredients_used: List[str]
    equipment_used: List[str]


@router.post("/api/createRecipeStep")
def create_recipe_step(
    recipe_step: RecipeStepModel,
):
    """
    Add recipe step object to database
    """
    log.info("Calling create_recipe_step")

    client = client_factory()

    recipe_step_dict = dict(recipe_step)
    recipe_step_dict.update({"id": create_guid()})
    recipe_step_dict.update({"partitionKey": "recipe-steps"})

    try:
        success = client.insert_data(
            [recipe_step_dict],
        )
        if not success:
            log.critical(f"Failed to insert recipe_step. Check logs for details.")
            return return_json(
                message="Failed to insert recipe_step.",
                success=False,
            )
    except Exception as e:
        log.critical(f"Failed to insert recipe_step. Error: {e}")
        return return_json(
            message="Failed to insert recipe_step.",
            success=False,
        )

    return return_json(
        message="Successfully inserted recipe_step.",
        success=True,
    )


@router.get("/api/readRecipeSteps")
def read_recipe_steps(
    where: Dict[str, Any] = None,
):
    """
    Read recipe steps
    """
    log.info("Calling read_recipe_steps")

    client = client_factory()

    if where is None:
        where = {}
    where.update({"partitionKey": "recipe-steps"})

    query = create_select(where)

    try:
        data = client.select_data(
            query=query,
        )
        if data:
            return return_json(
                message="Successfully selected recipe_step data.",
                success=True,
                content=data,
            )
    except Exception as e:
        log.critical(f"Failed to select recipe_step data. Error: {e}")
        return return_json(
            message="Failed to select recipe_step data.",
            success=False,
        )

    log.critical(f"Failed to select recipe_step data. Check logs for details.")
    return return_json(
        message="Failed to select recipe_step data.",
        success=False,
    )


@router.patch("/api/updateRecipeStep")
def update_recipe_step(
    recipe_step_id: str,
    patch: Dict[str, Any],
):
    """
    Update recipe step
    """
    log.info("Calling update_recipe_step")

    client = client_factory()

    patch.update({"id": recipe_step_id})
    patch.update({"partitionKey": "recipe-steps"})

    try:
        success = client.update_data(
            item={"id": recipe_step_id, "partitionKey": "recipe-steps"},
            body=patch,
            upsert=False,
        )
        if not success:
            log.critical(f"Failed to update recipe_step. Check logs for details.")
            return return_json(
                message="Failed to update recipe_step.",
                success=False,
            )
    except Exception as e:
        log.critical(f"Failed to update recipe_step. Error: {e}")
        return return_json(
            message="Failed to update recipe_step.",
            success=False,
        )

    return return_json(
        message="Successfully updated recipe_step.",
        success=True,
    )


@router.delete("/api/deleteRecipeStep")
def delete_recipe_step(
    recipe_step_id: str,
):
    """
    Delete recipe step
    """
    log.info("Calling delete_recipe")

    client = client_factory()

    try:
        success = client.delete_data(
            item=recipe_step_id,
            partition_key="recipe-steps",
        )
        if not success:
            log.critical(f"Failed to delete recipe_step. Check logs for details.")
            return return_json(
                message="Failed to delete recipe_step.",
                success=False,
            )
    except Exception as e:
        log.critical(f"Failed to delete recipe_step. Error: {e}")
        return return_json(
            message="Failed to delete recipe_step.",
            success=False,
        )

    return return_json(
        message="Successfully deleted recipe_step.",
        success=True,
    )
