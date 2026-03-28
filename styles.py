CSS = """
<style>
/* ── Основной фон ─────────────────────────────────────────────────────── */
.stApp { background: #F9FAFB; }
.main .block-container { padding: 2rem 2.5rem; max-width: 1200px; }

/* ── Сайдбар ──────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-right: 1px solid #E5E7EB;
}
[data-testid="stSidebar"] .stRadio label {
    font-size: 0.875rem;
    color: #374151;
    padding: 6px 10px;
    border-radius: 8px;
    transition: background 0.15s;
}
[data-testid="stSidebar"] .stRadio label:hover { background: #F3F4F6; }
[data-testid="stSidebar"] h1 {
    font-size: 1.2rem !important;
    font-weight: 700;
    color: #111827;
}
[data-testid="stSidebar"] hr { border-color: #E5E7EB; }
[data-testid="stSidebar"] .stCaption { color: #6B7280; font-size: 0.78rem; }

/* ── Заголовки ────────────────────────────────────────────────────────── */
h1 { font-size: 1.75rem !important; font-weight: 700 !important; color: #111827 !important; }
h2 { font-size: 1.25rem !important; font-weight: 600 !important; color: #111827 !important; }
h3 { font-size: 1.05rem !important; font-weight: 600 !important; color: #374151 !important; }

/* ── Кнопки ───────────────────────────────────────────────────────────── */
.stButton > button {
    background: #7C3AED !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    padding: 0.5rem 1.25rem !important;
    transition: background 0.15s, box-shadow 0.15s !important;
}
.stButton > button:hover {
    background: #6D28D9 !important;
    box-shadow: 0 4px 12px rgba(124,58,237,0.3) !important;
}
.stButton > button[kind="secondary"] {
    background: #F3F4F6 !important;
    color: #374151 !important;
}
.stButton > button[kind="secondary"]:hover { background: #E5E7EB !important; }

/* ── Метрики ──────────────────────────────────────────────────────────── */
[data-testid="metric-container"] {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
[data-testid="metric-container"] label {
    color: #6B7280 !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-size: 1.8rem !important;
    font-weight: 700 !important;
    color: #111827 !important;
}
[data-testid="metric-container"] [data-testid="stMetricDelta"] { font-size: 0.82rem !important; }

/* ── Таблицы / датафреймы ─────────────────────────────────────────────── */
[data-testid="stDataFrame"] {
    border: 1px solid #E5E7EB;
    border-radius: 12px;
    overflow: hidden;
}

/* ── Инпуты ───────────────────────────────────────────────────────────── */
.stTextInput > div > div > input,
.stSelectbox > div > div,
.stMultiSelect > div > div,
.stNumberInput > div > div > input,
.stTextArea > div > div > textarea {
    border: 1px solid #D1D5DB !important;
    border-radius: 8px !important;
    background: #FFFFFF !important;
    color: #111827 !important;
}
.stTextInput > div > div > input:focus,
.stSelectbox > div > div:focus-within,
.stTextArea > div > div > textarea:focus {
    border-color: #7C3AED !important;
    box-shadow: 0 0 0 3px rgba(124,58,237,0.1) !important;
}

/* ── Разделитель ──────────────────────────────────────────────────────── */
hr { border: none; border-top: 1px solid #E5E7EB; margin: 1.5rem 0; }

/* ── Expander ─────────────────────────────────────────────────────────── */
[data-testid="stExpander"] {
    border: 1px solid #E5E7EB !important;
    border-radius: 10px !important;
    background: #FFFFFF;
    margin-bottom: 0.5rem;
}
[data-testid="stExpander"] summary { font-weight: 500; color: #374151; }

/* ── Info / Success / Warning / Error блоки ──────────────────────────── */
[data-testid="stAlert"] { border-radius: 10px !important; border: none !important; }
div[data-baseweb="notification"] { border-radius: 10px !important; }

/* ── Progress bar ─────────────────────────────────────────────────────── */
.stProgress > div > div > div { background: #7C3AED !important; }

/* ── Чекбоксы ─────────────────────────────────────────────────────────── */
.stCheckbox label { color: #374151 !important; font-size: 0.9rem !important; }

/* ── Слайдеры ─────────────────────────────────────────────────────────── */
.stSlider [data-baseweb="slider"] div[role="slider"] { background: #7C3AED !important; }

/* ── Карточки (кастомные HTML-блоки) ─────────────────────────────────── */
.lf-card {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 12px;
    padding: 1.25rem;
    margin-bottom: 0.75rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    transition: box-shadow 0.15s;
}
.lf-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.08); }

.lf-badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 500;
}
.lf-badge-red    { background: #FEF2F2; color: #DC2626; }
.lf-badge-green  { background: #F0FDF4; color: #16A34A; }
.lf-badge-yellow { background: #FFFBEB; color: #D97706; }
.lf-badge-purple { background: #F5F3FF; color: #7C3AED; }
.lf-badge-gray   { background: #F3F4F6; color: #6B7280; }

.lf-stat-row {
    display: flex;
    gap: 1rem;
    margin: 1rem 0;
}
.lf-stat {
    flex: 1;
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    text-align: center;
}
.lf-stat-value { font-size: 2rem; font-weight: 700; color: #111827; }
.lf-stat-label { font-size: 0.78rem; color: #6B7280; text-transform: uppercase; letter-spacing: 0.04em; margin-top: 4px; }

.lf-page-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: #111827;
    margin-bottom: 0.25rem;
}
.lf-page-subtitle {
    font-size: 0.9rem;
    color: #6B7280;
    margin-bottom: 1.5rem;
}

/* ── Скрыть стандартный Streamlit footer ─────────────────────────────── */
footer { display: none !important; }
#MainMenu { display: none !important; }
[data-testid="stToolbar"] { display: none !important; }
</style>
"""


def inject():
    import streamlit as st
    st.markdown(CSS, unsafe_allow_html=True)


def card(content: str, hover: bool = True) -> str:
    cls = "lf-card" + (" lf-card-hover" if hover else "")
    return f'<div class="{cls}">{content}</div>'


def badge(text: str, color: str = "gray") -> str:
    return f'<span class="lf-badge lf-badge-{color}">{text}</span>'


SEGMENT_BADGE = {
    "hot":  badge("🔥 Горячий", "red"),
    "warm": badge("🌤 Тёплый",  "yellow"),
    "cold": badge("🧊 Холодный","gray"),
}
