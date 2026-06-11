from jose import jwt

SECRET_KEY = "SUPER_SECRET"

ALGORITHM = "HS256"


def create_access_token(
    user_id: str
):

    return jwt.encode(
        {"sub": user_id},
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def decode_token(token):

    return jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM]
    )