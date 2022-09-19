#!
# -*- coding: utf-8 -*-
"""
Created on 2022-07-16
@author: Edmund Bennett
@email: bennettedmund@gmail.com
"""

from fastapi import APIRouter

from bfsa.db.environment import Environment
from bfsa.db.client import Client
from bfsa.sql.create_select import create_select
from bfsa.utils.return_json import return_json
from bfsa.utils.logger import logger as log


router = APIRouter()


@router.get("/api/readRecipeDetails")
def read_recipe_details(
    recipe_id: str,
):
    """
    Read recipe details
    """
    log.info("Calling read_recipe_details")

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

    # get recipe

    data = {}

    try:
        recipes = client.select_data(
            query=create_select(
                {
                    "id": recipe_id,
                    "partitionKey": "recipes",
                }
            ),
        )
        if recipes:

            data.update({"recipe": recipes[0]})

            # get recipe steps

            try:
                recipe_steps = client.select_data(
                    query=create_select(
                        {
                            "recipe_id": recipe_id,
                            "partitionKey": "recipe-steps",
                        }
                    ),
                )

                data.update({"steps": []})
                if recipe_steps:
                    data.update({"steps": recipe_steps})

            except Exception as e:
                log.critical(f"Failed to select recipe-steps data. Error: {e}")
                return return_json(
                    message="Failed to select recipe-steps data.",
                    success=False,
                )

            # get ingredients

            try:
                ingredients = client.select_data(
                    query=create_select(
                        {
                            "partitionKey": "ingredients",
                        }
                    ),
                )

                data.update({"ingredients": []})
                if ingredients:
                    data.update({"ingredients": ingredients})

            except Exception as e:
                log.critical(f"Failed to select ingredients data. Error: {e}")
                return return_json(
                    message="Failed to select ingredients data.",
                    success=False,
                )

            # get equipment

            try:
                equipment = client.select_data(
                    query=create_select(
                        {
                            "partitionKey": "equipment",
                        }
                    ),
                )

                data.update({"equipment": []})
                if equipment:
                    data.update({"equipment": equipment})

            except Exception as e:
                log.critical(f"Failed to select equipment data. Error: {e}")
                return return_json(
                    message="Failed to select equipment data.",
                    success=False,
                )

            ingredient_usages, equipment_usages = [], []
            for recipe_step in recipe_steps:

                # for each step get ingredient usages

                try:
                    ingredient_usage = client.select_data(
                        query=create_select(
                            {
                                "recipe_step_id": recipe_step["id"],
                                "partitionKey": "ingredient-usage",
                            }
                        ),
                    )

                    if ingredient_usage:
                        ingredient_usages += ingredient_usage

                except Exception as e:
                    log.critical(f"Failed to select ingredient usage data. Error: {e}")
                    return return_json(
                        message="Failed to select ingredient usage data.",
                        success=False,
                    )

                # for each step get equipment usage

                try:
                    equipment_usage = client.select_data(
                        query=create_select(
                            {
                                "recipe_step_id": recipe_step["id"],
                                "partitionKey": "equipment-usage",
                            }
                        ),
                    )

                    if equipment_usage:
                        equipment_usages =+ equipment_usage

                except Exception as e:
                    log.critical(f"Failed to select equipment usage data. Error: {e}")
                    return return_json(
                        message="Failed to select equipment usage data.",
                        success=False,
                    )

            data.update({"ingredient_usage": ingredient_usages})
            data.update({"equipment_usage": equipment_usages})

        else:
            log.critical(f"Failed to select recipe data. Check logs for details.")
            return return_json(
                message="Failed to select recipe data.",
                success=False,
            )
    except Exception as e:
        log.critical(f"Failed to select recipe data. Error: {e}")
        return return_json(
            message="Failed to select recipe data.",
            success=False,
        )

    return return_json(
        message="Successfully selected recipe details.",
        success=True,
        content=data,
    )
