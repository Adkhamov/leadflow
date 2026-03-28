import streamlit as st
import pandas as pd
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from database import (init_db, get_leads, save_ai_result, save_ai_result_full,
                      mark_message_sent, set_setting, get_setting,
                      get_token_usage, get_token_usage_total,
                      save_hypotheses, get_hypotheses, get_leads_inactive)
from ai_processor import (MODELS, DEFAULT_MODEL, estimate_cost,
                          DROP_REASON_LABELS, DROP_STAGE_LABELS,
                          RETURN_POTENTIAL_LABELS, APPROACH_LABELS)

st.set_page_config(page_title="LeadFlow", page_icon="🚀", layout="wide", initial_sidebar_state="expanded")
init_db()

from styles import inject, badge, SEGMENT_BADGE
inject()

# ─── Sidebar ─────────────────────────────────────────────────────────────────
st.sidebar.markdown("""
<div style="padding:0.5rem 0 1rem 0">
  <div style="font-size:1.15rem;font-weight:700;color:#111827;">🚀 LeadFlow</div>
  <div style="font-size:0.75rem;color:#6B7280;margin-top:2px;">AI реактивация лидов</div>
</div>
""", unsafe_allow_html=True)

page = st.sidebar.radio("Навигация", [
    "📊 Дашборд",
    "🔄 Синхронизация",
    "🤖 AI Анализ",
    "💡 Гипотезы кампаний",
    "📤 Рассылка",
    "📈 Аналитика",
    "🪙 Токены и расходы",
    "🔑 Настройки",
], label_visibility="collapsed")

current_model = get_setting("selected_model", DEFAULT_MODEL)
model_info = MODELS.get(current_model, {})

total = get_token_usage_total()
st.sidebar.divider()
st.sidebar.markdown(f"""
<div style="font-size:0.78rem;color:#6B7280;line-height:1.8">
  <div>🤖 <b>{model_info.get('label', current_model)}</b></div>
  <div style="color:#9CA3AF">${model_info.get('input_price',0):.2f} / ${model_info.get('output_price',0):.2f} за 1M</div>
  {"<div style='margin-top:6px;color:#7C3AED;font-weight:600'>💸 " + f"${total['cost_usd']:.4f} (~{total['cost_usd']*500:.0f} ₸)" + "</div>" if total.get("cost_usd") else ""}
</div>
""", unsafe_allow_html=True)

# ─── Helpers ─────────────────────────────────────────────────────────────────
SEGMENT_EMOJI = {"hot": "🔥", "warm": "🌤️", "cold": "🧊", None: "❓"}


def leads_to_df(leads):
    if not leads:
        return pd.DataFrame()
    df = pd.DataFrame(leads)
    if "created_at" in df.columns:
        df["created_dt"] = pd.to_datetime(df["created_at"], unit="s", errors="coerce")
    return df


