import sqlite3
import json
from datetime import datetime

DB_PATH = "leadflow.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY,
            name TEXT,
            pipeline_id INTEGER,
            pipeline_name TEXT,
            stage_id INTEGER,
            stage_name TEXT,
            status_id INTEGER,
            created_at INTEGER,
            closed_at INTEGER,
            price INTEGER,
            responsible_name TEXT,
            tags TEXT,
            notes TEXT,
            contact_name TEXT,
            contact_phone TEXT,
            contact_email TEXT,
            raw_json TEXT,
            last_activity_at INTEGER,
            -- AI fields
            ai_segment TEXT,
            ai_score INTEGER,
            ai_reason TEXT,
            ai_message TEXT,
            ai_processed_at TEXT,
            -- AI segmentation criteria
            drop_reason_category TEXT,
            drop_stage_type TEXT,
            return_potential TEXT,
            engagement_level TEXT,
            best_approach_type TEXT,
            best_channel TEXT,
            hypothesis_id TEXT,
            -- Sending
            message_sent INTEGER DEFAULT 0,
            message_sent_at TEXT,
            wazzup_message_id TEXT,
            message_status TEXT,
            delivered_at TEXT,
            read_at TEXT,
            replied_at TEXT,
            reply_text TEXT,
            synced_at TEXT
        );

        CREATE TABLE IF NOT EXISTS campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            created_at TEXT,
            lead_ids TEXT,
            status TEXT DEFAULT 'draft'
        );

        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        );

        CREATE TABLE IF NOT EXISTS message_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_id INTEGER,
            wazzup_message_id TEXT,
            event_type TEXT,
            event_data TEXT,
            ts TEXT
        );

        CREATE TABLE IF NOT EXISTS hypotheses (
            id TEXT PRIMARY KEY,
            pipeline_name TEXT,
            name TEXT,
            description TEXT,
            criteria TEXT,
            lead_ids TEXT,
            lead_count INTEGER,
            estimated_response_rate INTEGER,
            priority INTEGER,
            approach TEXT,
            sample_message TEXT,
            created_at TEXT
        );

        CREATE TABLE IF NOT EXISTS token_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT,
            model TEXT,
            provider TEXT,
            operation TEXT,
            lead_id INTEGER,
            input_tokens INTEGER,
            output_tokens INTEGER,
            cost_usd REAL
        );
    """)
    conn.commit()
    conn.close()


def upsert_lead(lead: dict):
    conn = get_conn()
    existing = conn.execute("SELECT id FROM leads WHERE id = ?", (lead["id"],)).fetchone()
    la = lead.get("last_activity_at")
    if existing:
        conn.execute("""
            UPDATE leads SET
                name=?, pipeline_id=?, pipeline_name=?, stage_id=?, stage_name=?,
                status_id=?, created_at=?, closed_at=?, price=?, responsible_name=?,
                tags=?, notes=?, contact_name=?, contact_phone=?, contact_email=?,
                raw_json=?, last_activity_at=?, synced_at=?
            WHERE id=?
        """, (
            lead["name"], lead["pipeline_id"], lead["pipeline_name"],
            lead["stage_id"], lead["stage_name"], lead["status_id"],
            lead["created_at"], lead["closed_at"], lead["price"],
            lead["responsible_name"], lead["tags"], lead["notes"],
            lead["contact_name"], lead["contact_phone"], lead["contact_email"],
            lead["raw_json"], la, datetime.now().isoformat(), lead["id"]
        ))
    else:
        conn.execute("""
            INSERT INTO leads (
                id, name, pipeline_id, pipeline_name, stage_id, stage_name,
                status_id, created_at, closed_at, price, responsible_name,
                tags, notes, contact_name, contact_phone, contact_email,
                raw_json, last_activity_at, synced_at
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            lead["id"], lead["name"], lead["pipeline_id"], lead["pipeline_name"],
            lead["stage_id"], lead["stage_name"], lead["status_id"],
            lead["created_at"], lead["closed_at"], lead["price"],
            lead["responsible_name"], lead["tags"], lead["notes"],
            lead["contact_name"], lead["contact_phone"], lead["contact_email"],
            lead["raw_json"], la, datetime.now().isoformat()
        ))
    conn.commit()
    conn.close()


def save_ai_result_full(lead_id: int, result: dict):
    """Save full AI segmentation result with all 7 criteria."""
    conn = get_conn()
    conn.execute("""
        UPDATE leads SET
            ai_segment=?, ai_score=?, ai_reason=?, ai_message=?, ai_processed_at=?,
            drop_reason_category=?, drop_stage_type=?, return_potential=?,
            engagement_level=?, best_approach_type=?, best_channel=?
        WHERE id=?
    """, (
        result.get("segment"), result.get("score"), result.get("reason"),
        result.get("message"), datetime.now().isoformat(),
        result.get("drop_reason_category"), result.get("drop_stage_type"),
        result.get("return_potential"), result.get("engagement_level"),
        result.get("best_approach_type"), result.get("best_channel"),
        lead_id
    ))
    conn.commit()
    conn.close()


