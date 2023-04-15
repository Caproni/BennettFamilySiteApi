#!
# -*- coding: utf-8 -*-
"""
Created on 2022-11-12
@author: Edmund Bennett
@email: bennettedmund@gmail.com
"""

from os import system, remove
from io import BytesIO
from typing import Dict, Any, Optional
from fastapi import APIRouter, UploadFile
from fastapi.responses import FileResponse
from PyPDF2 import PdfReader
import csv

from bfsa.db.environment import client_factory
from bfsa.db.client import get_blob_credentials
from bfsa.controllers.environment import Environment as Base
from bfsa.blob.blob_service_client import upload_blob, delete_blob
from bfsa.sql.create_select import create_select
from bfsa.utils.return_json import return_json
from bfsa.utils.create_guid import create_guid
from bfsa.utils.get_files_recursively import FileManipulation
from bfsa.utils.logger import logger as log


router = APIRouter()

environment = Base()

#    @       @
#     @     @
#   @@@@@@@@@@@
#  @@@ @@@@@ @@@
# @@@@@@@@@@@@@@@
# @  @@@@@@@@@  @
# @  @       @  @
#     @@   @@


@router.post("/api/createPaper")
def create_paper(
    title: str,
    file: UploadFile = None,
    description: Optional[str] = None,
    abstract: Optional[str] = None,
    doi: Optional[str] = None,
    language: Optional[str] = None,
    authors: Optional[str] = None,
    publication_type: Optional[str] = None,
    publication_location: Optional[str] = None,
    publication_date: Optional[str] = None,
):
    """
    Add paper object to database
    """
    log.info("Calling create_paper")

    staging_dir = "./staging"
    staging_populated = False
    if doi is not None:
        try:
            system(f'python -m PyPaperBot --doi="{doi}" --dwn-dir="{staging_dir}"')
            staging_populated = True
        except Exception as e:
            log.warning(f"DOI provided but could not get paper. Error: {e}")
            return return_json(
                message="DOI provided but could not get paper.",
                success=False,
            )

    bib_data, file_bytes = None, None
    if staging_populated:  # then load obtained files

        # metadata first (from result.csv)

        with open(f"{staging_dir}/result.csv", newline="") as csv_file:
            metadata = csv.DictReader(csv_file, delimiter=",")

            for row in metadata:
                bib_data = row
                if not file.filename:
                    file = FileResponse(f'{staging_dir}/{row["PDF Name"]}')
                    with open(f'{staging_dir}/{row["PDF Name"]}', "rb") as pdf:
                        file_bytes = BytesIO(pdf.read())
                break  # always take the first result

    # check inputs

    filename = file.filename if file.filename else file.path

    if filename == "":
        return return_json(
            "No file selected for uploading.",
            success=False,
        )

    if (
        file
        and "." in filename
        and filename.rsplit(".", 1)[1].lower() not in ["pdf"]
    ):
        return return_json(
            "Invalid file.",
            success=False,
        )

    # pre-amble

    client = client_factory()

    # insert data - blob first then metadata

    guid = create_guid()

    blob_credentials = get_blob_credentials()

    try:
        blob_url = upload_blob(
            connection=blob_credentials["credentials"],
            container="papers",
            guid=guid,
            filename=filename,
            file=file_bytes,
            overwrite=False,
        )

    except Exception as e:
        log.critical(f"Failed to insert paper. Error: {e}")
        return return_json(
            message="Failed to insert paper.",
            success=False,
        )

    file_bytes.seek(0)

    reader = PdfReader(file_bytes)
    paper_content = "\n".join([page.extract_text() for page in reader.pages])

    parsed_authors = None if bib_data is None else bib_data["Authors"].split(" and ")

    paper_dict = {
        "title": title if bib_data is None else bib_data["Name"],
        "description": description,
        "abstract": abstract,
        "paper_content": paper_content,
        "doi": doi,
        "pages": len(reader.pages),
        "language": language,
        "publication_type": publication_type,
        "publication_location": publication_location,
        "publication_date": publication_date,
        "authors": authors.split(",") if bib_data is None and parsed_authors is None else parsed_authors,
        "blob_url": blob_url,
        "id": guid,
        "partitionKey": "papers",
    }

    # clear staging directory

    files_in_staging = FileManipulation.get_files_recursively(
        directory=staging_dir,
        exclude_filename_text=".gitkeep",
    )

    for file_in_staging in files_in_staging:
        remove(file_in_staging)

    # insert data into cosmos

    try:
        cosmos_success = client.insert_data(
            [paper_dict],
        )
        if not cosmos_success:
            log.critical(f"Failed to insert paper. Check logs for details.")

    except Exception as e:
        cosmos_success = False
        log.critical(f"Failed to insert paper. Error: {e}")

    if cosmos_success:
        return return_json(
            message="Successfully inserted paper.",
            success=True,
        )

    # Are you still here? Then blob insertion succeeded but Cosmos insertion failed
    # roll back by deleting blob

    try:
        response = delete_paper(
            paper_id=guid,
        )
        # TODO: indicate whether roll back was successful
        return return_json(
            message="Failed to insert paper.",
            success=False,
        )
    except Exception as e:
        log.critical(
            f"Failed to insert paper. Check blob storage for orphaned blobs. Error: {e}"
        )
        return return_json(
            message="Failed to insert paper.",
            success=False,
        )


