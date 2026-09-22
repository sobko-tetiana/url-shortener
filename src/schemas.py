from pydantic import BaseModel, HttpUrl


class ShortenedUrlRequest(BaseModel):
    original_url: HttpUrl


class ShortenedUrlResponse(BaseModel):
    original_url: HttpUrl
    shortened_url: HttpUrl
