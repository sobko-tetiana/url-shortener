from pydantic import BaseModel, EmailStr, Field, HttpUrl


class ShortenedUrlRequest(BaseModel):
    original_url: HttpUrl


class ShortenedUrlResponse(BaseModel):
    original_url: HttpUrl
    shortened_url: HttpUrl


class UserRegistrationRequestSchema(BaseModel):
    email: EmailStr
    password: str = Field(max_length=72)


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


class UserLogoutRequestSchema(BaseModel):
    refresh_token: str


class MessageResponseSchema(BaseModel):
    message: str
