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


class EquipmentUsageModel(BaseModel):
    """
    Pydantic model for equipment usage
    """
    recipe_id: str
    equipment_id: str
    notes: str


@router.post("/api/createEquipmentUsage")
def create_equipment_usage(
    equipment_usage: EquipmentUsageModel,
):
    """
    Add equipment usage object to database
    """
    log.info("Calling create_equipment_usage")

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

    equipment_usage_dict = dict(equipment_usage)
    equipment_usage_dict.update({"id": create_guid()})
    equipment_usage_dict.update({"partitionKey": "equipment-usage"})

    try:
        success = client.insert_data(
            [equipment_usage_dict],
        )
        if not success:
            log.critical(f"Failed to insert equipment usage. Check logs for details.")
            return return_json(
                message="Failed to insert equipment usage.",
                success=False,
            )
    except Exception as e:
        log.critical(f"Failed to insert equipment usage. Error: {e}")
        return return_json(
            message="Failed to insert equipment usage.",
            success=False,
        )

    return return_json(
        message="Successfully inserted equipment usage.",
        success=True,
    )


@router.get("/api/readEquipmentUsages")
def read_equipment_usages(
    where: Dict[str, Any] = None,
):
    """
    Read equipment usages
    """
    log.info("Calling read_equipment_usages")

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
    where.update({"partitionKey": "equipment-usage"})

    query = create_select(where)

    try:
        data = client.select_data(
            query=query,
        )
        if data:
            return return_json(
                message="Successfully selected equipment usage data.",
                success=True,
                content=data,
            )
    except Exception as e:
        log.critical(f"Failed to select equipment usage data. Error: {e}")
        return return_json(
            message="Failed to select equipment usage data.",
            success=False,
        )

    log.critical(f"Failed to select equipment usage data. Check logs for details.")
    return return_json(
        message="Failed to select equipment usage data.",
        success=False,
    )


@router.patch("/api/updateEquipmentUsage")
def update_equipment_usage(
    equipment_usage_id: str,
    patch: Dict[str, Any],
):
    """
    Update equipment usage
    """
    log.info("Calling update_equipment_usage")

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

    patch.update({"id": equipment_usage_id})
    patch.update({"partitionKey": "equipment-usage"})

    try:
        success = client.update_data(
            item={"id": equipment_usage_id, "partitionKey": "equipment-usage"},
            body=patch,
            upsert=False,
        )
        if not success:
            log.critical(f"Failed to update equipment usage. Check logs for details.")
            return return_json(
                message="Failed to update equipment usage.",
                success=False,
            )
    except Exception as e:
        log.critical(f"Failed to update equipment usage. Error: {e}")
        return return_json(
            message="Failed to update equipment usage.",
            success=False,
        )

    return return_json(
        message="Successfully updated equipment usage.",
        success=True,
    )


@router.delete("/api/deleteEquipmentUsage")
def delete_equipment_usage(
    equipment_usage_id: str,
):
    """
    Delete equipment usage
    """
    log.info("Calling delete_equipment_usage")

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
            item=equipment_usage_id,
            partition_key="equipment-usage",
        )
        if not success:
            log.critical(f"Failed to delete equipment usage. Check logs for details.")
            return return_json(
                message="Failed to delete equipment usage.",
                success=False,
            )
    except Exception as e:
        log.critical(f"Failed to delete equipment usage. Error: {e}")
        return return_json(
            message="Failed to delete equipment usage.",
            success=False,
        )

    return return_json(
        message="Successfully deleted equipment usage.",
        success=True,
    )
