#!
# -*- coding: utf-8 -*-
"""
Created on 2022-08-20
@author: Edmund Bennett
@email: bennettedmund@gmail.com
"""

from typing import Optional
from os import environ
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

from bfsa.utils.logger import logger as log


def get_vault_secret(
    secret_name: str,
    production: bool,
) -> Optional[str]:

    if not production:
        return environ[secret_name.upper()]

    try:
        client = SecretClient(
            vault_url="https://family-key-vault.vault.azure.net",
            credential=DefaultAzureCredential(),
        )
        return client.get_secret(secret_name).value
    except Exception as e:
        log.critical(f"Connection to SecretClient could not be established. Error: {e}")
