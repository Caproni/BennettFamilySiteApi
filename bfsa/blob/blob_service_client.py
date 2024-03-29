#!
# -*- coding: utf-8 -*-
"""
Created on 2022-08-28
@author: Edmund Bennett
@email: bennettedmund@gmail.com
"""

from typing import Optional
from io import BytesIO
from azure.storage.blob import BlobServiceClient

from bfsa.utils.logger import logger as log


def upload_blob(
    connection: str,
    container: str,
    filename: str,
    file: BytesIO,
    guid: str,
    overwrite: bool = False,
) -> Optional[str]:
    log.info("Calling upload_blob")

    try:

        blob_service_client = BlobServiceClient.from_connection_string(connection)

        client = blob_service_client.get_container_client(
            container=container,
        )

        # get properties of the container to force exception to be thrown if container does not exist
        client.get_container_properties()

        response = client.upload_blob(
            f"{guid}.{filename.split('.')[-1]}",
            file,
            overwrite=overwrite,
        )

        return response.url
    except Exception as e:
        log.critical(f"Failed to insert blob into storage. Error: {e}")
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
        client.get_blob_client(
            url.replace(client.primary_endpoint + "/", "")
        ).delete_blob()
        return True
    except Exception as e:
        log.critical(f"Failed to delete blob from storage. Error: {e}")
        return False


if __name__ == "__main__":
    pass
