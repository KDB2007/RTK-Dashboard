from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/rtk_dash"
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60
    jwt_refresh_expire_days: int = 30

    cors_origins: str = "http://localhost:5173"

    rate_limit_per_minute: int = 100
    rate_limit_login_per_minute: int = 10

    batch_max_size: int = 500

    admin_email: str = "admin@rtk.ai"
    admin_password: str = "admin123"


settings = Settings()
