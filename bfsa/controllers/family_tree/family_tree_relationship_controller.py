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
from datetime import date

from bfsa.db.environment import Environment
from bfsa.db.client import Client
from bfsa.sql.create_select import create_select
from bfsa.utils.return_json import return_json
from bfsa.utils.create_guid import create_guid
from bfsa.utils.logger import logger as log


router = APIRouter()


class FamilyTreeRelationshipModel(BaseModel):
    """
    Pydantic model for family-tree relationship
    """
    person_one: str
    person_two: str
    start_time: date
    end_time: date
    narrative: str


@router.post("/api/createFamilyTreeRelationship")
def create_family_tree_relationship(
    relationship: FamilyTreeRelationshipModel,
):
    """
    Add family-tree relationship object to database
    """
    log.info("Calling create_family_tree_relationship")

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

    relationship_dict = dict(relationship)
    relationship_dict.update({"id": create_guid()})
    relationship_dict.update({"partitionKey": "family-tree-relationship"})

    try:
        success = client.insert_data(
            [relationship_dict],
        )
        if not success:
            log.critical(f"Failed to insert family-tree relationship. Check logs for details.")
            return return_json(
                message="Failed to insert family-tree relationship.",
                success=False,
            )
    except Exception as e:
        log.critical(f"Failed to insert family-tree relationship. Error: {e}")
        return return_json(
            message="Failed to insert family-tree relationship.",
            success=False,
        )

    return return_json(
        message="Successfully inserted family-tree relationship.",
        success=True,
    )


@router.get("/api/readFamilyTreeRelationships")
def read_family_tree_relationships(
    where: Dict[str, Any] = None,
):
    """
    Read family-tree people
    """
    log.info("Calling read_family_tree_relationships")

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
    where.update({"partitionKey": "family-tree-relationship"})

    query = create_select(where)

    try:
        data = client.select_data(
            query=query,
        )
        if data:
            return return_json(
                message="Successfully selected family-tree relationship data.",
                success=True,
                content=data,
            )
    except Exception as e:
        log.critical(f"Failed to select family-tree relationship data. Error: {e}")
        return return_json(
            message="Failed to select family-tree relationship data.",
            success=False,
        )

    log.critical(f"Failed to select family-tree relationship data. Check logs for details.")
    return return_json(
        message="Failed to select family-tree relationship data.",
        success=False,
    )


@router.patch("/api/updateFamilyTreeRelationship")
def update_family_tree_relationship(
    family_tree_relationship_id: str,
    patch: Dict[str, Any],
):
    """
    Update family-tree relationship
    """
    log.info("Calling update_family_tree_relationship")

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

    patch.update({"id": family_tree_relationship_id})
    patch.update({"partitionKey": "family-tree-relationship"})

    try:
        success = client.update_data(
            item={"id": family_tree_relationship_id, "partitionKey": "family-tree-relationship"},
            body=patch,
            upsert=False,
        )
        if not success:
            log.critical(f"Failed to update family-tree relationship. Check logs for details.")
            return return_json(
                message="Failed to update family-tree relationship.",
                success=False,
            )
    except Exception as e:
        log.critical(f"Failed to update family-tree relationship. Error: {e}")
        return return_json(
            message="Failed to update family-tree relationship.",
            success=False,
        )

    return return_json(
        message="Successfully updated family-tree relationship.",
        success=True,
    )


@router.delete("/api/deleteFamilyTreeRelationship")
def delete_family_tree_relationship(
    family_tree_relationship_id: str,
):
    """
    Delete family tree relationship
    """
    log.info("Calling delete_family_tree_relationship")

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
            item=family_tree_relationship_id,
            partition_key="family-tree-relationship",
        )
        if not success:
            log.critical(f"Failed to delete family-tree relationship. Check logs for details.")
            return return_json(
                message="Failed to delete family-tree relationship.",
                success=False,
            )
    except Exception as e:
        log.critical(f"Failed to delete family-tree relationship. Error: {e}")
        return return_json(
            message="Failed to delete family-tree relationship.",
            success=False,
        )

    return return_json(
        message="Successfully deleted family-tree relationship.",
        success=True,
    )
