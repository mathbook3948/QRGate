import uuid
import os
import aioredis
import bcrypt
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from starlette.websockets import WebSocket
from ..utils import ConnectionManager, select_by_id_user, create_token, decode_token


class Login(BaseModel):
    id: str
    pwd: str


routes = APIRouter(prefix="/qr", tags=["qr"])
manager = ConnectionManager()

# 환경변수에서 Redis 연결 정보 가져오기
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
redis = aioredis.from_url(REDIS_URL)


@routes.get("/start")
async def start():
    uuid4 = uuid.uuid4()
    token = create_token(str(uuid4))

    redis_result = await redis.set("current", str(uuid4), ex=300)
    if redis_result:
        return {"success": True, "token": token}
    else:
        raise HTTPException(status_code=500, detail="Redis 접속 중 오류가 발생했습니다")


@routes.post("/auth/{token}")
async def get(login: Login, token: str):
    uuid4 = decode_token(token)
    if not uuid4:
        raise HTTPException(status_code=401, detail="JWT 토큰이 유효하지 않습니다")

    current_uuid = await redis.get("current")
    if not current_uuid or current_uuid.decode("utf-8") != uuid4:
        raise HTTPException(status_code=401, detail="세션이 만료되었습니다")

    user = select_by_id_user(login.id)
    if user and bcrypt.checkpw(login.pwd.encode(), user.user_pwd.encode()):
        await redis.publish(uuid4, "TRUE")
        await redis.delete("current")
        return {"success": True}
    else:
        raise HTTPException(status_code=401, detail="비밀번호가 일치하지 않습니다")


@routes.websocket("/ws/loading/{token}")
async def loading_websocket(websocket: WebSocket, token: str):
    uuid4 = decode_token(token)
    print(uuid4)
    if not uuid4:
        await websocket.close(code=1008)
        raise HTTPException(status_code=401, detail="JWT 토큰이 유효하지 않습니다")

    await manager.connect(websocket)

    pubsub = redis.pubsub()
    await pubsub.subscribe(uuid4)

    try:
        async for message in pubsub.listen():
            print(message)
            if message["type"] == "message" and message["data"] == b"TRUE":
                await manager.send_personal_message("success", websocket)
                break
    except Exception as e:
        await manager.send_personal_message("error", websocket)
        print(e)
    finally:
        await manager.disconnect(websocket)
        await pubsub.unsubscribe(uuid4)