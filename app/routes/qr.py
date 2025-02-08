import uuid

import aioredis
import bcrypt
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from redis.asyncio import Redis
from starlette.websockets import WebSocket
from utils import ConnectionManager, select_by_id_user, create_token, decode_token

class Login(BaseModel):
    id: str
    pwd: str

routes = APIRouter(prefix="/qr", tags=["qr"])
manager = ConnectionManager()
r = Redis()

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
    else:
        raise HTTPException(status_code=500, detail="Redis 접속 중 오류가 발생했습니다")

@routes.post("/auth/{token}")
async def get(login: Login, token: str):
    uuid4 = decode_token(token)

    if not uuid4:
        raise HTTPException(status_code=401, detail="JWT 토큰이 유효하지 않습니다")

    # Redis의 비동기 메서드 호출 시 await 추가
    elif not (await r.exists("current") and await r.get("current") != uuid4):
        raise HTTPException(status_code=401, detail="세션이 만료되었습니다")

    user = select_by_id_user(login.id)

    if bcrypt.checkpw(login.pwd.encode(), user.user_pwd.encode()):
        await r.set(uuid4, "TRUE", ex=300)
        if await r.exists("current"):
            await r.delete("current")
        return {
            "success": True
        }
    else:
        raise HTTPException(status_code=401, detail="비밀번호가 일치하지 않습니다")

@routes.websocket("/ws/loading/{token}")
async def loading_websocket(websocket: WebSocket, token: str):
    uuid = decode_token(token)
    if not uuid:
        raise HTTPException(status_code=401, detail="JWT 토큰이 유효하지 않습니다")

    await manager.connect(websocket)

    redis = await aioredis.from_url("redis://localhost")
    pubsub = redis.pubsub()
    await pubsub.subscribe(uuid)

    try:
        async for message in pubsub.listen():
            if message["type"] == "message" and message["data"] == b"TRUE":
                await manager.send_personal_message("success", websocket)
                break
    except Exception as e:
        await manager.send_personal_message("error", websocket)
        print(e)
    finally:
        await manager.disconnect(websocket)
        await pubsub.unsubscribe(uuid)
