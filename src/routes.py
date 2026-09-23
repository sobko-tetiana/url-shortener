from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.codec import decode_base62, decrypt_id, encode_base62, encrypt_id
from src.dependencies import (
    get_current_user,
    get_current_user_optional,
    get_jwt_auth_manager,
)
from src.interfaces import JWTAuthManagerInterface
from src.models import RefreshTokenModel, UrlModel, UserModel
from src.schemas import (
    MessageResponseSchema,
    ShortenedUrlRequest,
    ShortenedUrlResponse,
    TokenRefreshRequestSchema,
    TokenRefreshResponseSchema,
    UserLoginRequestSchema,
    UserLoginResponseSchema,
    UserLogoutRequestSchema,
    UserRegistrationRequestSchema,
    UserRegistrationResponseSchema,
    UserUrlResponse
)
from src.security import InvalidTokenError, hash_password, verify_password
from src.settings import Settings, get_settings


router = APIRouter()


def _build_shortened_url(url_id: int, settings: Settings) -> str:
    obfuscated_id = encrypt_id(
        settings.ENCRYPTION_KEY, settings.ENCRYPTION_TWEAK, url_id
    )
    shortened_url_code = encode_base62(obfuscated_id)
    return f"{settings.APP_BASE_URL}/{shortened_url_code}"


@router.post("/shorten", response_model=ShortenedUrlResponse)
async def get_shortened_url(
    data: ShortenedUrlRequest,
    user: UserModel | None = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings)
) -> ShortenedUrlResponse:
    original_url = str(data.original_url)
    user_id = user.id if user else None
    user_id_filter = (
        UrlModel.user_id.is_(None) if user_id is None
        else UrlModel.user_id == user_id
    )

    existing_url = await db.scalar(
        select(UrlModel).where(
            UrlModel.original_url == original_url, user_id_filter
        )
    )
    if existing_url is not None:
        return ShortenedUrlResponse(
            original_url=original_url,
            shortened_url=_build_shortened_url(existing_url.id, settings),
        )

    url = UrlModel(original_url=original_url, user_id=user_id)
    db.add(url)
    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise e

    return ShortenedUrlResponse(
        original_url=original_url,
        shortened_url=_build_shortened_url(url.id, settings),
    )


@router.get("/urls", response_model=list[UserUrlResponse])
async def list_user_urls(
    user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings)
) -> list[UserUrlResponse]:
    urls = await db.scalars(
        select(UrlModel)
        .where(UrlModel.user_id == user.id)
        .order_by(UrlModel.created_at.desc())
    )

    return [
        UserUrlResponse(
            original_url=url.original_url,
            shortened_url=_build_shortened_url(url.id, settings),
            click_count=url.click_count,
        )
        for url in urls
    ]


@router.delete(
    "/urls/{shortened_url_code}",
    response_model=MessageResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def delete_user_url(
    shortened_url_code: str,
    user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings)
) -> MessageResponseSchema:
    obfuscated_id = decode_base62(shortened_url_code)
    original_id = decrypt_id(
        settings.ENCRYPTION_KEY, settings.ENCRYPTION_TWEAK, obfuscated_id
    )
    url = await db.get(UrlModel, original_id)
    if url is None or url.user_id != user.id:
        raise HTTPException(status_code=404, detail="URL not found")

    try:
        await db.delete(url)
        await db.commit()
    except Exception as error:
        await db.rollback()
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Something went wrong. Try again later.",
        ) from error

    return MessageResponseSchema(message="Shortened URL deleted successfully.")


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

    url.click_count += 1
    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise e

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


@router.post(
    "/login",
    response_model=UserLoginResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def login_user(
    data: UserLoginRequestSchema,
    db: AsyncSession = Depends(get_db),
    jwt_manager: JWTAuthManagerInterface = Depends(get_jwt_auth_manager),
) -> UserLoginResponseSchema:
    user = await db.scalar(
        select(UserModel).where(UserModel.email == str(data.email))
    )

    if user is None or not verify_password(
        data.password,
        user.hashed_password,
    ):
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Invalid email or password.",
        )

    refresh_jwt = jwt_manager.create_refresh_token({"user_id": user.id})
    refresh_token = RefreshTokenModel.create(
        user_id=user.id,
        days_valid=7,
        token=refresh_jwt,
    )
    db.add(refresh_token)

    try:
        await db.commit()
    except Exception as error:
        await db.rollback()
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Something went wrong. Try again later.",
        ) from error

    access_token = jwt_manager.create_access_token({"user_id": user.id})
    return UserLoginResponseSchema(
        access_token=access_token,
        refresh_token=refresh_jwt,
    )


@router.post(
    "/logout",
    response_model=MessageResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def logout_user(
    data: UserLogoutRequestSchema,
    db: AsyncSession = Depends(get_db),
) -> MessageResponseSchema:
    refresh_token = await db.scalar(
        select(RefreshTokenModel).where(
            RefreshTokenModel.token == data.refresh_token
        )
    )

    if refresh_token is None:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Refresh token not found.",
        )

    try:
        await db.delete(refresh_token)
        await db.commit()
    except Exception as error:
        await db.rollback()
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Something went wrong. Try again later.",
        ) from error

    return MessageResponseSchema(
        message="Logged out successfully."
    )


@router.post(
    "/refresh",
    response_model=TokenRefreshResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def refresh_access_token(
    data: TokenRefreshRequestSchema,
    db: AsyncSession = Depends(get_db),
    jwt_manager: JWTAuthManagerInterface = Depends(get_jwt_auth_manager),
) -> TokenRefreshResponseSchema:
    try:
        payload = jwt_manager.decode_refresh_token(data.refresh_token)
        user_id = payload.get("user_id")
    except InvalidTokenError as error:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Invalid or expired refresh token.",
        ) from error

    stored_token = await db.scalar(
        select(RefreshTokenModel).where(
            RefreshTokenModel.token == data.refresh_token
        )
    )
    if stored_token is None or stored_token.user_id != user_id:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Refresh token not found.",
        )

    user = await db.scalar(
        select(UserModel).where(
            UserModel.id == user_id
        )
    )
    if user is None:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "User account is unavailable.",
        )

    access_token = jwt_manager.create_access_token({"user_id": user.id})
    return TokenRefreshResponseSchema(
        access_token=access_token
    )
