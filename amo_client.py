import os
import json
import requests
from dotenv import load_dotenv
from database import set_setting, get_setting

load_dotenv()

SUBDOMAIN = os.getenv("AMO_SUBDOMAIN", "moonai")
BASE_URL = f"https://{SUBDOMAIN}.amocrm.ru"
TOKEN_URL = f"{BASE_URL}/oauth2/access_token"


def _get_token() -> str:
    token = get_setting("amo_access_token") or os.getenv("AMO_ACCESS_TOKEN")
    if not token:
        raise ValueError("AmoCRM access token not found. Run auth first.")
    return token


def _headers() -> dict:
    return {"Authorization": f"Bearer {_get_token()}"}


def authorize_with_code(client_id: str, client_secret: str, auth_code: str) -> dict:
    """Exchange auth code for tokens (one-time setup)."""
    resp = requests.post(TOKEN_URL, json={
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": "https://example.com"
    })
    resp.raise_for_status()
    data = resp.json()
    set_setting("amo_access_token", data["access_token"])
    set_setting("amo_refresh_token", data["refresh_token"])
    return data


def refresh_token() -> str:
    client_id = os.getenv("AMO_CLIENT_ID")
    client_secret = os.getenv("AMO_CLIENT_SECRET")
    refresh = get_setting("amo_refresh_token") or os.getenv("AMO_REFRESH_TOKEN")
    resp = requests.post(TOKEN_URL, json={
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "refresh_token",
        "refresh_token": refresh,
        "redirect_uri": "https://example.com"
    })
    resp.raise_for_status()
    data = resp.json()
    set_setting("amo_access_token", data["access_token"])
    set_setting("amo_refresh_token", data["refresh_token"])
    return data["access_token"]


def _get(path: str, params: dict = None) -> dict:
    resp = requests.get(f"{BASE_URL}{path}", headers=_headers(), params=params)
    if resp.status_code == 401:
        refresh_token()
        resp = requests.get(f"{BASE_URL}{path}", headers=_headers(), params=params)
    resp.raise_for_status()
    return resp.json()


def get_pipelines() -> list:
    data = _get("/api/v4/leads/pipelines")
    return data.get("_embedded", {}).get("pipelines", [])


def get_pipeline_stages() -> dict:
    """Returns {stage_id: {name, pipeline_name}}"""
    stages = {}
    pipelines = get_pipelines()
    for pipeline in pipelines:
        for stage in pipeline.get("_embedded", {}).get("statuses", []):
            stages[stage["id"]] = {
                "name": stage["name"],
                "pipeline_name": pipeline["name"],
                "pipeline_id": pipeline["id"]
            }
    return stages


def get_leads_page(page: int = 1, limit: int = 250, with_contacts: bool = True) -> list:
    params = {
        "page": page,
        "limit": limit,
    }
    if with_contacts:
        params["with"] = "contacts"
    try:
        data = _get("/api/v4/leads", params=params)
        return data.get("_embedded", {}).get("leads", [])
    except requests.HTTPError as e:
        if e.response.status_code == 204:
            return []
        raise


def get_all_leads(max_pages: int = 50) -> list:
    all_leads = []
    for page in range(1, max_pages + 1):
        batch = get_leads_page(page=page)
        if not batch:
            break
        all_leads.extend(batch)
        if len(batch) < 250:
            break
    return all_leads


def get_contacts_batch(contact_ids: list) -> dict:
    """Fetch contacts in batches of 250. Returns {contact_id: contact_dict}."""
    result = {}
    for i in range(0, len(contact_ids), 250):
        chunk = contact_ids[i:i+250]
        # Build filter params: filter[id][]=1&filter[id][]=2...
        params = [("with", "custom_fields")]
        for cid in chunk:
            params.append(("filter[id][]", cid))
        try:
            resp = requests.get(f"{BASE_URL}/api/v4/contacts", headers=_headers(), params=params)
            if resp.status_code == 401:
                refresh_token()
                resp = requests.get(f"{BASE_URL}/api/v4/contacts", headers=_headers(), params=params)
            if resp.status_code == 204:
                continue
            resp.raise_for_status()
            data = resp.json()
            for c in data.get("_embedded", {}).get("contacts", []):
                result[c["id"]] = c
        except Exception:
            pass
    return result


def get_notes_batch(lead_ids: list) -> dict:
    """Fetch notes for multiple leads. Returns {lead_id: [notes]}."""
    result = {lid: [] for lid in lead_ids}
    for i in range(0, len(lead_ids), 50):
        chunk = lead_ids[i:i+50]
        params = [("limit", 250)]
        for lid in chunk:
            params.append(("filter[entity_id][]", lid))
        params.append(("filter[entity_type]", "leads"))
        try:
            resp = requests.get(f"{BASE_URL}/api/v4/leads/notes", headers=_headers(), params=params)
            if resp.status_code in (204, 404):
                continue
            resp.raise_for_status()
            data = resp.json()
            for note in data.get("_embedded", {}).get("notes", []):
                entity_id = note.get("entity_id")
                if entity_id in result:
                    result[entity_id].append(note)
        except Exception:
            pass
    return result


def extract_contact_info(contact: dict) -> tuple:
    """Returns (name, phone, email)"""
    name = contact.get("name", "")
    phone, email = "", ""
    for field in contact.get("custom_fields_values") or []:
        if field.get("field_code") == "PHONE":
            vals = field.get("values", [])
            if vals:
                phone = vals[0].get("value", "")
        if field.get("field_code") == "EMAIL":
            vals = field.get("values", [])
            if vals:
                email = vals[0].get("value", "")
    return name, phone, email


def build_lead_dict(raw_lead: dict, stages: dict, contacts_cache: dict = None, notes_cache: dict = None) -> dict:
    """Transform raw AMO lead into our DB format."""
    stage_info = stages.get(raw_lead.get("status_id"), {})

    # Contacts from cache
    contact_name, contact_phone, contact_email = "", "", ""
    contacts = raw_lead.get("_embedded", {}).get("contacts", [])
    if contacts:
        contact_id = contacts[0]["id"]
        contact_data = (contacts_cache or {}).get(contact_id, {})
        contact_name, contact_phone, contact_email = extract_contact_info(contact_data)

    # Tags
    tags = ", ".join([t["name"] for t in (raw_lead.get("_embedded", {}).get("tags") or [])])

    # Notes from cache
    notes_raw = (notes_cache or {}).get(raw_lead["id"], [])
    note_texts = []
    for note in notes_raw:
        p = note.get("params", {})
        text = p.get("text") or p.get("note_type_text", "")
        if text:
            note_texts.append(text)
    notes = "\n---\n".join(note_texts[:20])

    return {
        "id": raw_lead["id"],
        "name": raw_lead.get("name", ""),
        "pipeline_id": stage_info.get("pipeline_id"),
        "pipeline_name": stage_info.get("pipeline_name", ""),
        "stage_id": raw_lead.get("status_id"),
        "stage_name": stage_info.get("name", ""),
        "status_id": raw_lead.get("status_id"),
        "created_at": raw_lead.get("created_at"),
        "closed_at": raw_lead.get("closed_at"),
        "price": raw_lead.get("price", 0),
        "responsible_name": (raw_lead.get("_embedded") or {}).get("responsible_user", {}).get("name", ""),
        "tags": tags,
        "notes": notes,
        "contact_name": contact_name,
        "contact_phone": contact_phone,
        "contact_email": contact_email,
        "raw_json": json.dumps(raw_lead, ensure_ascii=False)
    }
