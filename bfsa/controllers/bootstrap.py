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
from bfsa.controllers.mapping import map_controller
from bfsa.controllers.media import media_controller
from bfsa.controllers.content import content_controller
from bfsa.controllers.papers import papers_controller
from bfsa.controllers.recipes import (
    recipe_controller,
    recipe_step_controller,
    ingredient_controller,
    ingredient_usage_controller,
    equipment_controller,
    equipment_usage_controller,
    recipe_detail_controller,
)
from bfsa.controllers.movie_database import movie_database_controller

from bfsa.controllers.blog import blog_controller


port = 4646
host = "localhost"

server = FastAPI()

server.include_router(admin_controller.router, tags=["Administration"])
server.include_router(authentication_controller.router, tags=["Authentication"])

server.include_router(family_tree_person_controller.router, tags=["Family Tree People"])
server.include_router(
    family_tree_relationship_controller.router, tags=["Family Tree Relationships"]
)
server.include_router(
    family_tree_data_source_controller.router, tags=["Family Tree Data Sources"]
)

server.include_router(map_controller.router, tags=["Maps"])

server.include_router(media_controller.router, tags=["Media"])

server.include_router(movie_database_controller.router, tags=["Movie Database"])

server.include_router(content_controller.router, tags=["Content"])

server.include_router(papers_controller.router, tags=["Papers"])

server.include_router(recipe_controller.router, tags=["Recipes"])
server.include_router(recipe_step_controller.router, tags=["Recipe Steps"])
server.include_router(ingredient_controller.router, tags=["Ingredients"])
server.include_router(ingredient_usage_controller.router, tags=["Ingredient Usage"])
server.include_router(equipment_controller.router, tags=["Equipment"])
server.include_router(equipment_usage_controller.router, tags=["Equipment Usage"])
server.include_router(recipe_detail_controller.router, tags=["Recipe Details"])

server.include_router(blog_controller.router, tags=["Blog"])

origins = [
    "http://localhost",
    "https://localhost:443",
    "http://localhost:4200",
    "http://127.0.0.1:4200",
]

server.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
