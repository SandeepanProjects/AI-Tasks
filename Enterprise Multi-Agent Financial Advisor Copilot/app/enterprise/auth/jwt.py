import jwt
import datetime

from app.core.config import settings


SECRET_KEY = "super-secret-key"

ALGORITHM = "HS256"


class JWTService:

    @staticmethod
    def create_token(
        user_id: str,
        role: str
    ):

        payload = {
            "user_id": user_id,
            "role": role,
            "exp": datetime.datetime.utcnow()
            + datetime.timedelta(hours=6)
        }

        return jwt.encode(
            payload,
            SECRET_KEY,
            algorithm=ALGORITHM
        )


    @staticmethod
    def decode_token(token: str):

        return jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )