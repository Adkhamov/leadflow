"""Sync leads from AmoCRM into local SQLite database."""
from database import init_db, upsert_lead
from amo_client import get_all_leads, get_pipeline_stages, build_lead_dict, get_contacts_batch, get_notes_batch


def sync_all(progress_callback=None) -> int:
    init_db()

    print("Fetching pipeline stages...")
    stages = get_pipeline_stages()

    print("Fetching all leads...")
    raw_leads = get_all_leads(max_pages=50)
    total = len(raw_leads)
    print(f"Found {total} leads")

    # Batch-fetch contacts
    print("Fetching contacts in batches...")
    contact_ids = []
    for lead in raw_leads:
        for c in lead.get("_embedded", {}).get("contacts", []):
            contact_ids.append(c["id"])
    contact_ids = list(set(contact_ids))
    contacts_cache = get_contacts_batch(contact_ids)
    print(f"Loaded {len(contacts_cache)} contacts")

    # Batch-fetch notes
    print("Fetching notes in batches...")
    lead_ids = [l["id"] for l in raw_leads]
    notes_cache = get_notes_batch(lead_ids)
    print(f"Loaded notes for {sum(1 for v in notes_cache.values() if v)} leads")

    # Save to DB
    for i, raw in enumerate(raw_leads):
        lead = build_lead_dict(raw, stages, contacts_cache=contacts_cache, notes_cache=notes_cache)
        # Compute last_activity_at = max of (closed_at, last note created_at)
        notes = notes_cache.get(raw["id"], [])
        note_ts = max((n.get("created_at", 0) for n in notes), default=0)
        lead["last_activity_at"] = max(
            raw.get("closed_at") or 0,
            raw.get("updated_at") or 0,
            note_ts
        ) or None
        upsert_lead(lead)
        if progress_callback:
            progress_callback(i + 1, total)
        elif (i + 1) % 100 == 0:
            print(f"  Saved {i+1}/{total}")

    print(f"Sync complete: {total} leads")
    return total


if __name__ == "__main__":
    sync_all()
