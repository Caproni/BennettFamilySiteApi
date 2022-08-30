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

from json import load

from bfsa.utils.get_vault_secret import get_vault_secret


with open("credentials/blob_config.json", "r") as credentials_file:
    blob_credentials = load(credentials_file)

blob_credentials["credentials"] = get_vault_secret("bennettfamilyblobs-credentials")


if __name__ == "__main__":
    pass
