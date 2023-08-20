from fastapi import APIRouter, HTTPException, Depends, status
from keycloak.exceptions import KeycloakAuthenticationError

from src.auth.service import KeycloakAuthService
from src.auth.dependencies import get_auth_service
from src.auth.schemas import LoginDto, RefreshTokenDto, LogoutDto

router = APIRouter()


@router.post("/login")
def login(
    data: LoginDto, auth_service: KeycloakAuthService = Depends(get_auth_service)
):
    try:
        return auth_service.login(data.username, data.password)
    except KeycloakAuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/client-login")
def client_login(auth_service: KeycloakAuthService = Depends(get_auth_service)):
    try:
        return auth_service.client_login()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/refresh")
def refresh(
    data: RefreshTokenDto, auth_service: KeycloakAuthService = Depends(get_auth_service)
):
    try:
        return auth_service.refresh_token(data.refresh_token)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/logout")
def logout(
    data: LogoutDto, auth_service: KeycloakAuthService = Depends(get_auth_service)
):
    try:
        auth_service.logout(data.refresh_token)
        return {"message": "Logged out successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
