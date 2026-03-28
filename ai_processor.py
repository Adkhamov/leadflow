import os
import json
import anthropic
from openai import OpenAI
from dotenv import load_dotenv
from database import log_token_usage

load_dotenv()

# ─── Model catalog ───────────────────────────────────────────────────────────
MODELS = {
    "claude-opus-4-6": {
        "label": "Claude Opus 4.6",
        "provider": "anthropic",
        "input_price": 15.0,
        "output_price": 75.0,
        "desc": "Самый мощный. Лучший анализ и нюансы.",
        "best_for": "Сложные лиды, VIP, Enterprise"
    },
    "claude-sonnet-4-6": {
        "label": "Claude Sonnet 4.6",
        "provider": "anthropic",
        "input_price": 3.0,
        "output_price": 15.0,
        "desc": "Баланс качества и цены. Рекомендуется.",
        "best_for": "Массовая обработка, основной режим"
    },
    "claude-haiku-4-5": {
        "label": "Claude Haiku 4.5",
        "provider": "anthropic",
        "input_price": 0.25,
        "output_price": 1.25,
        "desc": "Самый быстрый и дешёвый.",
        "best_for": "Огромные базы, черновики"
    },
    "gpt-4o": {
        "label": "GPT-4o",
        "provider": "openai",
        "input_price": 2.5,
        "output_price": 10.0,
        "desc": "Флагман OpenAI.",
        "best_for": "Альтернатива Sonnet"
    },
    "gpt-4o-mini": {
        "label": "GPT-4o Mini",
        "provider": "openai",
        "input_price": 0.15,
        "output_price": 0.60,
        "desc": "Самый дешёвый вариант.",
        "best_for": "Тест на большой базе"
    },
    "gpt-4-turbo": {
        "label": "GPT-4 Turbo",
        "provider": "openai",
        "input_price": 10.0,
        "output_price": 30.0,
        "desc": "Большой контекст.",
        "best_for": "Лиды с длинной историей"
    },
}

DEFAULT_MODEL = "claude-sonnet-4-6"

DROP_REASON_LABELS = {
    "price": "Цена/бюджет",
    "timing": "Не сейчас/время",
    "competitor": "Ушёл к конкуренту",
    "no_need": "Не нужно",
    "no_response": "Не отвечал",
    "unclear": "Непонятно"
}

DROP_STAGE_LABELS = {
    "early": "Ранняя (не разобрался)",
    "mid": "Средняя (думал, но не решил)",
    "late": "Поздняя (был близко к оплате)"
}

RETURN_POTENTIAL_LABELS = {
    "high": "Высокий",
    "medium": "Средний",
    "low": "Низкий"
}

APPROACH_LABELS = {
    "timing_check": "Проверить актуальность",
    "new_offer": "Новый оффер / обновление",
    "discount": "Специальное предложение",
    "value_reminder": "Напомнить о ценности",
    "competitor_compare": "Выгода vs конкурент",
    "case_story": "Поделиться кейсом"
}


def calc_cost(model_id: str, input_tokens: int, output_tokens: int) -> float:
    m = MODELS.get(model_id, {})
    return (input_tokens * m.get("input_price", 0) + output_tokens * m.get("output_price", 0)) / 1_000_000


# ─── Lead summary ─────────────────────────────────────────────────────────────
def _lead_summary(lead: dict) -> str:
    from datetime import datetime
    created = datetime.fromtimestamp(lead["created_at"]).strftime("%d.%m.%Y") if lead.get("created_at") else "неизвестно"
    closed = datetime.fromtimestamp(lead["closed_at"]).strftime("%d.%m.%Y") if lead.get("closed_at") else "открыт"
    last_act = datetime.fromtimestamp(lead["last_activity_at"]).strftime("%d.%m.%Y") if lead.get("last_activity_at") else "неизвестно"
    return f"""Лид: {lead.get('name','Без имени')}
Контакт: {lead.get('contact_name','')} | Тел: {lead.get('contact_phone','')}
Воронка: {lead.get('pipeline_name','')} → Этап слива: {lead.get('stage_name','')}
Создан: {created} | Закрыт: {closed} | Последняя активность: {last_act}
Сумма сделки: {lead.get('price',0)} тенге
Теги: {lead.get('tags','')}
История / примечания:
{lead.get('notes','Нет примечаний')}"""


