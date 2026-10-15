# IMKON Backend

IMKON — бесплатная платформа для поиска постоянной удалённой работы в Таджикистане. Этот репозиторий содержит первый backend-срез на FastAPI; frontend намеренно не включён.

## Реализовано

- Email-регистрация, одноразовое подтверждение email, access/refresh JWT и отзыв refresh-сессий.
- Профиль соискателя и одно основное резюме с контролем владельца.
- Заявка работодателя, административное одобрение/отклонение и разделение системной роли с ролью участника организации.
- Черновики вакансий, отправка на модерацию, публикация только администратором, публичный поиск и пагинация.
- Один отклик на вакансию на уровне PostgreSQL и контролируемые переходы статуса работодателем.
- Защищённые административные endpoints для пользователей, заявок и вакансий.

## Стек

Python 3.12+, FastAPI, SQLAlchemy 2, Pydantic 2, PostgreSQL, Alembic, JWT и pytest.

## Быстрый запуск

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
# отредактируйте DATABASE_URL и JWT_SECRET_KEY в .env
alembic upgrade head
uvicorn app.main:app --reload
```

Swagger: `http://127.0.0.1:8000/docs`; health-check: `http://127.0.0.1:8000/health`.

## PostgreSQL и миграции

Создайте отдельные базы `imkon` и `imkon_test`; SQLite не поддерживается. Изменения схемы выполняются только через Alembic:

```powershell
alembic revision --autogenerate -m "description"
alembic upgrade head
```

## Администратор и демо-данные

```powershell
python scripts/create_admin.py --email admin@example.com
python scripts/seed_demo.py
```

Пароль администратора запрашивается скрыто; скрипт не содержит стандартного пароля. Demo-данные запускаются вручную и помечают вакансию как тестовую.

## Тесты

Тесты требуют отдельную PostgreSQL-базу и не используют `DATABASE_URL` разработки:

```powershell
$env:TEST_DATABASE_URL="postgresql+psycopg://imkon:password@localhost:5432/imkon_test"
pytest
```

## Следующие этапы

SMTP-доставка, OAuth Google/Telegram, Redis/Celery, WebSocket-чат, обучение, сертификаты, Gemini и React-клиент запланированы, но не имеют фиктивных endpoint-ов в этом срезе.
