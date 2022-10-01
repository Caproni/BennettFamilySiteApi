#!
# -*- coding: utf-8 -*-
"""
Created on 2022-08-08
@author: Edmund Bennett
@email: bennettedmund@gmail.com
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel

from bfsa.db.environment import Environment
from bfsa.db.client import Client, get_blob_credentials
from bfsa.blob.blob_service_client import upload_blob, delete_blob
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


@router.put("/api/putFamilyTreePersonImage")
def put_family_tree_person_image(
    family_tree_person_id: str,
    image: UploadFile = File(...),
):
    """
    Put family tree person image
    """
    log.info("Calling put_family_tree_person_image")

    # check inputs

    if image.filename == "":
        return return_json(
            "No file selected for uploading.",
            success=False,
        )

    if (
        image
        and "." in image.filename
        and image.filename.rsplit(".", 1)[1].lower() not in ["png", "bmp", "jpg", "jpeg"]
    ):
        return return_json(
            "Invalid image file.",
            success=False,
        )

    # pre-amble

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

    # insert data - blob first then metadata

    blob_credentials = get_blob_credentials()

    try:
        blob_url = upload_blob(
            connection=blob_credentials["credentials"],
            container="family-tree-photos",
            id=family_tree_person_id,
            file=image,
            overwrite=True,
        )

    except Exception as e:
        log.critical(f"Failed to insert family tree person image. Error: {e}")
        return return_json(
            message="Failed to insert family tree person image.",
            success=False,
        )

    response = read_family_tree_people(where={"id": family_tree_person_id})

    if response["success"]:
        content = response["content"]
        if content:
            family_tree_person_dict = content[0]
            if "blob_url" in family_tree_person_dict.keys() and family_tree_person_dict["blob_url"] == blob_url:
                return return_json(
                    message="Successfully updated family tree person image.",
                    success=True,
                )

            family_tree_person_dict.update({"blob_url": blob_url})

            try:
                cosmos_success = client.update_data(
                    item={"id": family_tree_person_id, "partitionKey": "family-tree-person"},
                    body=family_tree_person_dict,
                    upsert=False,
                )
                if not cosmos_success:
                    log.critical(f"Failed to insert family tree person image. Check logs for details.")

            except Exception as e:
                cosmos_success = False
                log.critical(f"Failed to insert family tree person image. Error: {e}")

            if cosmos_success:
                return return_json(
                    message="Successfully inserted family tree person image.",
                    success=True,
                )

    # Are you still here? Then blob insertion succeeded but Cosmos insertion failed
    # roll back by deleting blob

    try:
        response = delete_family_tree_person_image(
            photo_id=family_tree_person_id,
        )
        # TODO: indicate whether roll back was successful
        return return_json(
            message="Failed to insert family tree person image.",
            success=False,
        )
    except Exception as e:
        log.critical(f"Failed to insert family tree person image. Check blob storage for orphaned blobs. Error: {e}")
        return return_json(
            message="Failed to insert family tree person image.",
            success=False,
        )


@router.get("/api/deleteFamilyTreePersonImage")
def delete_family_tree_person_image(
    family_tree_person_id: str,
):
    log.info("Calling delete_family_tree_person_image")

    blob_credentials = get_blob_credentials()

    try:
        success = delete_blob(
            connection=blob_credentials["credentials"],
            container="family-tree-photos",
            url="",
        )

    except Exception as e:
        log.critical(f"Failed to delete family tree person image. Error: {e}")
        return return_json(
            message="Failed to delete family tree person image.",
            success=False,
        )

    return return_json(
        message="Successfully deleted family tree person image.",
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
