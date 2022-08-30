#!
# -*- coding: utf-8 -*-
"""
Created on 2022-06-26
@author: Edmund Bennett
@email: bennettedmund@gmail.com
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from bfsa.controllers.admin import admin_controller
from bfsa.controllers.authentication import authentication_controller
from bfsa.controllers.family_tree import (
    family_tree_person_controller,
    family_tree_relationship_controller,
    family_tree_data_source_controller,
)
from bfsa.controllers.media import media_controller
from bfsa.controllers.photos import photos_controller
from bfsa.controllers.recipes import (
    recipe_controller,
    recipe_step_controller,
    ingredient_controller,
    ingredient_usage_controller,
    equipment_controller,
    recipe_detail_controller,
)


port = 4646
host = "localhost"

server = FastAPI()

server.include_router(admin_controller.router)
server.include_router(authentication_controller.router)

server.include_router(family_tree_person_controller.router)
server.include_router(family_tree_relationship_controller.router)
server.include_router(family_tree_data_source_controller.router)

server.include_router(media_controller.router)

server.include_router(photos_controller.router)

server.include_router(recipe_controller.router)
server.include_router(recipe_step_controller.router)
server.include_router(ingredient_controller.router)
server.include_router(ingredient_usage_controller.router)
server.include_router(equipment_controller.router)
server.include_router(recipe_detail_controller.router)

origins = [
    "http://localhost",
    "https://localhost:443",
    "http://localhost:4200",
]

server.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