@router.get("/api/readPapers")
def read_papers(
    where: Dict[str, Any] = None,
):
    """
    Read papers
    """
    log.info("Calling read_papers")

    client = client_factory()

    if where is None:
        where = {}
    where.update({"partitionKey": "papers"})

    query = create_select(where)

    try:
        data = client.select_data(
            query=query,
        )
        if data:
            return return_json(
                message="Successfully selected papers data.",
                success=True,
                content=data,
            )
    except Exception as e:
        log.critical(f"Failed to select papers data. Error: {e}")
        return return_json(
            message="Failed to select papers data.",
            success=False,
        )

    log.critical(f"Failed to select papers data. Check logs for details.")
    return return_json(
        message="Failed to select papers data.",
        success=False,
    )


@router.patch("/api/updatePaperMetadata")
def update_paper_metadata(
    paper_id: str,
    patch: Dict[str, Any],
):
    """
    Update papers metadata
    """
    log.info("Calling update_paper_metadata")

    client = client_factory()

    patch.update({"id": paper_id})
    patch.update({"partitionKey": "papers"})

    try:
        success = client.update_data(
            item={"id": paper_id, "partitionKey": "papers"},
            body=patch,
            upsert=False,
        )
        if not success:
            log.critical(f"Failed to update paper metadata. Check logs for details.")
            return return_json(
                message="Failed to update paper metadata.",
                success=False,
            )
    except Exception as e:
        log.critical(f"Failed to update paper metadata. Error: {e}")
        return return_json(
            message="Failed to update paper metadata.",
            success=False,
        )

    return return_json(
        message="Successfully updated paper metadata.",
        success=True,
    )


@router.delete("/api/deletePaper")
def delete_paper(
    paper_id: str,
):
    """
    Delete paper
    """
    log.info("Calling delete_paper")

    client = client_factory()

    blob_credentials = get_blob_credentials()

    try:
        papers_details = read_papers(where={"id": paper_id})
    except Exception as e:
        log.critical(f"Failed to read paper. Error: {e}")
        return return_json(
            message="Failed to read paper.",
            success=False,
        )

    try:
        success = client.delete_data(
            item=paper_id,
            partition_key="papers",
        )
        if not success:
            log.critical(f"Failed to delete paper. Check logs for details.")
            return return_json(
                message="Failed to delete paper.",
                success=False,
            )

        blob_delete_success = delete_blob(
            connection=blob_credentials["credentials"],
            container="paper",
            url=papers_details["content"][0]["blob_url"],
        )

        if blob_delete_success:
            ...

    except Exception as e:
        log.critical(f"Failed to delete paper. Error: {e}")
        return return_json(
            message="Failed to delete paper.",
            success=False,
        )

    return return_json(
        message="Successfully deleted paper.",
        success=True,
    )
