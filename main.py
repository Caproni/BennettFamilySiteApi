#!
# -*- coding: utf-8 -*-
"""
Created on 2022-06-26
@author: Edmund Bennett
@email: bennettedmund@gmail.com
"""

import uvicorn

import bfsa.controllers.bootstrap as bootstrap


app = bootstrap.server


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=bootstrap.host,
        port=bootstrap.port,
        reload=True,
    )
