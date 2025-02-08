import uuid
import bcrypt
from redis.asyncio import Redis
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from starlette.websockets import WebSocket
from utils import ConnectionManager
from utils import create_token
from utils import decode_token
from utils import select_by_id_user

class Email(BaseModel):
    email: str


class Login(BaseModel):
    id: str
    pwd: str


routes = APIRouter(prefix="/qr", tags=["qr"])
manager = ConnectionManager()
r = Redis()

"""
가게에 있는 패드에 인증 시작 누름 -> jwt 발급 -> qr 보여짐 -> 사용자가 스캔시 로그인 화면으로 이동
"""


@routes.get("/start")
async def start():
    uuid4 = uuid.uuid4()
    token = create_token(str(uuid4))
    redis_result = await r.set("current", str(uuid4), ex=300)

    if redis_result:
        return {
            "success": True,
            "token": token
        }
    else :
        raise HTTPException(status_code=500, detail="Redis 접속 중 오류가 발생했습니다")


@routes.get("/auth/{token}")
async def get(login: Login, token: str):
    uuid = decode_token(token)

    if not uuid:
        raise HTTPException(status_code=401, detail="JWT 토큰이 유효하지 않습니다")
    elif not (r.exists("current") and r.get("current") != uuid):
        raise HTTPException(status_code=401, detail="세션이 만료되었습니다")

    user = select_by_id_user(login.id)

    if bcrypt.checkpw(login.pwd.encode(), user.user_pwd):
        await r.set(uuid, True, ex=300)
        if r.exists("current"):
            await r.delete("current")
        return {
            "success": True
        }
    else:
        raise HTTPException(status_code=401, detail="비밀번호가 일치하지 않습니다")


@routes.websocket("ws/loading/{token}")
async def loading_websocket(websocket: WebSocket, token: str):
    uuid = decode_token(token)

    if not uuid:
        raise HTTPException(status_code=401, detail="JWT 토큰이 유효하지 않습니다")

    await manager.connect(websocket)
    try:
        while True:
            if r.exists(uuid) and r.get(uuid) == True:
                await manager.send_personal_message("success", websocket)
                break
    except Exception as e:
        await manager.send_personal_message("error", websocket)
        print(e)
    finally:
        await manager.disconnect(websocket)
