# IMKON

IMKON — бесплатная платформа поиска постоянной удалённой работы для пользователей Таджикистана и других стран. Репозиторий содержит FastAPI Backend и React Frontend. Платежей, комиссий и фриланс-заказов нет.

## Что работает

- Email-регистрация с одноразовым кодом в development, вход, JWT refresh/logout, профиль и основное резюме.
- Заявка работодателя с одобрением администратором; черновик вакансии, модерация и публикация.
- Публичный каталог и детальная страница только актуальных опубликованных вакансий; отклик с резюме и защита от повторной отправки.
- Админ-интерфейс для заявок работодателей, вакансий и блокировки пользователей.
- Отдельные честные экраны обучения и AI: сервисы пока не подключены.

## Структура

`app/` — модульный FastAPI Backend: `core/` конфигурация, БД и JWT; `routers/` API пользователей, работодателей, резюме, вакансий, откликов и администратора; `models.py` и `schemas.py` — модели и контракты. `alembic/` хранит миграции, `scripts/` — ручные команды создания администратора и демо-данных, `tests/` — pytest. `frontend/` содержит Vite + React + TypeScript, Tailwind и компоненты в стиле shadcn/ui. Дизайн Open Horizons разработан через Google Stitch и адаптирован к реальным API; подробности: `STITCH_DESIGN.md`, `FRONTEND_ARCHITECTURE.md`, `DESIGN_SYSTEM.md`, `FRONTEND_API_GAPS.md`.

## Backend на Windows PowerShell

Нужны Python 3.12+ и запущенный PostgreSQL. Создайте отдельные базы приложения и тестов. SQLite не поддерживается. Команды установки для обычного окружения Windows:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

В `.env` укажите свой `DATABASE_URL` с драйвером `postgresql+psycopg`, случайный `JWT_SECRET_KEY` длиной не менее 32 символов и `CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173`. Не добавляйте `.env` в Git. После настройки:

```powershell
.\.venv\Scripts\alembic.exe upgrade head
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Swagger: `http://127.0.0.1:8000/docs`; OpenAPI: `http://127.0.0.1:8000/openapi.json`; health: `http://127.0.0.1:8000/health`. Миграции проверены на отдельной локальной PostgreSQL-базе; таблицы не создаются через `create_all()` при запуске.

## Frontend на Windows PowerShell

В другом терминале:

```powershell
Set-Location frontend
Copy-Item .env.example .env.local
npm.cmd install
npm.cmd run dev -- --host 127.0.0.1 --port 5173
```

Откройте `http://127.0.0.1:5173`. `VITE_API_URL` в `frontend/.env.local` должен указывать на текущий Backend, по умолчанию `http://127.0.0.1:8000/api/v1`. Если используете другой порт Vite, добавьте его origin в `CORS_ORIGINS` и перезапустите Backend. Docker не требуется.

## Администратор, демо и тесты

```powershell
.\.venv\Scripts\python.exe scripts/create_admin.py --email admin@example.com
.\.venv\Scripts\python.exe scripts/seed_demo.py
$env:TEST_DATABASE_URL="postgresql+psycopg://test_user:your_password@127.0.0.1:5432/imkon_test"
.\.venv\Scripts\python.exe -m pytest -q
Set-Location frontend
npm.cmd run typecheck
npm.cmd run build
npm.cmd run test:browser
```

Пароль администратора вводится скрыто. Демо-скрипт запускается вручную и помечает вакансии. `test:browser` использует установленный Microsoft Edge, локальные серверы и тестовую PostgreSQL-базу; он создаёт тестовые аккаунты. Для дополнительного сценария администрирования передайте в окружении `IMKON_QA_ADMIN_EMAIL` и `IMKON_QA_ADMIN_PASSWORD` тестового администратора. Никогда не направляйте browser QA на production.

PWA-кэш проверяется отдельно после `npm.cmd run build`: запустите `npm.cmd run preview -- --host 127.0.0.1 --port 5175`, затем в другом терминале из `frontend/` выполните `npm.cmd run test:pwa`. Тест требует установленного Microsoft Edge.

## Ограничения

Production SMTP, rate limiting, полноценное управление HR, TG/EN локализация, Gemini, курсы, чат, уведомления и расширенный поиск ещё не реализованы. Refresh JWT не хранится долговременно на клиенте. Точные пробелы API и результаты проверок описаны в `FRONTEND_API_GAPS.md` и `FRONTEND_QA.md`.
