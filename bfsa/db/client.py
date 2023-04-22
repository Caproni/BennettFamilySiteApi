#!
# -*- coding: utf-8 -*-
"""
Created on 2022-06-26
@author: Edmund Bennett
@email: bennettedmund@gmail.com
"""

from typing import List, Dict, Any, Union
from json import load
from azure.cosmos import CosmosClient, PartitionKey

from bfsa.controllers.environment import Environment
from bfsa.utils.get_vault_secret import get_vault_secret


environment = Environment()


def get_blob_credentials():
    with open("credentials/blob_config.json", "r") as credentials_file:
        blob_credentials = load(credentials_file)

    blob_credentials["credentials"] = get_vault_secret(
        "bennettfamilyblobs_credentials",
        production=environment["IS_PROD"],
    )
    return blob_credentials


class Client:
    """
    Client to connect to backend database and manage interactions
    """
    def __init__(
        self,
        endpoint: str,
        key: str,
        database_name: str,
        container_name: str,
        partition_key_field: str = "partitionKey",
    ):
        self.client = CosmosClient(
            url=endpoint,
            credential=key,
        )
        self.database = self.client.create_database_if_not_exists(id=database_name)
        self.container = self.database.create_container_if_not_exists(
            id=container_name,
            partition_key=PartitionKey(path=f"/{partition_key_field}"),
            offer_throughput=400,
        )

    def insert_data(self, payloads: List[Dict[str, Any]]) -> bool:
        """
        Inserts data into collection
        :param payloads:
        :return: boolean indicating success or failure
        """
        for payload in payloads:
            self.container.create_item(body=payload)
        return True

    def select_data(self, query):
        """
        Selects data from collection
        :param query:
        :return:
        """
        items = list(self.container.query_items(
            query=query,
            enable_cross_partition_query=True,
        ))

        return items

    def delete_data(
        self,
        item: Union[Dict[str, Any], str],
        partition_key: str,
    ):
        """
        Removes single document from collection
        :param query:
        :return:
        """

        self.container.delete_item(
            item=item,
            partition_key=partition_key,
        )
        return True

    def update_data(
        self,
        item: Dict[str, Any],
        body: Dict[str, Any],
        upsert: bool = True,
    ):
        """
        Updates data in collection
        :param query:
        :param payload:
        :return:
        """

        if upsert:
            self.container.upsert_item(
                body=body,
            )
        else:

            doc = list(self.container.query_items(
                query=f"SELECT * FROM c WHERE c.id = '{item['id']}' AND c.partitionKey = '{item['partitionKey']}'",
                enable_cross_partition_query=False,
            ))

            if doc:
                payload = doc[0]
                payload.update(body)
                self.container.replace_item(
                    item=payload,
                    body=payload,
                )
        return True


if __name__ == "__main__":
    pass