# ─── Prompts ─────────────────────────────────────────────────────────────────
SEGMENT_PROMPT = """Ты эксперт по реактивации лидов. Проанализируй лид по 7 критериям и верни JSON.

КРИТЕРИИ:
1. segment: "hot" | "warm" | "cold" — общая теплота
2. score: 0-100 — вероятность вернуть в диалог
3. reason: 1-2 предложения почему такой сегмент
4. drop_reason_category: одно из — "price" | "timing" | "competitor" | "no_need" | "no_response" | "unclear"
5. drop_stage_type: "early" (первые 1-2 этапа) | "mid" (середина воронки) | "late" (был близко к оплате)
6. return_potential: "high" | "medium" | "low" — потенциал возврата с учётом всего
7. engagement_level: "high" | "medium" | "low" — насколько активно общался
8. best_approach_type: "timing_check" | "new_offer" | "discount" | "value_reminder" | "competitor_compare" | "case_story"
9. best_channel: "whatsapp" | "call" | "email"
10. best_approach: 1-2 предложения — конкретно что написать/предложить

Верни ТОЛЬКО JSON без markdown.

Данные лида:
{lead_summary}"""

MESSAGE_PROMPT = """Ты опытный менеджер по продажам. Напиши WhatsApp сообщение для возврата лида.

Правила:
- 3-5 предложений
- Дружелюбный, персональный тон, не навязчивый
- Обращайся по имени если есть
- Учти причину ухода и этап
- Конкретный вопрос или предложение в конце
- Без шаблонных фраз
- Язык: русский

Лид: {lead_summary}
Сегмент: {segment} | Причина ухода: {drop_reason_category} | Подход: {best_approach}

ТОЛЬКО текст сообщения, без кавычек."""

HYPOTHESIS_PROMPT = """Ты стратег по продажам. На основе анализа лидов из воронки "{pipeline}" создай 3-5 гипотез для кампаний реактивации.

Данные по лидам (сгруппированы):
{groups_summary}

Для каждой гипотезы верни JSON объект с полями:
- id: "A" | "B" | "C" | "D" | "E"
- name: короткое название сегмента (3-5 слов)
- description: 2-3 предложения — кто эти люди и почему именно они
- criteria: список из 3-4 ключевых признаков этого сегмента
- lead_ids: список ID лидов в этом сегменте (только из предоставленных)
- lead_count: количество лидов
- estimated_response_rate: реалистичный % вероятности ответа (5-60)
- priority: 1 (срочно) до 5 (низкий приоритет)
- approach: конкретная стратегия — что писать, как зацепить
- sample_message: пример сообщения для этого сегмента (2-3 предложения, WhatsApp стиль, коротко)

Верни JSON массив: [{{"id":"A",...}}, {{"id":"B",...}}]
ТОЛЬКО JSON без markdown."""


# ─── API callers ─────────────────────────────────────────────────────────────
def _call_anthropic(model_id: str, prompt: str, max_tokens: int = 800) -> tuple:
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    resp = client.messages.create(
        model=model_id, max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}]
    )
    return resp.content[0].text.strip(), resp.usage.input_tokens, resp.usage.output_tokens


def _call_openai(model_id: str, prompt: str, max_tokens: int = 800) -> tuple:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    resp = client.chat.completions.create(
        model=model_id, max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}]
    )
    return resp.choices[0].message.content.strip(), resp.usage.prompt_tokens, resp.usage.completion_tokens


def _call_model(model_id: str, prompt: str, max_tokens: int = 800) -> tuple:
    provider = MODELS.get(model_id, {}).get("provider", "anthropic")
    if provider == "openai":
        return _call_openai(model_id, prompt, max_tokens)
    return _call_anthropic(model_id, prompt, max_tokens)


def _parse_json(text: str) -> dict | list:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Model truncated the response — try to recover partial array
        # Find the last complete object in the array
        if text.startswith("["):
            last_close = text.rfind("},")
            if last_close == -1:
                last_close = text.rfind("}")
            if last_close != -1:
                truncated = text[:last_close + 1] + "]"
                return json.loads(truncated)
        raise


# ─── Main processors ─────────────────────────────────────────────────────────
def analyze_lead(lead: dict, model_id: str = DEFAULT_MODEL) -> dict:
    summary = _lead_summary(lead)
    prompt = SEGMENT_PROMPT.format(lead_summary=summary)
    text, inp, out = _call_model(model_id, prompt, max_tokens=600)
    cost = calc_cost(model_id, inp, out)
    log_token_usage(model_id, MODELS[model_id]["provider"], "segment", lead["id"], inp, out, cost)
    return _parse_json(text)


