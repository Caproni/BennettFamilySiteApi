#!
# -*- coding: utf-8 -*-
"""
Created on 2022-08-08
@author: Edmund Bennett
@email: bennettedmund@gmail.com
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter
from pydantic import BaseModel

from bfsa.db.environment import Environment
from bfsa.db.client import Client
from bfsa.sql.create_select import create_select
from bfsa.utils.return_json import return_json
from bfsa.utils.create_guid import create_guid
from bfsa.utils.logger import logger as log


router = APIRouter()


class FamilyTreePersonModel(BaseModel):
    """
    Pydantic model for family-tree person
    """
    first_name: Optional[str]
    middle_names: List[str]
    chosen_name: Optional[str]
    surname: Optional[str]
    title: Optional[str]
    birthplace: Optional[str]
    sex: Optional[str]
    date_of_birth: Optional[str]
    date_of_death: Optional[str]
    image: Optional[str]
    previous_surnames: List[str]
    relationships: List[str]
    narrative: Optional[str]
    generation_index: int
    column_index: int
    facts: List[str]
    photos: List[str]
    sources: List[str]


@router.post("/api/createFamilyTreePerson")
def create_family_tree_person(
    person: FamilyTreePersonModel,
):
    """
    Add family-tree person object to database
    """
    log.info("Calling create_family_tree_person")

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

    person_dict = dict(person)
    person_dict.update({"id": create_guid()})
    person_dict.update({"partitionKey": "family-tree-person"})

    try:
        success = client.insert_data(
            [person_dict],
        )
        if not success:
            log.critical(f"Failed to insert family-tree person. Check logs for details.")
            return return_json(
                message="Failed to insert family-tree person.",
                success=False,
            )
    except Exception as e:
        log.critical(f"Failed to insert family-tree person. Error: {e}")
        return return_json(
            message="Failed to insert family-tree person.",
            success=False,
        )

    return return_json(
        message="Successfully inserted family-tree person.",
        success=True,
    )


@router.get("/api/readFamilyTreePeople")
def read_family_tree_people(
    where: Dict[str, Any] = None,
):
    """
    Read family-tree people
    """
    log.info("Calling read_family_tree_people")

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
    where.update({"partitionKey": "family-tree-person"})

    query = create_select(where)

    try:
        data = client.select_data(
            query=query,
        )
        if data:
            return return_json(
                message="Successfully selected family-tree person data.",
                success=True,
                content=data,
            )
    except Exception as e:
        log.critical(f"Failed to select family-tree person data. Error: {e}")
        return return_json(
            message="Failed to select family-tree person data.",
            success=False,
        )

    log.critical(f"Failed to select family-tree person data. Check logs for details.")
    return return_json(
        message="Failed to select family-tree person data.",
        success=False,
    )


@router.patch("/api/updateFamilyTreePerson")
def update_family_tree_person(
    family_tree_person_id: str,
    patch: Dict[str, Any],
):
    """
    Update family-tree person
    """
    log.info("Calling update_family_tree_person")

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

    patch.update({"id": family_tree_person_id})
    patch.update({"partitionKey": "family-tree-person"})

    try:
        success = client.update_data(
            item={"id": family_tree_person_id, "partitionKey": "family-tree-person"},
            body=patch,
            upsert=False,
        )
        if not success:
            log.critical(f"Failed to update family-tree person. Check logs for details.")
            return return_json(
                message="Failed to update family-tree person.",
                success=False,
            )
    except Exception as e:
        log.critical(f"Failed to update family-tree person. Error: {e}")
        return return_json(
            message="Failed to update family-tree person.",
            success=False,
        )

    return return_json(
        message="Successfully updated family-tree person.",
        success=True,
    )


@router.delete("/api/deleteFamilyTreePerson")
def delete_family_tree_person(
    family_tree_person_id: str,
):
    """
    Delete family tree person
    """
    log.info("Calling delete_family_tree_person")

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
            item=family_tree_person_id,
            partition_key="family-tree-person",
        )
        if not success:
            log.critical(f"Failed to delete family-tree person. Check logs for details.")
            return return_json(
                message="Failed to delete family-tree person.",
                success=False,
            )
    except Exception as e:
        log.critical(f"Failed to delete family-tree person. Error: {e}")
        return return_json(
            message="Failed to delete family-tree person.",
            success=False,
        )

    return return_json(
        message="Successfully deleted family-tree person.",
        success=True,
    )