# ═══════════════════════════════════════════════════════════════════════════════
if page == "📊 Дашборд":
    st.markdown('<div class="lf-page-title">Дашборд лидов</div><div class="lf-page-subtitle">Обзор базы и статус рассылок</div>', unsafe_allow_html=True)

    all_leads = get_leads()
    df = leads_to_df(all_leads)

    if df.empty:
        st.info("Нет данных. Перейди в **Синхронизация** чтобы загрузить лиды.")
        st.stop()

    # KPI карточки
    n_total   = len(df)
    n_hot     = len(df[df.ai_segment == "hot"])  if "ai_segment"    in df else 0
    n_warm    = len(df[df.ai_segment == "warm"]) if "ai_segment"    in df else 0
    n_cold    = len(df[df.ai_segment == "cold"]) if "ai_segment"    in df else 0
    n_sent    = len(df[df.message_sent == 1])    if "message_sent"  in df else 0
    n_replied = len([l for l in all_leads if l.get("replied_at")])

    st.markdown(f"""
    <div style="display:grid;grid-template-columns:repeat(6,1fr);gap:12px;margin-bottom:1.5rem">
      <div class="lf-card" style="text-align:center;padding:1rem">
        <div style="font-size:1.8rem;font-weight:700;color:#111827">{n_total:,}</div>
        <div style="font-size:0.75rem;color:#6B7280;text-transform:uppercase;margin-top:4px">Всего лидов</div>
      </div>
      <div class="lf-card" style="text-align:center;padding:1rem;border-top:3px solid #EF4444">
        <div style="font-size:1.8rem;font-weight:700;color:#EF4444">{n_hot:,}</div>
        <div style="font-size:0.75rem;color:#6B7280;text-transform:uppercase;margin-top:4px">🔥 Горячих</div>
      </div>
      <div class="lf-card" style="text-align:center;padding:1rem;border-top:3px solid #F59E0B">
        <div style="font-size:1.8rem;font-weight:700;color:#F59E0B">{n_warm:,}</div>
        <div style="font-size:0.75rem;color:#6B7280;text-transform:uppercase;margin-top:4px">🌤 Тёплых</div>
      </div>
      <div class="lf-card" style="text-align:center;padding:1rem;border-top:3px solid #6B7280">
        <div style="font-size:1.8rem;font-weight:700;color:#6B7280">{n_cold:,}</div>
        <div style="font-size:0.75rem;color:#6B7280;text-transform:uppercase;margin-top:4px">🧊 Холодных</div>
      </div>
      <div class="lf-card" style="text-align:center;padding:1rem;border-top:3px solid #7C3AED">
        <div style="font-size:1.8rem;font-weight:700;color:#7C3AED">{n_sent:,}</div>
        <div style="font-size:0.75rem;color:#6B7280;text-transform:uppercase;margin-top:4px">📤 Отправлено</div>
      </div>
      <div class="lf-card" style="text-align:center;padding:1rem;border-top:3px solid #10B981">
        <div style="font-size:1.8rem;font-weight:700;color:#10B981">{n_replied:,}</div>
        <div style="font-size:0.75rem;color:#6B7280;text-transform:uppercase;margin-top:4px">💬 Ответили</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Фильтры
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        seg_filter = st.multiselect("Сегмент", ["hot", "warm", "cold"], default=["hot", "warm", "cold"])
    with col_f2:
        sent_filter = st.selectbox("Статус рассылки", ["Все", "Не отправлено", "Отправлено"])
    with col_f3:
        search = st.text_input("🔍 Поиск по имени / телефону")

    filtered = df.copy()
    if seg_filter and "ai_segment" in filtered:
        filtered = filtered[filtered.ai_segment.isin(seg_filter) | filtered.ai_segment.isna()]
    if sent_filter == "Не отправлено":
        filtered = filtered[filtered.message_sent == 0]
    elif sent_filter == "Отправлено":
        filtered = filtered[filtered.message_sent == 1]
    if search:
        mask = (
            filtered.name.str.contains(search, case=False, na=False) |
            filtered.contact_phone.str.contains(search, case=False, na=False) |
            filtered.contact_name.str.contains(search, case=False, na=False)
        )
        filtered = filtered[mask]

    st.markdown(f'<div style="color:#6B7280;font-size:0.85rem;margin:0.5rem 0">Найдено: <b>{len(filtered)}</b> лидов</div>', unsafe_allow_html=True)

    display_cols = ["id", "name", "contact_name", "contact_phone", "stage_name",
                    "ai_segment", "ai_score", "message_sent", "message_status"]
    avail = [c for c in display_cols if c in filtered.columns]
    if not filtered.empty:
        st.dataframe(
            filtered[avail].rename(columns={
                "id": "ID", "name": "Лид", "contact_name": "Контакт",
                "contact_phone": "Телефон", "stage_name": "Этап",
                "ai_segment": "Сегмент", "ai_score": "Скор",
                "message_sent": "Отправлено", "message_status": "Статус"
            }),
            use_container_width=True, height=420
        )

    # Детали лида
    st.divider()
    lead_ids = filtered["id"].tolist() if not filtered.empty else []
    if lead_ids:
        selected_id = st.selectbox("Выбери лид для детального просмотра", lead_ids,
                                    format_func=lambda x: f"#{x} — {filtered[filtered.id==x].iloc[0]['name']}")
        row = filtered[filtered.id == selected_id].iloc[0]
        seg = row.get("ai_segment")
        seg_color = {"hot":"#EF4444","warm":"#F59E0B","cold":"#6B7280"}.get(seg,"#E5E7EB")
        seg_badge = SEGMENT_BADGE.get(seg, badge("Не проанализирован","gray"))

        st.markdown(f"""
        <div class="lf-card" style="border-top:3px solid {seg_color}">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:1rem">
            <div>
              <div style="font-size:1.1rem;font-weight:600;color:#111827">{row['name']}</div>
              <div style="color:#6B7280;font-size:0.875rem;margin-top:2px">
                {row.get('contact_name','')} · {row.get('contact_phone','')}
              </div>
            </div>
            <div>{seg_badge} &nbsp; <span style="font-size:0.85rem;color:#7C3AED;font-weight:600">{row.get('ai_score','—')}/100</span></div>
          </div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;font-size:0.875rem">
            <div><span style="color:#6B7280">Воронка:</span> {row.get('pipeline_name','—')}</div>
            <div><span style="color:#6B7280">Этап:</span> {row.get('stage_name','—')}</div>
            <div><span style="color:#6B7280">Теги:</span> {row.get('tags','—') or '—'}</div>
            <div><span style="color:#6B7280">Статус:</span> {row.get('message_status','Не отправлено') or 'Не отправлено'}</div>
          </div>
          {"<div style='margin-top:1rem;padding:0.75rem;background:#F5F3FF;border-radius:8px;font-size:0.875rem;color:#374151'><b style='color:#7C3AED'>Причина:</b> " + str(row.get('ai_reason','')) + "</div>" if row.get('ai_reason') else ""}
        </div>
        """, unsafe_allow_html=True)

        if row.get("ai_message"):
            st.markdown(f"""
            <div class="lf-card" style="background:#F0FDF4;border-color:#BBF7D0">
              <div style="font-size:0.75rem;font-weight:600;color:#16A34A;text-transform:uppercase;margin-bottom:6px">💬 Сгенерированное сообщение</div>
              <div style="color:#166534;font-size:0.9rem;line-height:1.6">{row['ai_message']}</div>
            </div>
            """, unsafe_allow_html=True)

        if row.get("notes"):
            with st.expander("📝 Примечания"):
                st.text(row["notes"])


# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🔄 Синхронизация":
    st.title("🔄 Синхронизация с AmoCRM")

    last_sync = get_setting("last_sync")
    if last_sync:
        st.success(f"Последняя синхронизация: {last_sync}")

    leads = get_leads()
    st.metric("Лидов в базе", len(leads))

    st.divider()
    st.subheader("Авторизация AmoCRM")

    with st.expander("Как получить токен AmoCRM", expanded=not get_setting("amo_access_token")):
        st.markdown("""
1. Зайди в AmoCRM → **Настройки → Интеграции → Добавить интеграцию**
2. Создай интеграцию, запиши **Client ID** и **Client Secret**
3. Нажми **Разрешить доступ** — получишь **Authorization Code**
        """)

    col1, col2 = st.columns(2)
    with col1:
        client_id = st.text_input("Client ID", value=os.getenv("AMO_CLIENT_ID", ""))
        client_secret = st.text_input("Client Secret", type="password")
    with col2:
        auth_code = st.text_input("Authorization Code (одноразовый)")

    if st.button("Авторизоваться", type="primary"):
        if not all([client_id, client_secret, auth_code]):
            st.error("Заполни все поля")
        else:
            try:
                from amo_client import authorize_with_code
                data = authorize_with_code(client_id, client_secret, auth_code)
                st.success("✅ Авторизация успешна!")
            except Exception as e:
                st.error(f"Ошибка: {e}")

    st.divider()
    if st.button("🔄 Синхронизировать лиды", type="primary"):
        if not get_setting("amo_access_token") and not os.getenv("AMO_ACCESS_TOKEN"):
            st.error("Сначала авторизуйся")
        else:
            progress = st.progress(0)
            status = st.empty()

            def update_progress(done, total):
                progress.progress(done / total)
                status.text(f"Синхронизировано: {done}/{total}")

            try:
                from sync import sync_all
                count = sync_all(progress_callback=update_progress)
                set_setting("last_sync", datetime.now().strftime("%d.%m.%Y %H:%M"))
                st.success(f"✅ Синхронизировано {count} лидов!")
            except Exception as e:
                st.error(f"Ошибка: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🤖 AI Анализ":
    st.title("🤖 AI Сегментация и генерация сообщений")

    # Model selector
    st.subheader("Выбор модели")
    cols = st.columns(len(MODELS))
    for i, (mid, info) in enumerate(MODELS.items()):
        with cols[i]:
            is_current = mid == current_model
            border = "2px solid #00cc00" if is_current else "1px solid #333"
            provider_icon = "🟣" if info["provider"] == "anthropic" else "🟢"
            st.markdown(f"""
<div style="border:{border};border-radius:8px;padding:10px;margin:2px;min-height:160px">
<b>{provider_icon} {info['label']}</b><br>
<small style="color:#aaa">{info['desc']}</small><br><br>
<small>📥 ${info['input_price']}/1M &nbsp; 📤 ${info['output_price']}/1M</small><br>
<small style="color:#88cc88">✓ {info['best_for']}</small>
</div>""", unsafe_allow_html=True)
            if not is_current:
                if st.button("Выбрать", key=f"sel_{mid}"):
                    set_setting("selected_model", mid)
                    st.rerun()
            else:
                st.success("✅ Активна")

    st.divider()

    # ── Filters ──────────────────────────────────────────────────────────────
    st.subheader("Фильтры выборки")

    all_leads = get_leads()
    all_pipelines = sorted(set(l.get("pipeline_name","") for l in all_leads if l.get("pipeline_name")))

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        selected_pipeline = st.selectbox("Воронка", ["— Все —"] + all_pipelines)
    with col_f2:
        inactive_days = st.slider("Не связывались более (дней)", 0, 365, 30,
                                  help="0 = без ограничения по давности")

    col_f3, col_f4, col_f5 = st.columns(3)
    with col_f3:
        only_with_phone = st.checkbox("Только с телефоном", value=True)
    with col_f4:
        only_unprocessed = st.checkbox("Только непроанализированные", value=True)
    with col_f5:
        max_leads = st.number_input("Максимум лидов", 1, 1000, 50)

    # Apply filters
    import time as _time
    to_process = all_leads
    if selected_pipeline != "— Все —":
        to_process = [l for l in to_process if l.get("pipeline_name") == selected_pipeline]
    if inactive_days > 0:
        cutoff = int(_time.time()) - inactive_days * 86400
        to_process = [l for l in to_process
                      if not l.get("last_activity_at") or l["last_activity_at"] < cutoff]
    if only_with_phone:
        to_process = [l for l in to_process if l.get("contact_phone")]
    if only_unprocessed:
        to_process = [l for l in to_process if not l.get("ai_segment")]
    to_process = to_process[:max_leads]

    # Stats
    col_s1, col_s2, col_s3 = st.columns(3)
    col_s1.metric("Подходит под фильтр", len(to_process))
    col_s2.metric("Проанализировано всего", len([l for l in all_leads if l.get("ai_segment")]))
    col_s3.metric("Осталось обработать", len([l for l in all_leads if not l.get("ai_segment")]))

    est = estimate_cost(len(to_process), current_model)
    st.info(
        f"**{len(to_process)} лидов** · модель **{est['model']}** · "
        f"≈ **${est['estimated_cost_usd']}** (~{est['estimated_cost_kzt']:.0f} ₸)"
    )

    if st.button("🤖 Запустить AI анализ (7 критериев)", type="primary", disabled=len(to_process) == 0):
        from ai_processor import process_lead

        progress = st.progress(0)
        status = st.empty()
        errors = []

        for i, lead in enumerate(to_process):
            status.text(f"Анализирую: {lead['name']} ({i+1}/{len(to_process)})")
            try:
                result = process_lead(lead, model_id=current_model)
                save_ai_result_full(lead["id"], result)
            except Exception as e:
                errors.append(f"#{lead['id']}: {e}")
            progress.progress((i + 1) / len(to_process))

        if errors:
            st.warning(f"Ошибки ({len(errors)}): " + "; ".join(errors[:3]))
        st.success(f"✅ Готово! Обработано {len(to_process) - len(errors)} лидов. "
                   f"Теперь перейди в **Гипотезы кампаний** →")
        st.rerun()

    # ── Results preview ───────────────────────────────────────────────────────
    st.divider()
    st.subheader("Результаты анализа")

    analyzed = get_leads({"has_ai": True})
    if selected_pipeline != "— Все —":
        analyzed = [l for l in analyzed if l.get("pipeline_name") == selected_pipeline]

    if not analyzed:
        st.info("Нет проанализированных лидов для выбранной воронки.")
    else:
        # Summary bar
        from collections import Counter
        seg_counts = Counter(l.get("ai_segment") for l in analyzed)
        reason_counts = Counter(l.get("drop_reason_category") for l in analyzed if l.get("drop_reason_category"))
        stage_counts = Counter(l.get("drop_stage_type") for l in analyzed if l.get("drop_stage_type"))

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("**Сегменты**")
            for seg, cnt in seg_counts.most_common():
                st.write(f"{SEGMENT_EMOJI.get(seg,'❓')} {seg}: **{cnt}**")
        with col2:
            st.markdown("**Причины отказа**")
            for reason, cnt in reason_counts.most_common():
                st.write(f"{DROP_REASON_LABELS.get(reason, reason)}: **{cnt}**")
        with col3:
            st.markdown("**Этап слива**")
            for stage, cnt in stage_counts.most_common():
                st.write(f"{DROP_STAGE_LABELS.get(stage, stage)}: **{cnt}**")

        st.divider()
        for lead in analyzed[:15]:
            seg = lead.get("ai_segment", "")
            reason = DROP_REASON_LABELS.get(lead.get("drop_reason_category",""), "—")
            stage = DROP_STAGE_LABELS.get(lead.get("drop_stage_type",""), "—")
            potential = RETURN_POTENTIAL_LABELS.get(lead.get("return_potential",""), "—")
            approach = APPROACH_LABELS.get(lead.get("best_approach_type",""), "—")
            with st.expander(
                f"{SEGMENT_EMOJI.get(seg,'❓')} **{lead['name']}** | "
                f"{lead.get('contact_phone','')} | Скор: {lead.get('ai_score',0)} | {reason}"
            ):
                c1, c2 = st.columns(2)
                with c1:
                    st.write(f"**Причина:** {lead.get('ai_reason','')}")
                    st.write(f"**Отказ:** {reason} | **Этап:** {stage}")
                    st.write(f"**Потенциал возврата:** {potential}")
                with c2:
                    st.write(f"**Вовлечённость:** {lead.get('engagement_level','—')}")
                    st.write(f"**Подход:** {approach}")
                    st.write(f"**Канал:** {lead.get('best_channel','—')}")
                msg = lead.get("ai_message", "")
                new_msg = st.text_area("Сообщение", value=msg, key=f"msg_{lead['id']}")
                if new_msg != msg:
                    if st.button("💾 Сохранить", key=f"save_{lead['id']}"):
                        save_ai_result(lead["id"], lead["ai_segment"], lead["ai_score"],
                                       lead["ai_reason"], new_msg)
                        st.success("Сохранено")
                        st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
elif page == "💡 Гипотезы кампаний":
    st.title("💡 Гипотезы кампаний реактивации")
    st.caption("AI анализирует все сегментированные лиды и предлагает сегменты с оценкой вероятности ответа")

    all_leads = get_leads()
    all_pipelines = sorted(set(l.get("pipeline_name","") for l in all_leads if l.get("pipeline_name")))

    col1, col2 = st.columns([2, 1])
    with col1:
        hyp_pipeline = st.selectbox("Воронка для анализа", all_pipelines, key="hyp_pipeline")
    with col2:
        hyp_model = st.selectbox("Модель", list(MODELS.keys()),
                                  format_func=lambda x: MODELS[x]["label"],
                                  index=list(MODELS.keys()).index(current_model))

    analyzed_for_pipeline = [l for l in all_leads
                              if l.get("pipeline_name") == hyp_pipeline and l.get("ai_segment")]

    col_a, col_b = st.columns(2)
    col_a.metric("Проанализировано лидов в воронке", len(analyzed_for_pipeline))
    col_b.metric("Всего лидов в воронке", len([l for l in all_leads if l.get("pipeline_name") == hyp_pipeline]))

    if len(analyzed_for_pipeline) < 5:
        st.warning(f"Мало проанализированных лидов ({len(analyzed_for_pipeline)}). "
                   f"Сначала запусти AI Анализ для воронки **{hyp_pipeline}**.")
    else:
        est = estimate_cost(1, hyp_model)
        st.info(f"Генерация гипотез: ~1 запрос · ≈$0.05-0.15 (~10-75 ₸)")

        if st.button("💡 Сгенерировать гипотезы", type="primary"):
            from ai_processor import generate_hypotheses
            with st.spinner("Анализирую лиды и формирую гипотезы..."):
                try:
                    hypotheses = generate_hypotheses(analyzed_for_pipeline, hyp_pipeline, hyp_model)
                    save_hypotheses(hypotheses, hyp_pipeline)
                    st.success(f"✅ Сгенерировано {len(hypotheses)} гипотез!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Ошибка: {e}")

    st.divider()

    # Show saved hypotheses
    hypotheses = get_hypotheses(hyp_pipeline)
    if not hypotheses:
        st.info("Гипотезы ещё не сгенерированы. Нажми кнопку выше.")
    else:
        st.subheader(f"Гипотезы для воронки «{hyp_pipeline}»")

        # Summary table
        summary_rows = []
        for h in hypotheses:
            summary_rows.append({
                "Приоритет": "⭐" * (6 - h["priority"]),
                "Сегмент": h["name"],
                "Лидов": h["lead_count"],
                "Вероятность ответа": f"{h['estimated_response_rate']}%",
                "Ожидаемых ответов": f"~{int(h['lead_count'] * h['estimated_response_rate'] / 100)}",
            })
        st.dataframe(pd.DataFrame(summary_rows), use_container_width=True, hide_index=True)

        st.divider()

        # Detail cards
        PRIORITY_COLOR = {1: "#ff4444", 2: "#ff8800", 3: "#ffcc00", 4: "#88cc44", 5: "#aaaaaa"}
        for h in hypotheses:
            color = PRIORITY_COLOR.get(h["priority"], "#aaa")
            response_rate = h["estimated_response_rate"]
            with st.expander(
                f"**[{h['id']}] {h['name']}** — {h['lead_count']} лидов · "
                f"{response_rate}% вероятность ответа · Приоритет {h['priority']}",
                expanded=h["priority"] <= 2
            ):
                st.markdown(f"""
<div style="border-left: 4px solid {color}; padding-left: 12px; margin-bottom: 12px">
<b>Описание:</b> {h['description']}
</div>""", unsafe_allow_html=True)

                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**Признаки сегмента:**")
                    for cr in h.get("criteria", []):
                        st.write(f"• {cr}")
                    st.markdown(f"**Стратегия:** {h['approach']}")
                with c2:
                    st.metric("Лидов в сегменте", h["lead_count"])
                    st.metric("Вероятность ответа", f"{response_rate}%")
                    st.metric("Ожидаемых ответов", f"~{int(h['lead_count'] * response_rate / 100)}")

                st.markdown("**Пример сообщения:**")
                st.info(h["sample_message"])

                # Leads in this segment
                seg_leads = [l for l in all_leads if l.get("hypothesis_id") == h["id"]
                             and l.get("pipeline_name") == hyp_pipeline]
                if seg_leads:
                    with st.expander(f"Показать {len(seg_leads)} лидов сегмента"):
                        seg_df = pd.DataFrame([{
                            "ID": l["id"], "Имя": l["name"],
                            "Телефон": l.get("contact_phone",""),
                            "Скор": l.get("ai_score", 0),
                            "Этап слива": l.get("stage_name",""),
                        } for l in seg_leads])
                        st.dataframe(seg_df, use_container_width=True, hide_index=True)

                    col_send1, col_send2 = st.columns(2)
                    with col_send1:
                        unsent = [l for l in seg_leads if not l.get("message_sent") and l.get("contact_phone") and l.get("ai_message")]
                        st.write(f"Готово к отправке: **{len(unsent)}** лидов")
                    with col_send2:
                        if st.button(f"📤 Отправить сегмент {h['id']}", key=f"send_hyp_{h['id']}"):
                            st.session_state[f"confirm_send_{h['id']}"] = True

                    if st.session_state.get(f"confirm_send_{h['id']}"):
                        st.warning(f"⚠️ Отправить {len(unsent)} сообщений сегменту «{h['name']}»?")
                        if st.button(f"✅ Да, отправить", key=f"confirm_{h['id']}"):
                            from wazzup_client import send_message
                            sent, errs = 0, 0
                            prog = st.progress(0)
                            for i, lead in enumerate(unsent):
                                try:
                                    resp = send_message(lead["contact_phone"], lead["ai_message"],
                                                        crm_message_id=f"lead_{lead['id']}")
                                    mark_message_sent(lead["id"], resp.get("messageId",""))
                                    sent += 1
                                except Exception:
                                    errs += 1
                                prog.progress((i+1)/len(unsent))
                            st.success(f"✅ Отправлено: {sent} | ❌ Ошибок: {errs}")
                            st.session_state[f"confirm_send_{h['id']}"] = False


# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📤 Рассылка":
    st.title("📤 Рассылка через WhatsApp (Wazzup)")

    try:
        from wazzup_client import get_channels, channel_label, get_active_channel_id
        all_channels = get_channels()
        active_id = get_active_channel_id()
        active_ch = next((c for c in all_channels if c["channelId"] == active_id), None)
        if active_ch:
            st.success(f"✅ Активный канал: **{channel_label(active_ch)}**")
        else:
            st.warning("Канал не выбран — зайди в **Настройки** и выбери канал")
    except Exception as e:
        st.error(f"Ошибка Wazzup: {e}")

    st.divider()
    st.subheader("Аудитория")
    col1, col2 = st.columns(2)
    with col1:
        segments = st.multiselect("Сегменты", ["hot", "warm", "cold"], default=["hot", "warm"])
    with col2:
        only_unsent = st.checkbox("Только не отправленным", value=True)

    leads_to_send = get_leads({"has_ai": True, "has_phone": True})
    if segments:
        leads_to_send = [l for l in leads_to_send if l.get("ai_segment") in segments]
    if only_unsent:
        leads_to_send = [l for l in leads_to_send if not l.get("message_sent")]

    st.metric("Лидов для отправки", len(leads_to_send))

    if leads_to_send:
        preview_df = pd.DataFrame([{
            "Имя": l["name"],
            "Телефон": l.get("contact_phone",""),
            "Сегмент": l.get("ai_segment",""),
            "Скор": l.get("ai_score", 0),
            "Сообщение": (l.get("ai_message") or "")[:80] + "..."
        } for l in leads_to_send[:20]])
        st.dataframe(preview_df, use_container_width=True)

        st.divider()
        col_dry, col_send = st.columns(2)
        with col_dry:
            if st.button("🔍 Тестовый прогон"):
                st.success(f"✅ {len(leads_to_send)} лидов готовы к отправке")

        with col_send:
            st.warning("⚠️ Реальная отправка сообщений!")
            confirm = st.checkbox("Подтверждаю отправку")
            if st.button("📤 Отправить", type="primary", disabled=not confirm):
                from wazzup_client import send_message
                progress = st.progress(0)
                sent, errors = 0, 0
                for i, lead in enumerate(leads_to_send):
                    try:
                        resp = send_message(lead["contact_phone"], lead["ai_message"],
                                            crm_message_id=f"lead_{lead['id']}")
                        mark_message_sent(lead["id"], resp.get("messageId", ""))
                        sent += 1
                    except Exception:
                        errors += 1
                    progress.progress((i+1)/len(leads_to_send))
                st.success(f"✅ Отправлено: {sent} | ❌ Ошибок: {errors}")


# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📈 Аналитика":
    st.title("📈 Аналитика рассылок")

    from database import get_message_analytics
    import json as _json

    analytics_days = st.sidebar.slider("Период (дней)", 7, 90, 30, key="analytics_days")
    analytics = get_message_analytics(days=analytics_days)

    # ── Воронка доставки ──────────────────────────────────────────────────────
    st.subheader("Воронка рассылки")

    sent_n      = analytics.get("sent", 0)
    delivered_n = analytics.get("delivered", 0)
    read_n      = analytics.get("read_count", 0)
    replied_n   = analytics.get("replied", 0)
    replied_24h = analytics.get("replied_24h", 0)
    errors_n    = analytics.get("errors", 0)

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("📤 Отправлено", sent_n)
    col2.metric("📬 Доставлено", delivered_n,
                delta=f"{delivered_n/sent_n*100:.0f}%" if sent_n else None)
    col3.metric("👁 Прочитано",  read_n,
                delta=f"{read_n/sent_n*100:.0f}%" if sent_n else None)
    col4.metric("💬 Ответили",   replied_n,
                delta=f"{replied_n/sent_n*100:.0f}%" if sent_n else None)
    col5.metric("⚡ Ответ < 24ч", replied_24h,
                delta=f"{replied_24h/replied_n*100:.0f}%" if replied_n else None)
    col6.metric("❌ Ошибки",     errors_n,
                delta=f"-{errors_n/sent_n*100:.0f}%" if sent_n else None,
                delta_color="inverse")

    # Visual funnel bar
    if sent_n:
        st.divider()
        funnel_data = pd.DataFrame({
            "Этап": ["Отправлено", "Доставлено", "Прочитано", "Ответили", "< 24ч"],
            "Кол-во": [sent_n, delivered_n, read_n, replied_n, replied_24h],
            "% от отправленных": [
                100,
                round(delivered_n/sent_n*100, 1),
                round(read_n/sent_n*100, 1),
                round(replied_n/sent_n*100, 1),
                round(replied_24h/sent_n*100, 1),
            ]
        })
        st.bar_chart(funnel_data.set_index("Этап")["Кол-во"])
        st.dataframe(funnel_data, use_container_width=True, hide_index=True)

    # ── Динамика по дням ──────────────────────────────────────────────────────
    daily = analytics.get("daily", [])
    if daily:
        st.divider()
        st.subheader("Динамика по дням")
        df_daily = pd.DataFrame(daily)
        df_daily = df_daily.rename(columns={
            "day": "Дата", "sent": "Отправлено", "delivered": "Доставлено",
            "read_count": "Прочитано", "replied": "Ответили", "errors": "Ошибки"
        })
        st.line_chart(df_daily.set_index("Дата")[["Отправлено","Доставлено","Прочитано","Ответили"]])
        st.dataframe(df_daily, use_container_width=True, hide_index=True)

    # ── Время ответа ──────────────────────────────────────────────────────────
    reply_times = analytics.get("reply_times", [])
    if reply_times:
        st.divider()
        st.subheader("Распределение времени ответа")
        df_rt = pd.DataFrame({"Часов до ответа": reply_times})
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Медиана", f"{sorted(reply_times)[len(reply_times)//2]:.1f} ч")
        col_b.metric("Быстрее 1ч", len([t for t in reply_times if t <= 1]))
        col_c.metric("Быстрее 24ч", len([t for t in reply_times if t <= 24]))
        st.bar_chart(df_rt["Часов до ответа"].value_counts().sort_index())

    # ── Ошибки ────────────────────────────────────────────────────────────────
    error_details = analytics.get("error_details", [])
    if error_details:
        st.divider()
        st.subheader(f"❌ Ошибки отправки ({len(error_details)})")
        rows = []
        for e in error_details:
            data = {}
            try:
                data = _json.loads(e.get("event_data") or "{}")
            except Exception:
                pass
            rows.append({
                "Время": e.get("ts","")[:19],
                "Лид": e.get("name",""),
                "Телефон": e.get("contact_phone",""),
                "Ошибка": data.get("error") or data.get("status","неизвестно"),
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # ── Ответившие лиды ───────────────────────────────────────────────────────
    st.divider()
    st.subheader("💬 Лиды которые ответили")
    all_leads = get_leads()
    replied_leads = [l for l in all_leads if l.get("replied_at")]
    if replied_leads:
        replied_df = pd.DataFrame([{
            "Лид": l["name"],
            "Телефон": l.get("contact_phone",""),
            "Сегмент": l.get("ai_segment",""),
            "Ответил через": (
                f"{(pd.Timestamp(l['replied_at']) - pd.Timestamp(l['message_sent_at'])).total_seconds()/3600:.1f}ч"
                if l.get("replied_at") and l.get("message_sent_at") else "—"
            ),
            "Текст ответа": (l.get("reply_text") or "")[:80],
        } for l in replied_leads])
        st.dataframe(replied_df, use_container_width=True, hide_index=True)
    else:
        st.info("Ответов пока нет. Они появятся после настройки вебхука.")

    # ── Webhook setup hint ────────────────────────────────────────────────────
    st.divider()
    with st.expander("⚙️ Как настроить получение статусов (вебхук)"):
        st.markdown("""
**Шаг 1.** Запусти webhook-сервер в отдельном терминале:
```bash
cd /Users/ae/Documents/code/leadflow
python webhook_server.py
```

**Шаг 2.** Получи публичный URL через ngrok:
```bash
brew install ngrok   # если не установлен
ngrok http 8502
```
Скопируй HTTPS-ссылку вида `https://xxxx.ngrok.io`

**Шаг 3.** В Wazzup → **Настройки → Webhooks** укажи:
```
https://xxxx.ngrok.io/webhook
```

После этого статусы **доставлено / прочитано / ответили** будут обновляться автоматически.
        """)

    st.divider()
    st.subheader("Общая статистика базы")
    all_leads_df = leads_to_df(all_leads)
    if not all_leads_df.empty and "ai_segment" in all_leads_df:
        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown("**Сегменты**")
            seg_counts = all_leads_df.ai_segment.value_counts().reset_index()
            seg_counts.columns = ["Сегмент", "Кол-во"]
            st.bar_chart(seg_counts.set_index("Сегмент"))
        with col_r:
            st.markdown("**Топ лидов по скору**")
            if "ai_score" in all_leads_df:
                top = all_leads_df.nlargest(10, "ai_score")[["name","ai_segment","ai_score"]]
                st.dataframe(top, use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🪙 Токены и расходы":
    st.title("🪙 Расходы на AI")

    total = get_token_usage_total()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Всего запросов", total.get("calls", 0))
    col2.metric("Вх. токенов", f"{total.get('input_tokens', 0):,}")
    col3.metric("Исх. токенов", f"{total.get('output_tokens', 0):,}")
    col4.metric("Потрачено", f"${total.get('cost_usd', 0):.4f} (~{(total.get('cost_usd',0)*500):.0f} ₸)")

    st.divider()

    # Daily usage
    usage = get_token_usage(days=30)
    if usage:
        df_usage = pd.DataFrame(usage)

        st.subheader("Расходы по дням")
        daily = df_usage.groupby("day")[["cost_usd","input_tokens","output_tokens","calls"]].sum().reset_index()
        daily["cost_kzt"] = (daily["cost_usd"] * 500).round(0)
        st.line_chart(daily.set_index("day")[["cost_usd"]])

        st.subheader("Детализация по дням и моделям")
        df_show = df_usage.copy()
        df_show["cost_kzt"] = (df_show["cost_usd"] * 500).round(0)
        df_show["input_tokens"] = df_show["input_tokens"].apply(lambda x: f"{x:,}")
        df_show["output_tokens"] = df_show["output_tokens"].apply(lambda x: f"{x:,}")
        st.dataframe(
            df_show.rename(columns={
                "day":"Дата","model":"Модель","provider":"Провайдер",
                "input_tokens":"Вх. токены","output_tokens":"Исх. токены",
                "cost_usd":"$ USD","cost_kzt":"₸ KZT","calls":"Запросов"
            }),
            use_container_width=True
        )

        # By model
        st.subheader("По моделям (всего)")
        by_model = df_usage.groupby("model")[["cost_usd","calls"]].sum().reset_index()
        by_model["cost_kzt"] = (by_model["cost_usd"] * 500).round(0)
        st.dataframe(by_model.rename(columns={"model":"Модель","cost_usd":"$ USD",
                                               "cost_kzt":"₸ KZT","calls":"Запросов"}),
                     use_container_width=True)
    else:
        st.info("Данных пока нет. Запусти AI анализ — расходы появятся здесь.")

    st.divider()
    st.subheader("Сравнение моделей")
    rows = []
    n_test = st.number_input("Лидов для оценки", min_value=1, max_value=10000, value=100)
    for mid, info in MODELS.items():
        est = estimate_cost(n_test, mid)
        rows.append({
            "Провайдер": "🟣 Anthropic" if info["provider"] == "anthropic" else "🟢 OpenAI",
            "Модель": info["label"],
            "Качество": info["desc"],
            "Лучше для": info["best_for"],
            f"Цена за {n_test} лидов ($)": est["estimated_cost_usd"],
            f"Цена за {n_test} лидов (₸)": est["estimated_cost_kzt"],
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🔑 Настройки":
    st.title("🔑 Настройки")

    st.subheader("API ключи")
    col1, col2 = st.columns(2)
    with col1:
        anthropic_key = st.text_input("Anthropic API Key", type="password",
                                       value=os.getenv("ANTHROPIC_API_KEY",""))
        if st.button("Сохранить Anthropic"):
            set_setting("anthropic_api_key", anthropic_key)
            st.success("Сохранено")
    with col2:
        openai_key = st.text_input("OpenAI API Key", type="password",
                                    value=os.getenv("OPENAI_API_KEY",""))
        if st.button("Сохранить OpenAI"):
            set_setting("openai_api_key", openai_key)
            st.success("Сохранено")

    st.divider()
    st.subheader("Статус подключений")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**AmoCRM**")
        token = get_setting("amo_access_token") or os.getenv("AMO_ACCESS_TOKEN")
        if token:
            try:
                from amo_client import _get
                acc = _get("/api/v4/account")
                st.success(f"✅ {acc.get('name','OK')}")
            except Exception as e:
                st.error(f"❌ {e}")
        else:
            st.error("❌ Нет токена")

    with col2:
        st.markdown("**Wazzup**")
        if os.getenv("WAZZUP_API_KEY"):
            try:
                from wazzup_client import get_channels
                chs = get_channels()
                st.success(f"✅ {len(chs)} каналов доступно")
            except Exception as e:
                st.error(f"❌ {e}")
        else:
            st.error("❌ Нет ключа")

    with col3:
        st.markdown("**Claude AI**")
        key = get_setting("anthropic_api_key") or os.getenv("ANTHROPIC_API_KEY")
        if key:
            st.success("✅ Ключ есть")
        else:
            st.error("❌ Нет ключа")

    st.divider()
    st.subheader("📱 Выбор канала Wazzup")

    try:
        from wazzup_client import get_channels, channel_label
        all_channels = get_channels()
        if not all_channels:
            st.warning("Каналы не найдены. Проверь API ключ Wazzup.")
        else:
            saved_channel_id = get_setting("wazzup_channel_id") or os.getenv("WAZZUP_CHANNEL_ID", "")

            # Build options dict: label -> channelId
            ch_options = {channel_label(ch): ch["channelId"] for ch in all_channels}
            ch_ids = list(ch_options.values())

            # Find current index
            current_idx = 0
            if saved_channel_id in ch_ids:
                current_idx = ch_ids.index(saved_channel_id)

            selected_label = st.selectbox(
                "Активный канал для рассылки",
                list(ch_options.keys()),
                index=current_idx,
                help="Все каналы из твоего аккаунта Wazzup"
            )
            selected_channel_id = ch_options[selected_label]

            # Show details
            selected_ch = next((c for c in all_channels if c["channelId"] == selected_channel_id), {})
            col_d1, col_d2, col_d3 = st.columns(3)
            col_d1.write(f"**Тип:** {selected_ch.get('transport','—').capitalize()}")
            col_d2.write(f"**Номер/ID:** {selected_ch.get('plainId','—')}")
            col_d3.write(f"**Статус:** {'✅ Активен' if selected_ch.get('state') == 'active' else '⚠️ ' + selected_ch.get('state','—')}")

            if st.button("💾 Сохранить канал", type="primary"):
                set_setting("wazzup_channel_id", selected_channel_id)
                os.environ["WAZZUP_CHANNEL_ID"] = selected_channel_id
                st.success(f"✅ Канал сохранён: {selected_label}")

            if saved_channel_id:
                active_ch = next((c for c in all_channels if c["channelId"] == saved_channel_id), None)
                if active_ch:
                    st.info(f"Текущий активный канал: **{channel_label(active_ch)}**")
    except Exception as e:
        st.error(f"Ошибка загрузки каналов: {e}")

    st.divider()
    st.subheader("Текущий .env")
    st.code("""AMO_SUBDOMAIN=moonai
AMO_CLIENT_ID=...
AMO_CLIENT_SECRET=...
AMO_ACCESS_TOKEN=...
WAZZUP_API_KEY=...
ANTHROPIC_API_KEY=...
OPENAI_API_KEY=...   # для GPT моделей""", language="bash")
