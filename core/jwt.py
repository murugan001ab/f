import jwt
from datetime import datetime, timedelta, timezone
import os

SECRET_KEY = os.getenv("SECRET_KEY", "super-secret")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

ACCESS_EXPIRE_MIN = int(os.getenv("ACCESS_EXPIRE_MIN", 15))
REFRESH_EXPIRE_DAYS = int(os.getenv("REFRESH_EXPIRE_DAYS", 7))


def create_access_token(data: dict):

    payload = data.copy()

    payload.update({
        "type": "access",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_EXPIRE_MIN),
        "iat": datetime.now(timezone.utc)
    })

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict):

    payload = data.copy()

    payload.update({
        "type": "refresh",
        "exp": datetime.now(timezone.utc) + timedelta(days=REFRESH_EXPIRE_DAYS),
        "iat": datetime.now(timezone.utc)
    })

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_verification_token(user_id: int):

    payload = {
        "user_id": user_id,
        "type": "email_verify",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
        "iat": datetime.now(timezone.utc)
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str):

    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    except jwt.ExpiredSignatureError:
        return None

    except jwt.InvalidTokenError:
        return None