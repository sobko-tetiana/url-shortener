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


class UserLoginRequestSchema(BaseModel):
    email: EmailStr
    password: str


class UserLoginResponseSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
