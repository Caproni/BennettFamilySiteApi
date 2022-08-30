#!
# -*- coding: utf-8 -*-
"""
Created on 2022-07-17
@author: Edmund Bennett
@email: bennettedmund@gmail.com
"""


def return_json(message, success=True, content=None, exceptions=None):
    """
    Convenience wrapper for ASGI return objects
    """
    resp_dict = {"success": success, "message": message}
    if content:
        resp_dict.update({"content": content})
    if exceptions:
        resp_dict.update({"exceptions": [str(e) for e in exceptions]})
    return resp_dict
