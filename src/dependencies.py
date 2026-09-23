import os

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.interfaces import JWTAuthManagerInterface
from src.models import UserModel
from src.token_manager import JWTAuthManager
from src.security import InvalidTokenError



def get_jwt_auth_manager() -> JWTAuthManagerInterface:
    """Create a JWT manager using environment configuration."""
    return JWTAuthManager(
        secret_key_access=os.getenv(
            "JWT_ACCESS_SECRET",
            "change-this-access-secret",
        ),
        secret_key_refresh=os.getenv(
            "JWT_REFRESH_SECRET",
            "change-this-refresh-secret",
        ),
        algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
    )


def get_token(request: Request) -> str:
    authorization: str = request.headers.get("Authorization")

    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is missing"
        )

    scheme, _, token = authorization.partition(" ")

    if scheme.lower() != "bearer" or not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header format."
        )

    return token


async def get_current_user(
    token: str = Depends(get_token),
    db: AsyncSession = Depends(get_db),
    jwt_manager: JWTAuthManagerInterface = Depends(get_jwt_auth_manager),
) -> UserModel:
    try:
        payload = jwt_manager.decode_access_token(token)
        user_id = payload.get("user_id")
    except InvalidTokenError as error:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Invalid or expired access token.",
        ) from error

    user = await db.scalar(select(UserModel).where(UserModel.id == user_id))
    if user is None:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Invalid or expired access token.",
        )
    return user


def get_optional_token(request: Request) -> str | None:
    authorization = request.headers.get("Authorization")
    if not authorization:
        return None

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header format."
        )

    return token


async def get_current_user_optional(
    token: str | None = Depends(get_optional_token),
    db: AsyncSession = Depends(get_db),
    jwt_manager: JWTAuthManagerInterface = Depends(get_jwt_auth_manager),
) -> UserModel | None:
    if token is None:
        return None

    try:
        payload = jwt_manager.decode_access_token(token)
        user_id = payload.get("user_id")
    except InvalidTokenError as error:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Invalid or expired access token.",
        ) from error

    user = await db.scalar(select(UserModel).where(UserModel.id == user_id))
    if user is None:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Invalid or expired access token.",
        )
    return user
