# @wdl/wdl-be-identity

Identity API для аутентификации и управления учетными записями WDL.

Репозиторий содержит базовый каркас сервиса: FastAPI, слои application/domain/
infrastructure/presentation, асинхронный SQLAlchemy, Alembic, Docker и CI.

<details>
<summary><strong>Requirements</strong></summary>

- Python 3.12
- [uv](https://docs.astral.sh/uv/)
- Docker и Docker Compose
- соседний каталог `../wdl-shared` для локальной разработки

</details>

---

<details>
<summary><strong>Installation</strong></summary>

```bash
make env
make install
make up
```

API в Docker будет доступно по адресу `http://localhost:8002`, документация —
`http://localhost:8002/docs`. Команда `make dev` запускает API на порту `8000`.

</details>

---

<details>
<summary><strong>Project commands</strong></summary>

| Команда                         | Назначение                              |
|---------------------------------|-----------------------------------------|
| `make env`                      | Создать `.env` из `.env.example`        |
| `make install`                  | Установить зависимости                  |
| `make dev`                      | Запустить API в режиме разработки       |
| `make lint`                     | Проверить код с помощью Ruff            |
| `make format`                   | Отформатировать код с помощью Ruff      |
| `make typecheck`                | Проверить типы с помощью mypy            |
| `make test`                     | Запустить тесты                         |
| `make check`                    | Запустить lint, typecheck и tests        |
| `make migrate`                  | Применить миграции Alembic              |
| `make migration name="message"` | Создать автогенерируемую миграцию      |
| `make up`                       | Запустить Docker Compose                |
| `make down`                     | Остановить сервисы и удалить их volumes |

</details>

Правила разработки и подключение Git hooks описаны в [CONTRIBUTING.md](CONTRIBUTING.md).
