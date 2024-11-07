from fastapi import FastAPI

from app.logger import logger
from app.users.router import router as router_users
from app.movies.router import router as router_movie
from app.movies.favorites.router import router as router_favorites


app = FastAPI()


app.include_router(router_users)
app.include_router(router_movie)
app.include_router(router_favorites)