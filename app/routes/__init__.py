from fastapi import APIRouter
from .qr import routes as qr_routes
from .test import routes as test_routes

routes = APIRouter(prefix="/api")

routes.include_router(qr_routes)
routes.include_router(test_routes)