CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

* { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important; }

/* ── Основной фон ─────────────────────────────────────────────────────── */
.stApp { background: #F6F8FA; }
.main .block-container { padding: 2rem 2.5rem; max-width: 1280px; }

/* ── Сайдбар — белый, чистый ──────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-right: 1px solid #E3E8EF !important;
    min-width: 220px !important;
    max-width: 220px !important;
}
[data-testid="stSidebar"] * { color: #425466 !important; }
[data-testid="stSidebar"] .stMarkdown p { color: #0A2540 !important; }

/* Пункты меню */
[data-testid="stSidebar"] .stRadio > div { gap: 1px; }
[data-testid="stSidebar"] .stRadio label input[type="radio"] { display: none !important; }
[data-testid="stSidebar"] .stRadio label p { margin: 0 !important; }
[data-testid="stSidebar"] .stRadio label {
    display: block !important;
    padding: 8px 16px !important;
    border-radius: 6px !important;
    font-size: 0.84rem !important;
    font-weight: 500 !important;
    color: #425466 !important;
    cursor: pointer;
    transition: background 0.12s, color 0.12s;
    border-left: 3px solid transparent !important;
    margin: 1px 6px !important;
}
[data-testid="stSidebar"] .stRadio label:hover {
    background: #F6F8FA !important;
    color: #0A2540 !important;
}
[data-testid="stSidebar"] .stRadio label:has(input:checked) {
    background: #EEF2FF !important;
    color: #635BFF !important;
    border-left: 3px solid #635BFF !important;
    font-weight: 600 !important;
}
[data-testid="stSidebar"] hr {
    border-color: #E3E8EF !important;
    margin: 10px 16px !important;
}
[data-testid="stSidebar"] .stCaption,
[data-testid="stSidebar"] small { color: #8898AA !important; }

/* Скрыть кнопки сворачивания */
[data-testid="stSidebarCollapseButton"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }

/* ── Заголовки ────────────────────────────────────────────────────────── */
h1 { font-size: 1.45rem !important; font-weight: 700 !important; color: #0A2540 !important; margin-bottom: 0.2rem !important; letter-spacing: -0.02em !important; }
h2 { font-size: 1.1rem !important; font-weight: 600 !important; color: #0A2540 !important; }
h3 { font-size: 0.95rem !important; font-weight: 600 !important; color: #425466 !important; }

/* ── Кнопки ───────────────────────────────────────────────────────────── */
.stButton > button {
    background: #635BFF !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 500 !important;
    font-size: 0.875rem !important;
    padding: 0.5rem 1.1rem !important;
    transition: background 0.12s, box-shadow 0.12s !important;
    box-shadow: 0 1px 3px rgba(99,91,255,0.3), 0 1px 2px rgba(0,0,0,0.06) !important;
    letter-spacing: 0.01em !important;
}
.stButton > button:hover {
    background: #4F46E5 !important;
    box-shadow: 0 4px 12px rgba(99,91,255,0.35) !important;
}
.stButton > button[kind="secondary"] {
    background: #FFFFFF !important;
    color: #425466 !important;
    border: 1px solid #E3E8EF !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05) !important;
}
.stButton > button[kind="secondary"]:hover {
    background: #F6F8FA !important;
    color: #0A2540 !important;
}

/* ── Метрики ──────────────────────────────────────────────────────────── */
[data-testid="metric-container"] {
    background: #FFFFFF;
    border: 1px solid #E3E8EF;
    border-radius: 8px;
    padding: 1.1rem 1.25rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
[data-testid="metric-container"] label {
    color: #8898AA !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-size: 1.75rem !important;
    font-weight: 700 !important;
    color: #0A2540 !important;
    letter-spacing: -0.02em !important;
}
[data-testid="metric-container"] [data-testid="stMetricDelta"] {
    font-size: 0.8rem !important;
    font-weight: 500 !important;
}

/* ── Таблицы ──────────────────────────────────────────────────────────── */
[data-testid="stDataFrame"] {
    border: 1px solid #E3E8EF !important;
    border-radius: 8px !important;
    overflow: hidden !important;
    background: #FFFFFF !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
}

/* ── Инпуты ───────────────────────────────────────────────────────────── */
.stTextInput input, .stTextArea textarea, .stNumberInput input {
    background: #FFFFFF !important;
    border: 1px solid #D5DCE6 !important;
    border-radius: 6px !important;
    color: #0A2540 !important;
    font-size: 0.875rem !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04) !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #635BFF !important;
    box-shadow: 0 0 0 3px rgba(99,91,255,0.15) !important;
}
.stSelectbox > div > div, .stMultiSelect > div > div {
    background: #FFFFFF !important;
    border: 1px solid #D5DCE6 !important;
    border-radius: 6px !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04) !important;
}

/* ── Expander ─────────────────────────────────────────────────────────── */
[data-testid="stExpander"] {
    background: #FFFFFF !important;
    border: 1px solid #E3E8EF !important;
    border-radius: 8px !important;
    margin-bottom: 6px !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.03) !important;
}

/* ── Alert блоки ──────────────────────────────────────────────────────── */
[data-testid="stAlert"] { border-radius: 8px !important; border: none !important; }
[data-testid="stAlert"][data-baseweb="notification"] {
    box-shadow: 0 1px 3px rgba(0,0,0,0.06) !important;
}

/* ── Progress ─────────────────────────────────────────────────────────── */
.stProgress > div > div > div { background: #635BFF !important; border-radius: 99px !important; }

/* ── Divider ──────────────────────────────────────────────────────────── */
hr { border: none !important; border-top: 1px solid #E3E8EF !important; margin: 1.25rem 0 !important; }

/* ── Кастомные карточки ───────────────────────────────────────────────── */
.lf-card {
    background: #FFFFFF;
    border: 1px solid #E3E8EF;
    border-radius: 8px;
    padding: 1.25rem;
    margin-bottom: 0.75rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.03);
    transition: box-shadow 0.15s;
}
.lf-card:hover { box-shadow: 0 4px 14px rgba(0,0,0,0.08); }

/* ── KPI сетка ───────────────────────────────────────────────────────── */
.lf-kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 12px;
    margin-bottom: 1.5rem;
}
.lf-kpi {
    background: #FFFFFF;
    border: 1px solid #E3E8EF;
    border-radius: 8px;
    padding: 1rem 1.25rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.lf-kpi-value {
    font-size: 1.75rem;
    font-weight: 700;
    color: #0A2540;
    letter-spacing: -0.02em;
    line-height: 1;
    margin-bottom: 4px;
}
.lf-kpi-label {
    font-size: 0.72rem;
    font-weight: 600;
    color: #8898AA;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

/* ── Бейджи ───────────────────────────────────────────────────────────── */
.lf-badge {
    display: inline-block;
    padding: 2px 9px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.02em;
}
.lf-badge-red    { background: #FFF0F0; color: #C0152A; }
.lf-badge-green  { background: #EDFAF3; color: #0D7A40; }
.lf-badge-yellow { background: #FFF8E6; color: #946500; }
.lf-badge-purple { background: #EEF2FF; color: #635BFF; }
.lf-badge-gray   { background: #F6F8FA; color: #6B7280; border: 1px solid #E3E8EF; }
.lf-badge-blue   { background: #EFF6FF; color: #1D4ED8; }

/* ── Заголовки страниц ────────────────────────────────────────────────── */
.lf-page-title    { font-size: 1.45rem; font-weight: 700; color: #0A2540; margin-bottom: 2px; letter-spacing: -0.02em; }
.lf-page-subtitle { font-size: 0.84rem; color: #8898AA; margin-bottom: 1.5rem; font-weight: 400; }

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
        var btn = document.querySelector('[data-testid="collapsedControl"]');
        if (btn) { btn.click(); return true; }
        var allBtns = document.querySelectorAll('button');
        for (var i = 0; i < allBtns.length; i++) {
            if (allBtns[i].getAttribute('aria-expanded') === 'false') {
                allBtns[i].click(); return true;
            }
        }
        return false;
    }
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
