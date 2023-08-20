from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Awesome API"
    app_version: str = "0.1.0"

    api_prefix: str = "/api"

    debug: bool = True

    secret_key: str = "super_secretkey"

    keycloak_realm: str = None
    keycloak_auth_server_url: str = None
    keycloak_client_id: str = None
    keycloak_secret: str = None
    keycloak_cookie_key: str = None

    class Config:
        env_file = ".env"

settings = Settings()
