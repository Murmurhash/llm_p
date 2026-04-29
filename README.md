# Защищённый API для работы с большой языковой моделью

FastAPI-сервис с JWT-аутентификацией, SQLite и проксированием запросов к LLM через OpenRouter.

## Стек

- FastAPI + Uvicorn
- SQLAlchemy 2.0 async + aiosqlite (чтобы всё было на `async/await`)
- python-jose для JWT, passlib[bcrypt] для паролей
- httpx для похода в OpenRouter
- uv как пакетный менеджер, ruff для линтинга

## Структура файлов

```
app/
├── main.py              # create_app(), /health, lifespan
├── core/
│   ├── config.py        # настройки из .env
│   ├── security.py      # JWT + хэш пароля
│   └── errors.py        # свои исключения
├── db/
│   ├── base.py
│   ├── session.py
│   └── models.py        # User, ChatMessage
├── schemas/             # Pydantic-схемы запросов/ответов
├── repositories/        # работа с БД, голый SQL/ORM
├── services/
│   └── openrouter_client.py
├── usecases/            # логика: auth, chat
└── api/                 # роуты + DI


## Установка и запуск

### 1. Установка uv

```bash
pip install uv
```

### 2. Настройка переменных окружения

Скопируйте `.env.example` в `.env` и заполните `OPENROUTER_API_KEY`:

```bash
cp .env.example .env
```

### 3. Запуск приложения

```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

После запуска Swagger UI доступен по адресу: http://localhost:8000/docs

### 4. Проверка кода линтером

```bash
uv run ruff check
```

## Эндпоинты

### Auth
- `POST /auth/register` — Регистрация пользователя
- `POST /auth/login` — Логин и получение JWT
- `GET /auth/me` — Профиль текущего пользователя

### Chat
- `POST /chat` — Отправка запроса к LLM
- `GET /chat/history` — Получение истории диалога
- `DELETE /chat/history` — Очистка истории диалога

### Health
- `GET /health` — Проверка статуса сервера

## Демо

## Скриншоты

Все скриншоты— в `docs/screenshots/`. Регистрация сделана на `dinasdrv@gmail.com`, email видно на каждом.

### Регистрация — `POST /auth/register`

![Register request](docs/screenshots/01_register_request.png)
![Register response](docs/screenshots/02_register_response.png)

### Логин — `POST /auth/login`

`POST /auth/login` — запрос:'
![Login request](docs/screenshots/03_login_request.png)

`POST /auth/login` — ответ:
![Login response](docs/screenshots/04_login_response.png)

### Запрос к LLM — `POST /chat`

`POST /chat` — отправка запроса к LLM:
![POST /chat](docs/screenshots/05_post_chat.png)

### История — `GET /chat/history`

`GET /chat/history` — получение истории:
![GET /chat/history](docs/screenshots/07_get_history.png)

### Очистка — `DELETE /chat/history`

`DELETE /chat/history` — очистка истории:

![DELETE /chat/history — очистка истории](docs/screenshots/08_delete_history.png)
