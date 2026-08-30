from app.infrastructure.config import Settings
from app.main import create_app


def test_app_metadata() -> None:
    app = create_app()

    assert app.title == "WDL Identity API"
    assert app.version == "0.1.0"


def test_database_uri_is_assembled() -> None:
    settings = Settings(
        POSTGRES_SERVER="database",
        POSTGRES_USER="identity",
        POSTGRES_PASSWORD="secret",
        POSTGRES_DB="identity",
        POSTGRES_PORT="5433",
    )

    assert settings.SQLALCHEMY_ASYNC_DATABASE_URI == (
        "postgresql+asyncpg://identity:secret@database:5433/identity"
    )


def test_boolean_settings_are_parsed_from_strings() -> None:
    settings = Settings(DEBUG="False", CORS_DISABLE="True")  # type: ignore[arg-type]

    assert settings.DEBUG is False
    assert settings.CORS_DISABLE is True


def test_redis_uri_is_assembled() -> None:
    settings = Settings(
        REDIS_HOST="redis",
        REDIS_PORT=6380,
        REDIS_DB=2,
        REDIS_PASSWORD="p@ssword",
    )

    assert settings.REDIS_URL == "redis://:p%40ssword@redis:6380/2"
