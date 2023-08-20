from pydantic import BaseModel


class LoginDto(BaseModel):
    username: str
    password: str


class RefreshTokenDto(BaseModel):
    refresh_token: str


class LogoutDto(BaseModel):
    refresh_token: str
