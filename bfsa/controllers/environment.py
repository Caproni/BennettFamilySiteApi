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


with open("credentials/blob_config.json", "r") as credentials_file:
    credentials = load(credentials_file)


if __name__ == "__main__":
    pass
