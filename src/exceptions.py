import typing

from fastapi import status
from starlette.exceptions import HTTPException


class HTTPAuthenticationError(HTTPException):
    def __init__(self, detail) -> None:
        super().__init__(
            status.HTTP_401_UNAUTHORIZED, detail, headers={"WWW-Authenticate": "Bearer"}
        )
