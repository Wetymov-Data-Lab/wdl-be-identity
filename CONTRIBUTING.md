# Contributing

<details>
<summary><strong>Подготовка окружения</strong></summary>

Репозитории должны находиться рядом:

```text
wdl/
├── wdl-be-identity/
└── wdl-shared/
```

Установите зависимости:

```bash
make install
```
</details>

---

<details>
<summary><strong>Git hooks</strong></summary>

Подключите hooks из репозитория один раз после клонирования:

```bash
git config core.hooksPath .githooks
chmod +x .githooks/*
```

Пример сообщения коммита:

```text
feat(auth): add login endpoint
```
</details>

## Перед pull request

```bash
make check
```

Если изменились модели SQLAlchemy, создайте и проверьте миграцию:

```bash
make migration name="describe schema change"
make migrate
```
