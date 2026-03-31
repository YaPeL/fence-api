from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # defaults for local dev/tests; override via env in docker-compose/.env
    database_url: str = "postgresql+asyncpg://fence_api:fence_api@localhost:5432/fence_api"
    jwt_secret: str = "change_me"
    jwt_algorithm: str = "HS256"
    admin_token_ttl_minutes: int = 60

    admin_username: str = "admin"
    admin_password: str = "change_me"
    service_name: str = "fence-api"


settings = Settings()
