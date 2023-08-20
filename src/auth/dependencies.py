from starlette import status
from fastapi import Depends, Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.security.utils import get_authorization_scheme_param
from keycloak.exceptions import KeycloakAuthenticationError

from src.exceptions import HTTPAuthenticationError
from src.auth.service import KeycloakAuthService, KeycloakAdminService
from src.config import settings

token_auth_scheme = HTTPBearer()


def get_authorization_credentials(request: Request) -> HTTPAuthorizationCredentials:
    authorization = request.headers.get("Authorization")
    scheme, credentials = get_authorization_scheme_param(authorization)

    if not (authorization and scheme and credentials):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authenticated"
        )

    if scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid authentication credentials",
        )

    return HTTPAuthorizationCredentials(scheme=scheme, credentials=credentials)


def get_auth_service() -> KeycloakAuthService:
    return KeycloakAuthService(
        realm=settings.keycloak_realm,
        server_url=settings.keycloak_auth_server_url,
        client_id=settings.keycloak_client_id,
        client_secret=settings.keycloak_secret,
        callback_uri="",
    )


def get_admin_service() -> KeycloakAdminService:
    return KeycloakAdminService(
        realm=settings.keycloak_realm,
        server_url=settings.keycloak_auth_server_url,
        client_id=settings.keycloak_client_id,
        client_secret=settings.keycloak_secret,
    )


def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(token_auth_scheme),
    auth_service: KeycloakAuthService = Depends(get_auth_service),
):
    try:
        # Check active and get user info
        return auth_service.userinfo(token.credentials)
    except KeycloakAuthenticationError:
        raise HTTPAuthenticationError("Unauthorized")
    except Exception as e:
        raise HTTPAuthenticationError(str(e))


class RoleChecker:
    def __init__(self, allowed_roles: list):
        self.allowed_roles = allowed_roles

    def __call__(
        self,
        user_info: dict = Depends(get_current_user),
    ):
        # Keycloak realm roles are usually in realm_access.roles
        realm_access = user_info.get("realm_access", {})
        roles = realm_access.get("roles", [])

        # Check exact matches first
        for role in self.allowed_roles:
            if role in roles:
                return user_info

        # Check if roles are prefixed with 'realm:' in the requirements or the token
        # Keycloak roles in token usually just "developer" inside "realm_access".

        clean_allowed = [r.replace("realm:", "") for r in self.allowed_roles]
        for role in clean_allowed:
            if role in roles:
                return user_info

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have enough permissions",
        )
