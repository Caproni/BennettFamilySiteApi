#!
# -*- coding: utf-8 -*-
"""
Created on 2022-08-20
@author: Edmund Bennett
@email: bennettedmund@gmail.com
"""

import os
from dotenv import load_dotenv
from typing import Optional
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

from bfsa.utils.logger import logger as log


def get_vault_secret(
    secret_name: str,
    production: bool,
) -> Optional[str]:

    if not production:
        load_dotenv()
        return os.getenv(secret_name.upper())

    try:
        client = SecretClient(
            vault_url="https://family-key-vault.vault.azure.net",
            credential=DefaultAzureCredential(),
        )
        return client.get_secret(secret_name).value
    except Exception as e:
        log.warning(f"Connection to SecretClient could not be established. Error: {e}")
        return os.getenv(secret_name.upper())
