from functools import lru_cache
from urllib.parse import quote_plus

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ---------------------------------------------------------------------------
    # App
    # ---------------------------------------------------------------------------

    APP_VERSION:     str        = "0.1.0"
    PROJECT_NAME:    str        = "WDL Identity API"
    PROJECT_DESC:    str        = "API аутентификации и управления учетными записями"

    DEBUG:           bool       = False

    CORS_DISABLE:    bool       = False
    CORS_REGEX:      str        = r"https://.*\.wdl\.ru"
    PROD_SERVER_URL: str | None = None

    # ---------------------------------------------------------------------------
    # PostgreSQL
    # ---------------------------------------------------------------------------

    POSTGRES_SERVER:               str | None = "localhost"
    POSTGRES_USER:                 str | None = "postgres"
    POSTGRES_PASSWORD:             str | None = "postgres"
    POSTGRES_DB:                   str | None = "wdl_identity"
    POSTGRES_PORT:                 str | None = "5432"
    SQLALCHEMY_ASYNC_DATABASE_URI: str | None = None
    SQLALCHEMY_ECHO:               bool       = False
    DATABASE_CREATE_TABLES:        bool       = True

    # ---------------------------------------------------------------------------
    # OAuth / JWT
    # ---------------------------------------------------------------------------

    JWT_SECRET_KEY:                   SecretStr = Field(
        default=SecretStr("development-only-change-me-at-least-32-chars"),
        min_length=32,
    )
    JWT_ISSUER:                       str       = "wdl-identity"
    JWT_AUDIENCE:                     str       = "wdl-api"
    JWT_ACCESS_TOKEN_EXPIRES_MINUTES: int       = Field(default=15, gt=0)
    JWT_REFRESH_TOKEN_EXPIRES_DAYS:   int       = Field(default=30, gt=0)

    # ---------------------------------------------------------------------------
    # Redis
    # ---------------------------------------------------------------------------

    REDIS_HOST:       str              = "127.0.0.1"
    REDIS_PORT:       int              = Field(default=6379, ge=1, le=65_535)
    REDIS_DB:         int              = Field(default=0, ge=0)
    REDIS_PASSWORD:   SecretStr | None = None
    REDIS_URL:        str | None       = None
    REDIS_KEY_PREFIX: str              = "wdl:identity"

    @model_validator(mode="after")
    def assemble_database_uri(self) -> "Settings":
        if not self.SQLALCHEMY_ASYNC_DATABASE_URI:
            self.SQLALCHEMY_ASYNC_DATABASE_URI = (
                f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )
        return self

    @model_validator(mode="after")
    def assemble_redis_uri(self) -> "Settings":
        if not self.REDIS_URL:
            password = ""
            if self.REDIS_PASSWORD is not None and self.REDIS_PASSWORD.get_secret_value():
                password = f":{quote_plus(self.REDIS_PASSWORD.get_secret_value())}@"
            self.REDIS_URL = f"redis://{password}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return self

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
