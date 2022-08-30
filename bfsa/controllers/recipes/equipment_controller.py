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


@router.get("/api/readEquipments")
def read_equipment(
    where: Dict[str, Any] = None,
):
    """
    Read equipment
    """
    log.info("Calling read_equipment")

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

    return return_json(
        message="Successfully deleted equipment.",
        success=True,
    )
