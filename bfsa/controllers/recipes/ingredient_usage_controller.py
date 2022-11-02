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

from bfsa.db.environment import client_factory
from bfsa.sql.create_select import create_select
from bfsa.utils.return_json import return_json
from bfsa.utils.create_guid import create_guid
from bfsa.utils.logger import logger as log


router = APIRouter()


class IngredientUsageModel(BaseModel):
    """
    Pydantic model for ingredient usage
    """
    recipe_step_id: str
    ingredient_id: str
    quantity: float
    quantity_units: str
    notes: str


@router.post("/api/createIngredientUsage")
def create_ingredient_usage(
    ingredient_usage: IngredientUsageModel,
):
    """
    Add ingredient usage object to database
    """
    log.info("Calling create_ingredient_usage")

    client = client_factory()

    ingredient_usage_dict = dict(ingredient_usage)
    ingredient_usage_dict.update({"id": create_guid()})
    ingredient_usage_dict.update({"partitionKey": "ingredient-usage"})

    try:
        success = client.insert_data(
            [ingredient_usage_dict],
        )
        if not success:
            log.critical(f"Failed to insert ingredient usage. Check logs for details.")
            return return_json(
                message="Failed to insert ingredient usage.",
                success=False,
            )
    except Exception as e:
        log.critical(f"Failed to insert ingredient usage. Error: {e}")
        return return_json(
            message="Failed to insert ingredient usage.",
            success=False,
        )

    return return_json(
        message="Successfully inserted ingredient usage.",
        success=True,
    )


@router.get("/api/readIngredientUsages")
def read_ingredient_usages(
    where: Dict[str, Any] = None,
):
    """
    Read ingredient usages
    """
    log.info("Calling read_ingredient_usages")

    client = client_factory()

    if where is None:
        where = {}
    where.update({"partitionKey": "ingredient-usage"})

    query = create_select(where)

    try:
        data = client.select_data(
            query=query,
        )
        if data:
            return return_json(
                message="Successfully selected ingredient usage data.",
                success=True,
                content=data,
            )
    except Exception as e:
        log.critical(f"Failed to select ingredient usage data. Error: {e}")
        return return_json(
            message="Failed to select ingredient usage data.",
            success=False,
        )

    log.critical(f"Failed to select ingredient usage data. Check logs for details.")
    return return_json(
        message="Failed to select ingredient usage data.",
        success=False,
    )


@router.patch("/api/updateIngredientUsage")
def update_ingredient_usage(
    ingredient_usage_id: str,
    patch: Dict[str, Any],
):
    """
    Update ingredient usage
    """
    log.info("Calling update_ingredient_usage")

    client = client_factory()

    patch.update({"id": ingredient_usage_id})
    patch.update({"partitionKey": "ingredient-usage"})

    try:
        success = client.update_data(
            item={"id": ingredient_usage_id, "partitionKey": "ingredient-usage"},
            body=patch,
            upsert=False,
        )
        if not success:
            log.critical(f"Failed to update ingredient usage. Check logs for details.")
            return return_json(
                message="Failed to update ingredient usage.",
                success=False,
            )
    except Exception as e:
        log.critical(f"Failed to update ingredient usage. Error: {e}")
        return return_json(
            message="Failed to update ingredient usage.",
            success=False,
        )

    return return_json(
        message="Successfully updated ingredient usage.",
        success=True,
    )


@router.delete("/api/deleteIngredientUsage")
def delete_ingredient_usage(
    ingredient_usage_id: str,
):
    """
    Delete ingredient usage
    """
    log.info("Calling delete_ingredient_usage")

    client = client_factory()

    try:
        success = client.delete_data(
            item=ingredient_usage_id,
            partition_key="ingredient-usage",
        )
        if not success:
            log.critical(f"Failed to delete ingredient usage. Check logs for details.")
            return return_json(
                message="Failed to delete ingredient usage.",
                success=False,
            )
    except Exception as e:
        log.critical(f"Failed to delete ingredient usage. Error: {e}")
        return return_json(
            message="Failed to delete ingredient usage.",
            success=False,
        )

    return return_json(
        message="Successfully deleted ingredient usage.",
        success=True,
    )
