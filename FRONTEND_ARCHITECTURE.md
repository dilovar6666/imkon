# Архитектура Frontend IMKON

`frontend/` — одно приложение React 18 + Vite 6 + TypeScript. Маршруты разделены на публичные, пользовательские и административные; Backend остаётся единым FastAPI-приложением.

| Файл | Назначение |
| --- | --- |
| `src/lib/api.ts` | Централизованные типизированные запросы, обработка HTTP-ошибок, access/refresh JWT. |
| `src/state.tsx` | Состояние авторизации. Access token — в `sessionStorage`, refresh — в памяти. |
| `src/pages.tsx` | Главная, каталог, вакансия с откликом, вход и регистрация. |
| `src/private-pages.tsx` | Профиль, резюме, заявка работодателя, создание вакансии и администрирование. |
| `src/future-pages.tsx` | Самостоятельные экраны обучения, AI и миссии; отсутствующие функции явно недоступны. |
| `src/components.tsx` и `src/components/ui/button.tsx` | Навигация, состояния и примитив кнопки на Radix Slot/CVA в стиле shadcn/ui. |
| `src/styles.css`, `src/redesign.css`, `postcss.config.cjs` | Базовые стили, слой Open Horizons по Stitch и Tailwind 4 utilities без Preflight-сброса. |
| `public/` | Manifest, SVG-иконка и service worker: кэшируются только собственные статические assets. |
| `tests/browser.mjs` | Playwright через установленный Edge: адаптивность, сценарии и axe. |

Базовый адрес API задаётся `VITE_API_URL` (`frontend/.env.example`). Для локального Vite origin необходимо явно добавить в `CORS_ORIGINS` Backend. Контент сейчас доступен на русском; TG/EN тексты требуют редакторской проверки до включения переключателя.
