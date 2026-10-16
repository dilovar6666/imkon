# IMKON — текущий прогресс

Дата проверки: 2026-10-16

## Завершено в этой итерации

- Добавлена модель `GoogleIdentity` и миграция `20261016_0004`.
- Добавлен `POST /api/v1/auth/google` для входа по Google ID token.
- Добавлен `POST /api/v1/auth/google/link` для безопасной привязки к уже подтверждённому аккаунту.
- Google ID token проверяется через `google-auth`: подпись, `aud`, `iss`, `exp` и `email_verified`.
- Новый Google-пользователь получает только роль `seeker`.
- Автоматическое объединение с существующим email запрещено; требуется вход и явная привязка.
- Добавлен Google Identity Services компонент Frontend и `VITE_GOOGLE_CLIENT_ID`.
- Добавлены контролируемые тесты первого входа, повторного входа, конфликта email и отсутствующей настройки.

## Проверки

- Alembic: миграция применена к тестовой PostgreSQL базе.
- Backend pytest: `13 passed`.
- Python compileall: успешно.
- Frontend TypeScript: успешно.
- Frontend production build: успешно.
- Реальный HTTP `/api/v1/auth/google` с недействительным токеном: `401`.
- Google Login с реальным аккаунтом не проверялся, так как требует интерактивного входа и настройки OAuth consent screen.

## Состояние этапов

- Backend, PostgreSQL, JWT, email-регистрация: частично реализовано; SMTP и rate limiting требуют production-настройки.
- React Frontend и дизайн: реализованы локальные страницы и сборка.
- Работодатели, вакансии, резюме, отклики и админ-модерация: реализованы базовые API.
- HR/Kanban: частично реализовано.
- Обучение, Gemini, WebSocket-чат, Redis/Celery, Telegram: не реализованы.
- Google OAuth: backend ID-token flow и frontend GSI подключены; требуется настройка Google Cloud и реальный smoke-тест.
- Три языка: частично; основной интерфейс — русский.
- Production/deployment: не готов без SMTP, rate limiting, внешних сервисов и HTTPS-проверки.

## Следующее действие

1. В Google Cloud создать OAuth Web Client и заполнить `GOOGLE_CLIENT_ID` в Backend и `VITE_GOOGLE_CLIENT_ID` во Frontend.
2. Добавить локальный origin `http://localhost:5174` и production origin `https://imkon.khayrkhoh.tj` в Authorized JavaScript origins.
3. Для выбранного GIS ID-token flow Authorized redirect URIs не требуются.
4. Выполнить интерактивный вход Google и проверить создание/повторный вход пользователя.
