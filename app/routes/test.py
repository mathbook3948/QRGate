from fastapi import APIRouter

from ..utils import insert_user

routes = APIRouter(prefix="/test", tags=["test"])

@routes.get("/insert")
async def insert(user_id: str, user_pwd: str):
    try:
        insert_user(user_id, user_pwd)
        return {"success": True}
    except Exception as e:
        print(e)
        return {"success": False}
