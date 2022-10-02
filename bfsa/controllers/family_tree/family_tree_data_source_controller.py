#!
# -*- coding: utf-8 -*-
"""
Created on 2022-08-08
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


class FamilyTreeDataSourceModel(BaseModel):
    """
    Pydantic model for family-tree data source
    """
    name: str
    description: str
    url: str
    source_date: str


@router.post("/api/createFamilyTreeDataSource")
def create_family_tree_data_source(
    data_source: FamilyTreeDataSourceModel,
):
    """
    Add family-tree data source object to database
    """
    log.info("Calling create_family_tree_data_source")

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

    data_source_dict = dict(data_source)
    data_source_dict.update({"id": create_guid()})
    data_source_dict.update({"partitionKey": "family-tree-data-source"})

    try:
        success = client.insert_data(
            [data_source_dict],
        )
        if not success:
            log.critical(f"Failed to insert family-tree data source. Check logs for details.")
            return return_json(
                message="Failed to insert family-tree data source.",
                success=False,
            )
    except Exception as e:
        log.critical(f"Failed to insert family-tree data source. Error: {e}")
        return return_json(
            message="Failed to insert family-tree data source.",
            success=False,
        )

    return return_json(
        message="Successfully inserted family-tree data source.",
        success=True,
    )


@router.get("/api/readFamilyTreeDataSources")
def read_family_tree_data_sources(
    where: Dict[str, Any] = None,
):
    """
    Read family-tree people
    """
    log.info("Calling read_family_tree_data_sources")

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
    where.update({"partitionKey": "family-tree-data-source"})

    query = create_select(where)

    try:
        data = client.select_data(
            query=query,
        )
        if data:
            return return_json(
                message="Successfully selected family-tree data source data.",
                success=True,
                content=data,
            )
    except Exception as e:
        log.critical(f"Failed to select family-tree data source data. Error: {e}")
        return return_json(
            message="Failed to select family-tree data source data.",
            success=False,
        )

    log.critical(f"Failed to select family-tree data source data. Check logs for details.")
    return return_json(
        message="Failed to select family-tree data source data.",
        success=False,
    )


@router.patch("/api/updateFamilyTreeDataSource")
def update_family_tree_data_source(
    family_tree_data_source_id: str,
    patch: Dict[str, Any],
):
    """
    Update family-tree data source
    """
    log.info("Calling update_family_tree_data_source")

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

    patch.update({"id": family_tree_data_source_id})
    patch.update({"partitionKey": "family-tree-data-source"})

    try:
        success = client.update_data(
            item={"id": family_tree_data_source_id, "partitionKey": "family-tree-data-source"},
            body=patch,
            upsert=False,
        )
        if not success:
            log.critical(f"Failed to update family-tree data source. Check logs for details.")
            return return_json(
                message="Failed to update family-tree data source.",
                success=False,
            )
    except Exception as e:
        log.critical(f"Failed to update family-tree data source. Error: {e}")
        return return_json(
            message="Failed to update family-tree data source.",
            success=False,
        )

    return return_json(
        message="Successfully updated family-tree data source.",
        success=True,
    )


@router.delete("/api/deleteFamilyTreeDataSource")
def delete_family_tree_data_source(
    family_tree_data_source_id: str,
):
    """
    Delete family tree data source
    """
    log.info("Calling delete_family_tree_data_source")

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
            item=family_tree_data_source_id,
            partition_key="family-tree-data-source",
        )
        if not success:
            log.critical(f"Failed to delete family-tree data source. Check logs for details.")
            return return_json(
                message="Failed to delete family-tree data source.",
                success=False,
            )
    except Exception as e:
        log.critical(f"Failed to delete family-tree data source. Error: {e}")
        return return_json(
            message="Failed to delete family-tree data source.",
            success=False,
        )

    return return_json(
        message="Successfully deleted family-tree data source.",
        success=True,
    )
