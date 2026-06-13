# import jwt
# import datetime

# from app.core.config import settings


# SECRET_KEY = "super-secret-key"

# ALGORITHM = "HS256"


# class JWTService:

#     @staticmethod
#     def create_token(
#         user_id: str,
#         role: str
#     ):

#         payload = {
#             "user_id": user_id,
#             "role": role,
#             "exp": datetime.datetime.utcnow()
#             + datetime.timedelta(hours=6)
#         }

#         return jwt.encode(
#             payload,
#             SECRET_KEY,
#             algorithm=ALGORITHM
#         )


#     @staticmethod
#     def decode_token(token: str):

#         return jwt.decode(
#             token,
#             SECRET_KEY,
#             algorithms=[ALGORITHM]
#         )



# pip install python-jose[cryptography]

# app/auth/jwt.py

from datetime import datetime
from datetime import timedelta
from datetime import timezone

from jose import JWTError
from jose import jwt

from app.config.settings import settings


class JWTService:

    @staticmethod
    def create_access_token(
        user_id: str,
        role: str
    ) -> str:

        expire = datetime.now(
            timezone.utc
        ) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

        payload = {

            "sub": user_id,

            "role": role,

            "exp": expire
        }

        return jwt.encode(
            payload,

            settings.JWT_SECRET,

            algorithm=settings.JWT_ALGORITHM
        )


    @staticmethod
    def verify_token(
        token: str
    ) -> dict:

        try:

            payload = jwt.decode(
                token,

                settings.JWT_SECRET,

                algorithms=[
                    settings.JWT_ALGORITHM
                ]
            )

            return payload

        except JWTError:

            raise ValueError(
                "Invalid token"
            )