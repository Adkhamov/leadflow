CSS = """
<style>
/* ── Основной фон ─────────────────────────────────────────────────────── */
.stApp { background: #F3F4F6; }
.main .block-container { padding: 2rem 2.5rem; max-width: 1200px; }

/* ── Тёмный сайдбар ───────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: #1E1E2E !important;
    border-right: none !important;
    min-width: 240px !important;
}
[data-testid="stSidebar"] * { color: #C4C4D4 !important; }

/* Логотип */
[data-testid="stSidebar"] .stMarkdown p {
    color: #FFFFFF !important;
}

/* Пункты меню */
[data-testid="stSidebar"] .stRadio > div { gap: 2px; }
[data-testid="stSidebar"] .stRadio label {
    display: block !important;
    padding: 9px 14px !important;
    border-radius: 8px !important;
    font-size: 0.875rem !important;
    color: #A0A0B8 !important;
    cursor: pointer;
    transition: background 0.15s, color 0.15s;
}
[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(255,255,255,0.08) !important;
    color: #FFFFFF !important;
}
[data-testid="stSidebar"] .stRadio [data-baseweb="radio"] input:checked ~ div ~ label,
[data-testid="stSidebar"] .stRadio label:has(input:checked) {
    background: rgba(124,58,237,0.25) !important;
    color: #FFFFFF !important;
}
[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.1) !important;
    margin: 12px 0 !important;
}
[data-testid="stSidebar"] .stCaption,
[data-testid="stSidebar"] small { color: #6B6B8A !important; }

/* Скрыть кнопку сворачивания сайдбара */
[data-testid="stSidebarCollapseButton"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }

/* ── Заголовки ────────────────────────────────────────────────────────── */
h1 { font-size: 1.6rem !important; font-weight: 700 !important; color: #111827 !important; margin-bottom: 0.25rem !important; }
h2 { font-size: 1.2rem !important; font-weight: 600 !important; color: #111827 !important; }
h3 { font-size: 1rem !important;   font-weight: 600 !important; color: #374151 !important; }

/* ── Кнопки ───────────────────────────────────────────────────────────── */
.stButton > button {
    background: #7C3AED !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    padding: 0.5rem 1.25rem !important;
    transition: background 0.15s, box-shadow 0.15s !important;
    box-shadow: 0 2px 6px rgba(124,58,237,0.25) !important;
}
.stButton > button:hover {
    background: #6D28D9 !important;
    box-shadow: 0 4px 14px rgba(124,58,237,0.4) !important;
}
.stButton > button[kind="secondary"] {
    background: #FFFFFF !important;
    color: #374151 !important;
    border: 1px solid #D1D5DB !important;
    box-shadow: none !important;
}
.stButton > button[kind="secondary"]:hover { background: #F9FAFB !important; }

/* ── Карточки-метрики ─────────────────────────────────────────────────── */
[data-testid="metric-container"] {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 12px;
    padding: 1.1rem 1.25rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
[data-testid="metric-container"] label {
    color: #6B7280 !important;
    font-size: 0.75rem !important;
    font-weight: 500 !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-size: 1.9rem !important;
    font-weight: 700 !important;
    color: #111827 !important;
}

/* ── Таблицы ──────────────────────────────────────────────────────────── */
[data-testid="stDataFrame"] {
    border: 1px solid #E5E7EB !important;
    border-radius: 12px !important;
    overflow: hidden !important;
    background: #FFFFFF !important;
}

/* ── Инпуты ───────────────────────────────────────────────────────────── */
.stTextInput input, .stTextArea textarea,
.stNumberInput input {
    background: #FFFFFF !important;
    border: 1px solid #D1D5DB !important;
    border-radius: 8px !important;
    color: #111827 !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #7C3AED !important;
    box-shadow: 0 0 0 3px rgba(124,58,237,0.12) !important;
}
.stSelectbox > div > div,
.stMultiSelect > div > div {
    background: #FFFFFF !important;
    border: 1px solid #D1D5DB !important;
    border-radius: 8px !important;
}

/* ── Expander ─────────────────────────────────────────────────────────── */
[data-testid="stExpander"] {
    background: #FFFFFF !important;
    border: 1px solid #E5E7EB !important;
    border-radius: 10px !important;
    margin-bottom: 6px !important;
}

/* ── Alert блоки ──────────────────────────────────────────────────────── */
[data-testid="stAlert"] { border-radius: 10px !important; border: none !important; }

/* ── Progress ─────────────────────────────────────────────────────────── */
.stProgress > div > div > div { background: #7C3AED !important; border-radius: 99px !important; }

/* ── Divider ──────────────────────────────────────────────────────────── */
hr { border: none !important; border-top: 1px solid #E5E7EB !important; margin: 1.25rem 0 !important; }

/* ── Кастомные карточки ───────────────────────────────────────────────── */
.lf-card {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 12px;
    padding: 1.25rem;
    margin-bottom: 0.75rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    transition: box-shadow 0.15s, transform 0.15s;
}
.lf-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.09); }

.lf-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.73rem;
    font-weight: 600;
    letter-spacing: 0.02em;
}
.lf-badge-red    { background: #FEF2F2; color: #DC2626; }
.lf-badge-green  { background: #F0FDF4; color: #16A34A; }
.lf-badge-yellow { background: #FFFBEB; color: #B45309; }
.lf-badge-purple { background: #F5F3FF; color: #7C3AED; }
.lf-badge-gray   { background: #F3F4F6; color: #6B7280; }
.lf-badge-blue   { background: #EFF6FF; color: #2563EB; }

.lf-page-title    { font-size: 1.5rem; font-weight: 700; color: #111827; margin-bottom: 4px; }
.lf-page-subtitle { font-size: 0.875rem; color: #6B7280; margin-bottom: 1.5rem; }

/* ── Убрать лишнее ────────────────────────────────────────────────────── */
footer { display: none !important; }
#MainMenu { display: none !important; }
[data-testid="stToolbar"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }
</style>
"""


EXPAND_JS = """
<script>
(function() {
    function tryExpand() {
        // Ищем кнопку раскрытия (когда сайдбар закрыт)
        var btn = document.querySelector('[data-testid="collapsedControl"]');
        if (btn) { btn.click(); return true; }
        // Fallback: ищем кнопку с aria-expanded=false рядом с сайдбаром
        var sidebar = document.querySelector('[data-testid="stSidebar"]');
        if (!sidebar) {
            var allBtns = document.querySelectorAll('button');
            for (var i = 0; i < allBtns.length; i++) {
                if (allBtns[i].getAttribute('aria-expanded') === 'false') {
                    allBtns[i].click(); return true;
                }
            }
        }
        return false;
    }
    // Пробуем несколько раз пока Streamlit грузится
    [300, 800, 1500, 3000].forEach(function(ms) {
        setTimeout(function() {
            var sidebar = document.querySelector('[data-testid="stSidebar"]');
            if (!sidebar) tryExpand();
        }, ms);
    });
})();
</script>
"""


def inject():
    import streamlit as st
    st.markdown(CSS, unsafe_allow_html=True)
    st.markdown(EXPAND_JS, unsafe_allow_html=True)


def badge(text: str, color: str = "gray") -> str:
    return f'<span class="lf-badge lf-badge-{color}">{text}</span>'


SEGMENT_BADGE = {
    "hot":  badge("🔥 Горячий", "red"),
    "warm": badge("🌤 Тёплый",  "yellow"),
    "cold": badge("🧊 Холодный", "gray"),
}
