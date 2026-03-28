"""
Wazzup webhook server.
Receives message status updates and incoming replies from Wazzup.

Run: python webhook_server.py
Runs on port 8502 alongside Streamlit (port 8501).

For public access (required for Wazzup webhooks):
  ngrok http 8502
  Then set webhook URL in Wazzup settings to: https://xxxx.ngrok.io/webhook
"""
import json
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
from database import init_db, record_message_event, get_lead_by_phone

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("webhook")

app = FastAPI(title="LeadFlow Webhook")
init_db()

# Wazzup message status codes → our event types
STATUS_MAP = {
    "sent": None,          # already recorded when we sent
    "delivered": "delivered",
    "read": "read",
    "failed": "error",
    "undelivered": "error",
}


@app.get("/")
def health():
    return {"status": "ok", "service": "LeadFlow Webhook"}


@app.post("/webhook")
async def wazzup_webhook(request: Request):
    """Main webhook endpoint for Wazzup."""
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    # Wazzup sends {test: true} on setup — respond 200
    if body.get("test"):
        log.info("Wazzup test ping received ✓")
        return JSONResponse({"ok": True})

    log.info(f"Webhook received: {json.dumps(body, ensure_ascii=False)[:200]}")

    # ── Incoming messages (replies) ───────────────────────────────────────────
    for msg in body.get("messages", []):
        if msg.get("isEcho"):
            continue  # our own outgoing message, skip

        chat_id = msg.get("chatId", "")
        text = (msg.get("text") or "").strip()
        msg_type = msg.get("type", "")

        if not chat_id:
            continue

        # Find the lead by phone number
        lead = get_lead_by_phone(chat_id)
        if not lead:
            log.info(f"No lead found for phone {chat_id}")
            continue

        log.info(f"Reply from {chat_id} (lead #{lead['id']}): {text[:80]}")
        record_message_event(
            lead_id=lead["id"],
            wazzup_message_id=lead.get("wazzup_message_id", ""),
            event_type="replied",
            event_data={"text": text, "msg_type": msg_type, "wazzup_msg_id": msg.get("messageId")}
        )

    # ── Message status updates ────────────────────────────────────────────────
    for update in body.get("messageStatuses", []):
        wazzup_msg_id = update.get("messageId", "")
        status = update.get("status", "")
        error_text = update.get("error", "")

        event_type = STATUS_MAP.get(status)
        if not event_type:
            continue

        log.info(f"Status update: {wazzup_msg_id} → {status}")
        record_message_event(
            lead_id=0,  # will be found by wazzup_message_id in DB
            wazzup_message_id=wazzup_msg_id,
            event_type=event_type,
            event_data={"status": status, "error": error_text}
        )

    return JSONResponse({"ok": True})


if __name__ == "__main__":
    print("=" * 50)
    print("LeadFlow Webhook Server")
    print("Listening on http://localhost:8502/webhook")
    print()
    print("To expose publicly (for Wazzup):")
    print("  brew install ngrok")
    print("  ngrok http 8502")
    print("  Copy HTTPS URL → Wazzup Settings → Webhook URL")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8502, log_level="info")
