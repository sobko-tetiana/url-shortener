from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.codec import encrypt_id
from src.models import UrlModel
from src.schemas import ShortenedUrlRequest, ShortenedUrlResponse
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

    shortened_url_code = encrypt_id(
        settings.ENCRYPTION_KEY, settings.ENCRYPTION_TWEAK, url.id
    )
    shortened_url = f"{settings.APP_BASE_URL}/{shortened_url_code}"
    return ShortenedUrlResponse(
        original_url=data.original_url,
        shortened_url=shortened_url
    )
