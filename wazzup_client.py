import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("WAZZUP_API_KEY")
BASE_URL = "https://api.wazzup24.com/v3"


def _headers():
    return {"Authorization": f"Bearer {API_KEY}"}


def get_channels() -> list:
    resp = requests.get(f"{BASE_URL}/channels", headers=_headers())
    resp.raise_for_status()
    return resp.json()


def get_active_channel_id() -> str:
    """Returns the currently selected channel from settings, env, or first active WA."""
    # 1. From DB settings (user picked in UI)
    try:
        from database import get_setting
        saved = get_setting("wazzup_channel_id")
        if saved:
            return saved
    except Exception:
        pass
    # 2. From env
    channel_id = os.getenv("WAZZUP_CHANNEL_ID")
    if channel_id:
        return channel_id
    # 3. First active WhatsApp
    channels = get_channels()
    for ch in channels:
        if ch.get("transport") == "whatsapp" and ch.get("state") == "active":
            return ch["channelId"]
    raise ValueError("Нет активного канала. Выбери канал в настройках.")


def channel_label(ch: dict) -> str:
    transport_icon = {"whatsapp": "💬", "telegram": "✈️", "instagram": "📸"}.get(ch.get("transport",""), "📱")
    state_icon = "✅" if ch.get("state") == "active" else "⚠️"
    phone = ch.get("plainId") or ch.get("channelId","")[:8]
    return f"{state_icon} {transport_icon} {ch.get('transport','').capitalize()} — {phone}"


def normalize_phone(phone: str) -> str:
    digits = "".join(c for c in phone if c.isdigit())
    if digits.startswith("8") and len(digits) == 11:
        digits = "7" + digits[1:]
    return digits


def send_message(phone: str, text: str, crm_message_id: str = None, channel_id: str = None) -> dict:
    if not channel_id:
        channel_id = get_active_channel_id()
    chat_id = normalize_phone(phone)

    payload = {
        "channelId": channel_id,
        "chatId": chat_id,
        "chatType": "whatsapp",
        "text": text,
    }
    if crm_message_id:
        payload["crmMessageId"] = crm_message_id

    resp = requests.post(f"{BASE_URL}/message", headers=_headers(), json=payload)
    resp.raise_for_status()
    return resp.json()


def send_bulk(leads: list, dry_run: bool = False) -> list:
    """
    leads: list of dicts with {id, contact_phone, ai_message}
    Returns list of results.
    """
    results = []
    for lead in leads:
        phone = lead.get("contact_phone", "")
        message = lead.get("ai_message", "")
        lead_id = lead["id"]

        if not phone or not message:
            results.append({"lead_id": lead_id, "status": "skipped", "reason": "no phone or message"})
            continue

        if dry_run:
            results.append({"lead_id": lead_id, "status": "dry_run", "phone": phone})
            continue

        try:
            resp = send_message(phone, message, crm_message_id=f"lead_{lead_id}")
            results.append({
                "lead_id": lead_id,
                "status": "sent",
                "message_id": resp.get("messageId"),
                "phone": phone
            })
        except Exception as e:
            results.append({"lead_id": lead_id, "status": "error", "error": str(e)})

    return results
