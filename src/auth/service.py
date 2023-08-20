import functools

from keycloak import KeycloakOpenID, KeycloakAdmin


class KeycloakAuthService:
    def __init__(
        self,
        server_url: str,
        client_id: str,
        client_secret: str,
        realm: str,
        callback_uri: str,
        timeout: int = 10,
    ) -> None:
        self.server_url = server_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.realm = realm
        self.callback_uri = callback_uri
        self.timeout = timeout

        self.keycloak_openid = KeycloakOpenID(
            server_url=server_url,
            client_id=client_id,
            realm_name=realm,
            client_secret_key=client_secret,
            timeout=timeout,
        )

    @functools.cached_property
    def open_id_configuration(self) -> dict:
        return self.keycloak_openid.well_known()

    @functools.cached_property
    def token_uri(self):
        return self.open_id_configuration.get("token_endpoint")

    def login(self, username, password):
        return self.keycloak_openid.token(username, password)

    def client_login(self):
        return self.keycloak_openid.token(grant_type="client_credentials")

    def refresh_token(self, refresh_token):
        return self.keycloak_openid.refresh_token(refresh_token)

    def logout(self, refresh_token):
        return self.keycloak_openid.logout(refresh_token)

    def has_resource_permission(self, token: str, resource: str) -> bool:
        return self.keycloak_openid.has_uma_access(token, resource)

    def userinfo(self, token: str) -> dict:
        return self.keycloak_openid.decode_token(token)


class KeycloakAdminService:
    def __init__(
        self,
        server_url: str,
        client_id: str,
        client_secret: str,
        realm: str,
    ) -> None:
        self.server_url = server_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.realm = realm

    def get_admin_client(self) -> KeycloakAdmin:
        return KeycloakAdmin(
            server_url=self.server_url,
            client_id=self.client_id,
            client_secret_key=self.client_secret,
            realm_name=self.realm,
            user_realm_name=self.realm,
            verify=True,
        )
