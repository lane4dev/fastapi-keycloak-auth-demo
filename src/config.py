from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Awesome API"
    app_version: str = "0.1.0"

    api_prefix: str = "/api"

    debug: bool = True

    secret_key: str = "super_secretkey"

    class Config:
        env_file = ".env"

settings = Settings()
