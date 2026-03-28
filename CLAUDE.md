# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the app

```bash
# Main dashboard
streamlit run dashboard.py

# Webhook server (for Wazzup delivery/read/reply statuses) — separate terminal
python webhook_server.py  # port 8502

# One-time sync of all leads from AmoCRM
python sync.py
```

## Architecture

Single-file-per-concern Python app. No frameworks beyond Streamlit + FastAPI.

**Data flow:**
```
AmoCRM API → sync.py → SQLite (leadflow.db) → ai_processor.py (Claude/OpenAI) → dashboard.py
                                                                                 ↑
Wazzup API ←────────────────────────────── webhook_server.py ──────────────────┘
```

**Key files:**
- `dashboard.py` — entire Streamlit UI, all pages in one file with `elif page ==` blocks
- `database.py` — all SQLite access; `init_db()` is idempotent, call it on startup
- `ai_processor.py` — model catalog (`MODELS` dict), `process_lead()` for segmentation + message, `generate_hypotheses()` for campaign hypotheses
- `amo_client.py` — AmoCRM REST API; uses batch fetching for contacts/notes to avoid N+1
- `wazzup_client.py` — Wazzup messaging API; active channel read from DB settings via `get_active_channel_id()`
- `sync.py` — bulk sync: fetches all leads, batch-fetches contacts + notes, saves `last_activity_at`
- `webhook_server.py` — FastAPI app receiving Wazzup status webhooks (delivered/read/replied)

## Database

SQLite at `leadflow.db` (gitignored). Schema lives in `database.py:init_db()`.

Key tables: `leads`, `token_usage`, `hypotheses`, `message_events`, `settings`.

Settings (user preferences) are stored in the `settings` table via `get_setting()`/`set_setting()`. This includes `amo_access_token`, `wazzup_channel_id`, `selected_model`.

When adding columns to existing deployments, use `ALTER TABLE ... ADD COLUMN` with try/except — SQLite doesn't support `IF NOT EXISTS` for columns.

## AI segmentation

Each lead is analyzed with 7 criteria (segment, score, drop_reason_category, drop_stage_type, return_potential, engagement_level, best_approach_type, best_channel). Results saved via `save_ai_result_full()`.

Hypothesis IDs from Claude ("A","B","C") are prefixed with a sanitized pipeline name before saving to avoid PRIMARY KEY conflicts across pipelines.

`_parse_json()` includes truncation recovery — if the model hits max_tokens mid-JSON, it finds the last complete `}` and closes the array.

## Environment

All secrets in `.env` (gitignored). See `.env.example` for required keys. On Streamlit Cloud, secrets go in the Secrets panel as TOML.

Required: `AMO_SUBDOMAIN`, `AMO_ACCESS_TOKEN`, `WAZZUP_API_KEY`, `ANTHROPIC_API_KEY`.
Optional: `OPENAI_API_KEY` (for GPT models), `WAZZUP_CHANNEL_ID` (overrides DB setting).

## Supported models

Defined in `ai_processor.MODELS`: `claude-opus-4-6`, `claude-sonnet-4-6`, `claude-haiku-4-5`, `gpt-4o`, `gpt-4o-mini`, `gpt-4-turbo`. Active model stored in `settings.selected_model`.
