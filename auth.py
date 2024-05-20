import bcrypt
from datetime import datetime, timedelta
from jose import JWTError, jwt
from .dependencies import get_current_user
import secrets

SECRET_KEY = secrets.token_urlsafe(32)

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed_password.decode("utf-8")

def create_jwt_token(user_id: int, username: str) -> str:
    expires_delta = timedelta(hours=9)
    expires = datetime.now() + expires_delta
    to_encode = {"sub": str(user_id), "exp": expires, "username": username}
    token = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return token

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

def get_current_user_from_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        return user_id
    except JWTError:
        return None