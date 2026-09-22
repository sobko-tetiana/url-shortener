from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.codec import decode_base62, decrypt_id, encode_base62, encrypt_id
from src.models import UrlModel, UserModel
from src.schemas import (
    ShortenedUrlRequest,
    ShortenedUrlResponse,
    UserRegistrationRequestSchema,
    UserRegistrationResponseSchema
)
from src.security import hash_password
from src.settings import Settings, get_settings


router = APIRouter()


@router.post("/shorten", response_model=ShortenedUrlResponse)
async def get_shortened_url(
    data: ShortenedUrlRequest,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings)
) -> ShortenedUrlResponse:
    url = UrlModel(original_url=str(data.original_url))
    db.add(url)
    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise e

    obfuscated_id = encrypt_id(
        settings.ENCRYPTION_KEY, settings.ENCRYPTION_TWEAK, url.id
    )
    shortened_url_code = encode_base62(obfuscated_id)
    shortened_url = f"{settings.APP_BASE_URL}/{shortened_url_code}"
    return ShortenedUrlResponse(
        original_url=data.original_url,
        shortened_url=shortened_url
    )


@router.get("/{shortened_url_code}", response_model=ShortenedUrlResponse)
async def redirect_to_original_url(
    shortened_url_code: str,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings)
) -> ShortenedUrlResponse:
    obfuscated_id = decode_base62(shortened_url_code)
    original_id = decrypt_id(
        settings.ENCRYPTION_KEY, settings.ENCRYPTION_TWEAK, obfuscated_id
    )
    url = await db.get(UrlModel, original_id)
    if not url:
        raise HTTPException(status_code=404, detail="URL not found")

    return ShortenedUrlResponse(
        original_url=url.original_url,
        shortened_url=f"{settings.APP_BASE_URL}/{shortened_url_code}"
    )


@router.post(
    "/register",
    response_model=UserRegistrationResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    data: UserRegistrationRequestSchema,
    db: AsyncSession = Depends(get_db),
) -> UserModel:
    email = str(data.email)
    if await db.scalar(select(UserModel).where(UserModel.email == email)):
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "A user with this email already exists."
        )

    user = UserModel(
        email=email,
        hashed_password=hash_password(data.password),
    )
    db.add(user)
    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Something went wrong. Try again later."
        ) from e

    return user
