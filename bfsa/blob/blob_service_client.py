#!
# -*- coding: utf-8 -*-
"""
╔═╗╦ ╦╔╦╗  ╔╦╗┬┌─┐┬┌┬┐┌─┐┬
║ ╦╠═╣ ║║   ║║││ ┬│ │ ├─┤│
╚═╝╩ ╩═╩╝  ═╩╝┴└─┘┴ ┴ ┴ ┴┴─┘

Created on 2022-08-28
@author: Edmund Bennett
@email: edmund.bennett@ghd.com
"""

from typing import List, Optional
from azure.storage.blob import BlobServiceClient
from fastapi import UploadFile

from bfsa.utils.logger import logger as log


def upload_blob(
    connection: str,
    container: str,
    file: UploadFile,
    id: str,
    overwrite: bool = False,
) -> Optional[str]:
    log.info("Calling upload_blob")

    try:

        blob_service_client = BlobServiceClient.from_connection_string(connection)

        client = blob_service_client.get_container_client(
            container=container,
        )

        client.get_container_properties()  # get properties of the container to force exception to be thrown if container does not exist

        response = client.upload_blob(
            f"{id}.{file.filename.split('.')[-1]}",
            file.file,
            overwrite=overwrite,
        )

        return response.url
    except Exception as e:
        log.critical(f"Failed to insert blob into storage. Error: {e}")
        return None


def read_blobs(
    connection: str,
    container: str,
    query: str,
) -> Optional[List[bytes]]:
    log.info("Calling read_blobs")

    try:
        blob_service_client = BlobServiceClient.from_connection_string(connection)
        client = blob_service_client.get_container_client(
            container=container,
        )
        client.get_container_properties()  # get properties of the container to force exception to be thrown if container does not exist
        return client.select_data(
            query,
        )
    except Exception as e:
        log.critical(f"Failed to select blobs from storage. Error: {e}")
        return None


def delete_blob(
    connection: str,
    container: str,
    url: str,
) -> bool:
    log.info("Calling delete_blob")

    try:

        blob_service_client = BlobServiceClient.from_connection_string(connection)
        client = blob_service_client.get_container_client(
            container=container,
        )
        client.get_container_properties()  # get properties of the container to force exception to be thrown if container does not exist
        client.delete_data(
            url,
        )
        return True
    except Exception as e:
        log.critical(f"Failed to delete blob from storage. Error: {e}")
        return False


if __name__ == "__main__":
    pass
