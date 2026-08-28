from wdl_be_identity.infrastructure.config import settings

tags_metadata = [
    {
        "name": "system",
        "description": "Служебные операции API и проверка доступности приложения.",
    },
]

servers = (
    [
        {"url": "http://localhost:8000", "description": "Development environment"},
        {"url": settings.PROD_SERVER_URL, "description": "Production environment"},
    ]
    if settings.PROD_SERVER_URL
    else []
)
