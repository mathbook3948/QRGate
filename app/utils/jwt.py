import jwt
import datetime
from dotenv import load_dotenv
import random
import os

load_dotenv()

def create_token(uuid : str):
    """
    Jwt 토큰을 생성하고 반환합니다
    :returns: (token, random)
    """
    payload = {
        "uuid": uuid,
        "exp": datetime.datetime.now() + datetime.timedelta(minutes=5)
    }

    token = jwt.encode(payload, os.getenv("SECRET_KEY"), algorithm="HS256")
    return token

def decode_token(token: str):
    """
    Jwt 토큰을 받아 유효 여부를 검사합니다
    """
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=["HS256"])
        return payload.get("uuid")
    except jwt.ExpiredSignatureError:
        return None