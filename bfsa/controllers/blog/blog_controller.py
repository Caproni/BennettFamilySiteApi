#!
# -*- coding: utf-8 -*-
"""
Created on 2022-07-16
@author: Edmund Bennett
@email: bennettedmund@gmail.com
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter
from pydantic import BaseModel

from bfsa.db.environment import client_factory
from bfsa.sql.create_select import create_select
from bfsa.utils.return_json import return_json
from bfsa.utils.create_guid import create_guid
from bfsa.utils.logger import logger as log


router = APIRouter()


class BlogPart(BaseModel):
    """
    Pydantic model for blog part
    """

    text: str
    image: Optional[bytes] = None
    image_caption: Optional[str] = None


class BlogModel(BaseModel):
    """
    Pydantic model for blog
    """

    title: str
    author: str
    theme: str
    sub_theme: Optional[str]
    blog_parts: list[BlogPart]
    tags: list[str]
    references: list[str]
    image: Optional[bytes] = None


@router.post("/api/createBlog")
def create_blog(
    blog: BlogModel,
):
    """
    Add blog object to database
    """
    log.info("Calling create_blog")

    client = client_factory()

    blog_dict = dict(blog)
    blog_dict.update({"id": create_guid()})
    blog_dict.update({"partitionKey": "blog"})

    try:
        success = client.insert_data(
            [blog_dict],
        )
        if not success:
            log.critical(f"Failed to insert blog. Check logs for details.")
            return return_json(
                message="Failed to insert blog.",
                success=False,
            )
    except Exception as e:
        log.critical(f"Failed to insert blog. Error: {e}")
        return return_json(
            message="Failed to insert blog.",
            success=False,
        )

    return return_json(
        message="Successfully inserted blog.",
        success=True,
    )


@router.get("/api/readBlog")
def read_blog(
    where: Dict[str, Any] = None,
):
    """
    Read blog
    """
    log.info("Calling read_blog")

    client = client_factory()

    if where is None:
        where = {}
    where.update({"partitionKey": "blog"})

    query = create_select(where)

    try:
        data = client.select_data(
            query=query,
        )
        if data:
            return return_json(
                message="Successfully selected blog data.",
                success=True,
                content=data,
            )
    except Exception as e:
        log.critical(f"Failed to select blog data. Error: {e}")
        return return_json(
            message="Failed to select blog data.",
            success=False,
        )

    log.critical(f"Failed to select blog data. Check logs for details.")
    return return_json(
        message="Failed to select blog data.",
        success=False,
    )


@router.patch("/api/updateBlog")
def update_blog(
    blog_id: str,
    patch: Dict[str, Any],
):
    """
    Update blog
    """
    log.info("Calling update_blog")

    client = client_factory()

    patch.update({"id": blog_id})
    patch.update({"partitionKey": "blog"})

    try:
        success = client.update_data(
            item={"id": blog_id, "partitionKey": "blog"},
            body=patch,
            upsert=False,
        )
        if not success:
            log.critical(f"Failed to update blog. Check logs for details.")
            return return_json(
                message="Failed to update blog.",
                success=False,
            )
    except Exception as e:
        log.critical(f"Failed to update blog. Error: {e}")
        return return_json(
            message="Failed to update blog.",
            success=False,
        )

    return return_json(
        message="Successfully updated blog.",
        success=True,
    )


@router.delete("/api/deleteBlog")
def delete_blog(
    blog_id: str,
):
    """
    Delete blog
    """
    log.info("Calling delete_blog")

    client = client_factory()

    try:
        success = client.delete_data(
            item=blog_id,
            partition_key="blog",
        )
        if not success:
            log.critical(f"Failed to delete blog. Check logs for details.")
            return return_json(
                message="Failed to delete blog.",
                success=False,
            )
    except Exception as e:
        log.critical(f"Failed to delete blog. Error: {e}")
        return return_json(
            message="Failed to delete blog.",
            success=False,
        )

    return return_json(
        message="Successfully deleted blog.",
        success=True,
    )
