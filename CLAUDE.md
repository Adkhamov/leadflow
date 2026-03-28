# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Запуск

```bash
# Основной дашборд
streamlit run dashboard.py

# Вебхук-сервер для статусов Wazzup (доставлено/прочитано/ответили) — отдельный терминал
python webhook_server.py  # порт 8502

# Разовая синхронизация лидов из AmoCRM
python sync.py
```

## Архитектура

Один файл на одну зону ответственности. Без фреймворков кроме Streamlit + FastAPI.

**Поток данных:**
```
AmoCRM API → sync.py → SQLite (leadflow.db) → ai_processor.py (Claude/OpenAI) → dashboard.py
                                                                                 ↑
Wazzup API ←────────────────────────────── webhook_server.py ──────────────────┘
```

**Ключевые файлы:**
- `dashboard.py` — весь Streamlit UI, все страницы в одном файле через блоки `elif page ==`
- `database.py` — весь доступ к SQLite; `init_db()` идемпотентен, вызывается при старте
- `ai_processor.py` — каталог моделей (`MODELS`), `process_lead()` для сегментации + генерации сообщения, `generate_hypotheses()` для гипотез кампаний
- `amo_client.py` — REST API AmoCRM; батч-загрузка контактов и заметок чтобы избежать N+1 запросов
- `wazzup_client.py` — API рассылки Wazzup; активный канал читается из настроек БД через `get_active_channel_id()`
- `sync.py` — полная синхронизация: все лиды, батч-загрузка контактов + заметок, сохранение `last_activity_at`
- `webhook_server.py` — FastAPI приложение, принимает статусы от Wazzup (доставлено/прочитано/ответили)

## База данных

SQLite в файле `leadflow.db` (в .gitignore). Схема находится в `database.py:init_db()`.

Основные таблицы: `leads`, `token_usage`, `hypotheses`, `message_events`, `settings`.

Настройки пользователя хранятся в таблице `settings` через `get_setting()`/`set_setting()` — включая `amo_access_token`, `wazzup_channel_id`, `selected_model`.

При добавлении колонок в существующую БД использовать `ALTER TABLE ... ADD COLUMN` с try/except — SQLite не поддерживает `IF NOT EXISTS` для колонок.

## AI сегментация

Каждый лид анализируется по 7 критериям: segment, score, drop_reason_category, drop_stage_type, return_potential, engagement_level, best_approach_type, best_channel. Результат сохраняется через `save_ai_result_full()`.

ID гипотез от Claude ("A","B","C") prefixируются именем воронки перед сохранением — чтобы избежать конфликтов PRIMARY KEY между разными воронками.

`_parse_json()` умеет восстанавливать обрезанный JSON — если модель упёрлась в max_tokens посередине ответа, находит последний полный `}` и закрывает массив.

## Переменные окружения

Все секреты в `.env` (в .gitignore). Пример в `.env.example`. На Streamlit Cloud — в панели Secrets в формате TOML.

Обязательные: `AMO_SUBDOMAIN`, `AMO_ACCESS_TOKEN`, `WAZZUP_API_KEY`, `ANTHROPIC_API_KEY`.
Опциональные: `OPENAI_API_KEY` (для GPT моделей), `WAZZUP_CHANNEL_ID` (переопределяет настройку из БД).

## Поддерживаемые модели

Определены в `ai_processor.MODELS`: `claude-opus-4-6`, `claude-sonnet-4-6`, `claude-haiku-4-5`, `gpt-4o`, `gpt-4o-mini`, `gpt-4-turbo`. Активная модель хранится в `settings.selected_model`.
