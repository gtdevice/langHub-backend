from pydantic import BaseModel, EmailStr
from typing import Optional


class SignInRequest(BaseModel):
    email: EmailStr
    password: str


class SignInResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict
    expires_in: int 