from wdl_be_identity.infrastructure.config import settings

tags_metadata = [
    {
        "name": "System",
        "description": "Служебные операции API и проверка доступности приложения.",
    },
    {
        "name": "Accounts",
        "description": "Создание аккаунтов, получение данных и управление жизненным циклом.",
    },
    {
        "name": "Registration",
        "description": "Регистрация пользователя с email, профилем и паролем.",
    },
    {
        "name": "Profiles",
        "description": "Персональные и публичные данные профиля аккаунта.",
    },
    {
        "name": "Identifiers",
        "description": "Email, телефон и внешние идентификаторы аккаунта, их проверка и настройки.",
    },
    {
        "name": "Passwords",
        "description": "Управление парольными данными аккаунта без раскрытия хешей.",
    },
    {
        "name": "Second Factors",
        "description": "Политика 2FA и управление вторыми факторами.",
    },
    {
        "name": "Recovery Codes",
        "description": "Управление одноразовыми кодами восстановления.",
    },
    {
        "name": "Sessions",
        "description": "Создание, обновление и завершение сессий аккаунта.",
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