def generate_message(lead: dict, analysis: dict, model_id: str = DEFAULT_MODEL) -> str:
    summary = _lead_summary(lead)
    prompt = MESSAGE_PROMPT.format(
        lead_summary=summary,
        segment=analysis.get("segment", ""),
        drop_reason_category=DROP_REASON_LABELS.get(analysis.get("drop_reason_category",""), ""),
        best_approach=analysis.get("best_approach", "")
    )
    text, inp, out = _call_model(model_id, prompt, max_tokens=300)
    cost = calc_cost(model_id, inp, out)
    log_token_usage(model_id, MODELS[model_id]["provider"], "message", lead["id"], inp, out, cost)
    return text


def process_lead(lead: dict, model_id: str = DEFAULT_MODEL) -> dict:
    """Full pipeline: analyze (7 criteria) + generate message."""
    analysis = analyze_lead(lead, model_id)
    msg = generate_message(lead, analysis, model_id)
    return {
        "segment": analysis.get("segment", "cold"),
        "score": int(analysis.get("score", 0)),
        "reason": analysis.get("reason", ""),
        "drop_reason_category": analysis.get("drop_reason_category", "unclear"),
        "drop_stage_type": analysis.get("drop_stage_type", "mid"),
        "return_potential": analysis.get("return_potential", "low"),
        "engagement_level": analysis.get("engagement_level", "low"),
        "best_approach_type": analysis.get("best_approach_type", "timing_check"),
        "best_channel": analysis.get("best_channel", "whatsapp"),
        "message": msg
    }


def generate_hypotheses(leads: list, pipeline_name: str, model_id: str = DEFAULT_MODEL) -> list:
    """
    Takes analyzed leads, groups them and generates campaign hypotheses.
    leads: list of lead dicts with ai_* fields populated
    """
    # Build compact summary for each lead
    lead_summaries = []
    for l in leads:
        if not l.get("ai_segment"):
            continue
        import time
        days_inactive = 0
        if l.get("last_activity_at"):
            days_inactive = int((time.time() - l["last_activity_at"]) / 86400)
        lead_summaries.append({
            "id": l["id"],
            "name": l.get("name", ""),
            "segment": l.get("ai_segment"),
            "score": l.get("ai_score", 0),
            "drop_reason": l.get("drop_reason_category", "unclear"),
            "drop_stage": l.get("drop_stage_type", "mid"),
            "return_potential": l.get("return_potential", "low"),
            "engagement": l.get("engagement_level", "low"),
            "approach": l.get("best_approach_type", "timing_check"),
            "days_inactive": days_inactive,
            "price": l.get("price", 0)
        })

    if not lead_summaries:
        return []

    # Group by key dimensions for the prompt
    groups = {}
    for l in lead_summaries:
        key = (l["segment"], l["drop_reason"], l["drop_stage"])
        if key not in groups:
            groups[key] = {"leads": [], "count": 0}
        groups[key]["leads"].append(l)
        groups[key]["count"] += 1

    # Build concise groups summary
    groups_lines = []
    all_leads_compact = []
    for (seg, reason, stage), g in sorted(groups.items(), key=lambda x: -x[1]["count"]):
        avg_score = sum(l["score"] for l in g["leads"]) / len(g["leads"])
        sample_ids = [l["id"] for l in g["leads"][:5]]
        groups_lines.append(
            f"• {seg.upper()} | причина: {reason} | этап: {stage} | "
            f"{g['count']} лидов | avg score: {avg_score:.0f} | IDs примеры: {sample_ids}"
        )
        all_leads_compact.extend([{"id": l["id"], "seg": seg, "reason": reason,
                                    "stage": stage, "score": l["score"],
                                    "days_inactive": l["days_inactive"]} for l in g["leads"]])

    groups_summary = "\n".join(groups_lines)
    groups_summary += f"\n\nПолный список лидов (для lead_ids):\n{json.dumps(all_leads_compact[:200], ensure_ascii=False)}"

    prompt = HYPOTHESIS_PROMPT.format(pipeline=pipeline_name, groups_summary=groups_summary)
    text, inp, out = _call_model(model_id, prompt, max_tokens=4000)
    cost = calc_cost(model_id, inp, out)
    log_token_usage(model_id, MODELS[model_id]["provider"], "hypotheses", 0, inp, out, cost)

    result = _parse_json(text)
    return result if isinstance(result, list) else result.get("hypotheses", [])


def estimate_cost(n_leads: int, model_id: str = DEFAULT_MODEL) -> dict:
    avg_input = 700
    avg_output = 450
    total_input = n_leads * avg_input
    total_output = n_leads * avg_output
    cost = calc_cost(model_id, total_input, total_output)
    return {
        "n_leads": n_leads,
        "model": MODELS[model_id]["label"],
        "estimated_input_tokens": total_input,
        "estimated_output_tokens": total_output,
        "estimated_cost_usd": round(cost, 4),
        "estimated_cost_kzt": round(cost * 500, 0)
    }