def save_ai_result(lead_id: int, segment: str, score: int, reason: str, message: str):
    conn = get_conn()
    conn.execute("""
        UPDATE leads SET ai_segment=?, ai_score=?, ai_reason=?, ai_message=?, ai_processed_at=?
        WHERE id=?
    """, (segment, score, reason, message, datetime.now().isoformat(), lead_id))
    conn.commit()
    conn.close()


def mark_message_sent(lead_id: int, wazzup_message_id: str):
    conn = get_conn()
    conn.execute("""
        UPDATE leads SET message_sent=1, message_sent_at=?, wazzup_message_id=?, message_status='sent'
        WHERE id=?
    """, (datetime.now().isoformat(), wazzup_message_id, lead_id))
    conn.commit()
    conn.close()


def update_message_status(lead_id: int, status: str):
    conn = get_conn()
    conn.execute("UPDATE leads SET message_status=? WHERE id=?", (status, lead_id))
    conn.commit()
    conn.close()


def get_leads(filters: dict = None) -> list:
    conn = get_conn()
    query = "SELECT * FROM leads WHERE 1=1"
    params = []
    if filters:
        if filters.get("segment"):
            query += " AND ai_segment=?"
            params.append(filters["segment"])
        if filters.get("not_sent"):
            query += " AND message_sent=0"
        if filters.get("has_phone"):
            query += " AND contact_phone IS NOT NULL AND contact_phone != ''"
        if filters.get("has_ai"):
            query += " AND ai_segment IS NOT NULL"
    query += " ORDER BY created_at DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def save_hypotheses(hypotheses: list, pipeline_name: str):
    conn = get_conn()
    # Clear old hypotheses for this pipeline
    conn.execute("DELETE FROM hypotheses WHERE pipeline_name=?", (pipeline_name,))
    # Prefix ID with sanitized pipeline name to avoid collisions across pipelines
    prefix = "".join(c for c in pipeline_name if c.isalnum())[:12]
    for h in hypotheses:
        unique_id = f"{prefix}_{h['id']}"
        conn.execute("""
            INSERT OR REPLACE INTO hypotheses (id, pipeline_name, name, description, criteria, lead_ids,
                lead_count, estimated_response_rate, priority, approach, sample_message, created_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            unique_id, pipeline_name, h["name"], h["description"],
            json.dumps(h.get("criteria", []), ensure_ascii=False),
            json.dumps(h.get("lead_ids", []), ensure_ascii=False),
            h.get("lead_count", 0), h.get("estimated_response_rate", 0),
            h.get("priority", 3), h.get("approach", ""), h.get("sample_message", ""),
            datetime.now().isoformat()
        ))
        # Tag leads with unique hypothesis id
        for lid in h.get("lead_ids", []):
            conn.execute("UPDATE leads SET hypothesis_id=? WHERE id=?", (unique_id, lid))
    conn.commit()
    conn.close()


def get_hypotheses(pipeline_name: str = None) -> list:
    conn = get_conn()
    if pipeline_name:
        rows = conn.execute("SELECT * FROM hypotheses WHERE pipeline_name=? ORDER BY priority", (pipeline_name,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM hypotheses ORDER BY priority").fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        d["criteria"] = json.loads(d.get("criteria") or "[]")
        d["lead_ids"] = json.loads(d.get("lead_ids") or "[]")
        result.append(d)
    return result


def get_leads_inactive(pipeline_name: str, days: int) -> list:
    """Leads from pipeline with no activity for N days."""
    from time import time
    cutoff = int(time()) - days * 86400
    conn = get_conn()
    rows = conn.execute("""
        SELECT * FROM leads
        WHERE pipeline_name=?
          AND (last_activity_at IS NULL OR last_activity_at < ?)
          AND status_id NOT IN (142)
        ORDER BY last_activity_at ASC
    """, (pipeline_name, cutoff)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def record_message_event(lead_id: int, wazzup_message_id: str, event_type: str, event_data: dict = None):
    """event_type: delivered | read | replied | error"""
    conn = get_conn()
    ts = datetime.now().isoformat()
    conn.execute("""
        INSERT INTO message_events (lead_id, wazzup_message_id, event_type, event_data, ts)
        VALUES (?,?,?,?,?)
    """, (lead_id, wazzup_message_id, event_type, json.dumps(event_data or {}, ensure_ascii=False), ts))

    if event_type == "delivered":
        conn.execute("UPDATE leads SET message_status='delivered', delivered_at=? WHERE wazzup_message_id=?",
                     (ts, wazzup_message_id))
    elif event_type == "read":
        conn.execute("UPDATE leads SET message_status='read', read_at=? WHERE wazzup_message_id=?",
                     (ts, wazzup_message_id))
    elif event_type == "replied":
        reply_text = (event_data or {}).get("text", "")
        conn.execute("UPDATE leads SET message_status='replied', replied_at=?, reply_text=? WHERE id=?",
                     (ts, reply_text, lead_id))
    elif event_type == "error":
        conn.execute("UPDATE leads SET message_status='error' WHERE wazzup_message_id=?",
                     (wazzup_message_id,))

    conn.commit()
    conn.close()


def get_message_analytics(days: int = 30) -> dict:
    conn = get_conn()
    cutoff = (datetime.now().replace(hour=0, minute=0, second=0)
              .strftime("%Y-%m-%d"))

    row = conn.execute(f"""
        SELECT
            COUNT(*) FILTER (WHERE message_sent=1) as sent,
            COUNT(*) FILTER (WHERE message_status='delivered') as delivered,
            COUNT(*) FILTER (WHERE message_status='read') as read_count,
            COUNT(*) FILTER (WHERE message_status='replied') as replied,
            COUNT(*) FILTER (WHERE message_status='error') as errors,
            COUNT(*) FILTER (WHERE replied_at IS NOT NULL
                AND (julianday(replied_at) - julianday(message_sent_at)) * 24 <= 24) as replied_24h
        FROM leads
        WHERE message_sent=1
          AND message_sent_at >= date('now', '-{days} days')
    """).fetchone()

    result = dict(row) if row else {}

    # Daily funnel
    daily = conn.execute(f"""
        SELECT date(message_sent_at) as day,
               COUNT(*) as sent,
               COUNT(*) FILTER (WHERE message_status IN ('delivered','read','replied')) as delivered,
               COUNT(*) FILTER (WHERE message_status IN ('read','replied')) as read_count,
               COUNT(*) FILTER (WHERE message_status='replied') as replied,
               COUNT(*) FILTER (WHERE message_status='error') as errors
        FROM leads
        WHERE message_sent=1
          AND message_sent_at >= date('now', '-{days} days')
        GROUP BY day ORDER BY day DESC
    """).fetchall()
    result["daily"] = [dict(r) for r in daily]

    # Error details
    errors = conn.execute("""
        SELECT me.ts, me.event_data, l.name, l.contact_phone
        FROM message_events me
        JOIN leads l ON me.lead_id = l.id
        WHERE me.event_type = 'error'
        ORDER BY me.ts DESC LIMIT 50
    """).fetchall()
    result["error_details"] = [dict(r) for r in errors]

    # Reply time distribution (hours)
    reply_times = conn.execute("""
        SELECT ROUND((julianday(replied_at) - julianday(message_sent_at)) * 24, 1) as hours
        FROM leads
        WHERE replied_at IS NOT NULL AND message_sent_at IS NOT NULL
        ORDER BY hours
    """).fetchall()
    result["reply_times"] = [r[0] for r in reply_times if r[0] is not None]

    conn.close()
    return result


def get_lead_by_phone(phone: str) -> dict | None:
    conn = get_conn()
    digits = "".join(c for c in phone if c.isdigit())
    row = conn.execute("""
        SELECT * FROM leads WHERE message_sent=1
          AND (contact_phone LIKE ? OR contact_phone LIKE ? OR contact_phone = ?)
        ORDER BY message_sent_at DESC LIMIT 1
    """, (f"%{digits}", f"%{digits[-10:]}", digits)).fetchone()
    conn.close()
    return dict(row) if row else None


def log_token_usage(model: str, provider: str, operation: str, lead_id: int,
                    input_tokens: int, output_tokens: int, cost_usd: float):
    conn = get_conn()
    conn.execute("""
        INSERT INTO token_usage (ts, model, provider, operation, lead_id, input_tokens, output_tokens, cost_usd)
        VALUES (?,?,?,?,?,?,?,?)
    """, (datetime.now().isoformat(), model, provider, operation, lead_id, input_tokens, output_tokens, cost_usd))
    conn.commit()
    conn.close()


def get_token_usage(days: int = 30) -> list:
    conn = get_conn()
    rows = conn.execute("""
        SELECT date(ts) as day, model, provider,
               SUM(input_tokens) as input_tokens,
               SUM(output_tokens) as output_tokens,
               SUM(cost_usd) as cost_usd,
               COUNT(*) as calls
        FROM token_usage
        WHERE ts >= datetime('now', ?)
        GROUP BY day, model, provider
        ORDER BY day DESC
    """, (f"-{days} days",)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_token_usage_total() -> dict:
    conn = get_conn()
    row = conn.execute("""
        SELECT SUM(input_tokens) as input_tokens,
               SUM(output_tokens) as output_tokens,
               SUM(cost_usd) as cost_usd,
               COUNT(*) as calls
        FROM token_usage
    """).fetchone()
    conn.close()
    return dict(row) if row else {}


def get_setting(key: str, default=None):
    conn = get_conn()
    row = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    conn.close()
    return row["value"] if row else default


def set_setting(key: str, value: str):
    conn = get_conn()
    conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?,?)", (key, value))
    conn.commit()
    conn.close()
