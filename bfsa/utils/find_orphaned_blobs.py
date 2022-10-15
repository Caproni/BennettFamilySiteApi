#!
# -*- coding: utf-8 -*-
"""
╔═╗╦ ╦╔╦╗  ╔╦╗┬┌─┐┬┌┬┐┌─┐┬
║ ╦╠═╣ ║║   ║║││ ┬│ │ ├─┤│
╚═╝╩ ╩═╩╝  ═╩╝┴└─┘┴ ┴ ┴ ┴┴─┘

Created on 2022-10-15
@author: Edmund Bennett
@email: edmund.bennett@ghd.com
"""

from typing import List

from bfsa.utils.logger import logger as log


def find_orphaned_blobs(
    blob_container: str,
    ids: List[str],
) -> List[str]:
    """
    Finds orphaned blobs within a specific container, by comparing with a list of IDs
    :param blob_container: Indicates a specific container within the relevant blob storage
    :param ids: List of IDs of blobs which should exist. Blobs whose IDs are not in this list are considered to be orphans.
    :return: List of URLs corresponding to orphaned blobs within the specified container
    """
    log.info("Calling find_orphaned_blobs")
    return []


if __name__ == "__main__":
    pass
