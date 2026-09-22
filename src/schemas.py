from pydantic import BaseModel, EmailStr, HttpUrl


class ShortenedUrlRequest(BaseModel):
    original_url: HttpUrl


class ShortenedUrlResponse(BaseModel):
    original_url: HttpUrl
    shortened_url: HttpUrl


class UserRegistrationRequestSchema(BaseModel):
    email: EmailStr
    password: str


class UserRegistrationResponseSchema(BaseModel):
    id: int
    email: EmailStr

    model_config = {"from_attributes": True}
