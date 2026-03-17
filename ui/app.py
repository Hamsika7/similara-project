import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import requests
import time
import uuid

API = "http://127.0.0.1:8000"

# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SIMILARA - Product Matching",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── GLOBAL CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=EB+Garamond:wght@400;600;700;800&family=DM+Sans:wght@300;400;500;600;700&display=swap');

:root {
    --bg: #f5f6fa;
    --card: #ffffff;
    --card2: #f0f2f8;
    --accent: #e74c3c;
    --accent-light: #ff6b6b;
    --gold: #e67e22;
    --green: #27ae60;
    --text: #1a1a2e;
    --muted: #6c7a8d;
    --border: rgba(0,0,0,0.10);
    --heading: #1a1a2e;
}

.stApp {
    background-color: #f5f6fa !important;
    font-family: 'DM Sans', sans-serif;
}

#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

section[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid rgba(0,0,0,0.10);
}
section[data-testid="stSidebar"] * { color: #1a1a2e !important; }
section[data-testid="stSidebar"] .stMarkdown p { color: #6c7a8d !important; }

.stApp, .stApp p, .stApp label, .stApp div { color: #1a1a2e; }

.stTextInput input, .stSelectbox select, .stFileUploader {
    background: #ffffff !important;
    border: 1.5px solid #d0d5e0 !important;
    border-radius: 8px !important;
    color: #1a1a2e !important;
}
.stTextInput input:focus { border-color: #e74c3c !important; }

/* ── All standard buttons: red accent ── */
.stButton > button {
    background: #e74c3c !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    font-family: 'DM Sans', sans-serif !important;
    letter-spacing: 0.5px !important;
    transition: all 0.15s !important;
}
.stButton > button:hover {
    background: #ff6b6b !important;
    transform: translateY(-1px);
    box-shadow: 0 6px 16px rgba(231,76,60,0.35) !important;
}

/* ── Ghost button ── */
.btn-ghost > button {
    background: transparent !important;
    border: 1.5px solid rgba(0,0,0,0.15) !important;
    color: #6c7a8d !important;
}

/* ── Dark/neutral button ── */
.btn-dark > button {
    background: #f0f2f8 !important;
    border: 1px solid rgba(0,0,0,0.15) !important;
    color: #1a1a2e !important;
}

/* ── Green button ── */
.btn-green > button {
    background: #eafaf1 !important;
    border: 1.5px solid #27ae60 !important;
    color: #1e8449 !important;
}

/* ── FIX: Download buttons (st.download_button) light theme ── */
[data-testid="stDownloadButton"] button {
    background: #f0f2f8 !important;
    color: #1a1a2e !important;
    border: 1.5px solid rgba(0,0,0,0.18) !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    font-family: 'DM Sans', sans-serif !important;
    width: 100% !important;
    height: 38px !important;
    min-height: 38px !important;
    padding: 0 16px !important;
    line-height: 38px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}
[data-testid="stDownloadButton"] button:hover {
    background: #e8eaf0 !important;
    color: #1a1a2e !important;
}

/* ── Ensure download button wrapper has no extra margin so it aligns with siblings ── */
[data-testid="stDownloadButton"] {
    display: flex !important;
    align-items: stretch !important;
    width: 100% !important;
}

/* ── Keep btn-dark wrapper transparent so it does not add height ── */
.btn-dark {
    display: contents !important;
}

/* ── FIX: Green-wrapped download button (Export Final Catalog) ── */
.btn-green [data-testid="stDownloadButton"] button {
    background: #eafaf1 !important;
    color: #1e8449 !important;
    border: 1.5px solid #27ae60 !important;
}
.btn-green [data-testid="stDownloadButton"] button:hover {
    background: #d5f5e3 !important;
    color: #1a6e38 !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #f0f2f8;
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #6c7a8d !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}
.stTabs [aria-selected="true"] {
    background: #e74c3c !important;
    color: white !important;
}

/* ── Expander ── */
.streamlit-expanderHeader {
    background: #f0f2f8 !important;
    border: 1px solid rgba(0,0,0,0.10) !important;
    border-radius: 10px !important;
    color: #1a1a2e !important;
}
.streamlit-expanderContent {
    background: #f0f2f8 !important;
    border: 1px solid rgba(0,0,0,0.10) !important;
    border-top: none !important;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    background: #ffffff !important;
    border: 2px dashed #c0c8d8 !important;
    border-radius: 14px !important;
    padding: 20px !important;
}
[data-testid="stFileUploader"] section {
    background-color: #f8f9fc !important;
    border: 2px dashed #c0c8d8 !important;
    border-radius: 10px !important;
}
[data-testid="stFileUploader"] section > div {
    background-color: #f8f9fc !important;
    color: #1a1a2e !important;
}
[data-testid="stFileUploader"] section button {
    background-color: #ffffff !important;
    color: #1a1a2e !important;
    border: 1px solid #c0c8d8 !important;
    border-radius: 6px !important;
}
[data-testid="stFileUploader"] section small {
    color: #6c7a8d !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] {
    color: #1a1a2e !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] span {
    color: #6c7a8d !important;
}

/* ── Selectbox trigger (the closed input box) ── */
.stSelectbox [data-baseweb="select"] div,
[data-baseweb="select"] div,
[data-baseweb="select"] span,
[data-baseweb="select"] input {
    background-color: #ffffff !important;
    color: #1a1a2e !important;
    border-color: rgba(0,0,0,0.15) !important;
}

/* ── Progress bar ── */
.stProgress > div > div { background: #e74c3c !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #f5f6fa; }
::-webkit-scrollbar-thumb { background: rgba(0,0,0,0.15); border-radius: 3px; }

/* ── Metrics ── */
[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid rgba(0,0,0,0.10);
    border-radius: 12px;
    padding: 16px;
}
[data-testid="stMetricValue"] { color: #1a1a2e !important; }
[data-testid="stMetricLabel"] { color: #6c7a8d !important; }

hr { border-color: rgba(0,0,0,0.10) !important; }

/* ── FIX: st.table — visible text in data preview ── */
[data-testid="stTable"] table {
    background-color: #ffffff !important;
    color: #1a1a2e !important;
    border-collapse: collapse !important;
    width: 100% !important;
    font-size: 13px !important;
    font-family: 'DM Sans', sans-serif !important;
}
[data-testid="stTable"] thead tr th {
    background-color: #f0f2f8 !important;
    color: #1a1a2e !important;
    font-weight: 700 !important;
    font-size: 11px !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
    padding: 10px 14px !important;
    border-bottom: 2px solid rgba(0,0,0,0.10) !important;
    white-space: nowrap !important;
}
[data-testid="stTable"] tbody tr td {
    background-color: #ffffff !important;
    color: #1a1a2e !important;
    font-size: 12px !important;
    padding: 9px 14px !important;
    border-bottom: 1px solid rgba(0,0,0,0.06) !important;
    max-width: 260px !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    white-space: nowrap !important;
}
[data-testid="stTable"] tbody tr:hover td {
    background-color: #f8f9fc !important;
}
[data-testid="stTable"] {
    border: 1px solid rgba(0,0,0,0.10) !important;
    border-radius: 10px !important;
    overflow: hidden !important;
}
.stMarkdown table {
    background-color: #ffffff !important;
    color: #1a1a2e !important;
}
.stMarkdown table th {
    background-color: #f0f2f8 !important;
    color: #1a1a2e !important;
}
.stMarkdown table td {
    background-color: #ffffff !important;
    color: #1a1a2e !important;
}

/* ── Dataframe outer wrapper ── */
.stDataFrame {
    background-color: #ffffff !important;
    border: 1px solid rgba(0,0,0,0.10) !important;
    border-radius: 10px !important;
    color-scheme: light !important;
}
[data-testid="stDataFrame"] {
    background: #ffffff !important;
    color-scheme: light !important;
}
[data-testid="stDataFrame"] iframe {
    background: #ffffff !important;
    color-scheme: light !important;
}
[data-testid="stDataFrame"] button {
    background-color: #f0f2f8 !important;
    color: #1a1a2e !important;
    border: 1px solid rgba(0,0,0,0.15) !important;
}
</style>
""", unsafe_allow_html=True)

# ─── JS: Force light theme on BaseWeb dropdown portal ─────────────────────────
st.markdown("""
<script>
(function() {
    var LIGHT_BG   = '#ffffff';
    var HOVER_BG   = '#f0f2f8';
    var TEXT_COLOR = '#1a1a2e';

    function styleDropdown(root) {
        root.querySelectorAll('[data-baseweb="popover"],[data-baseweb="menu"]')
            .forEach(function(el) {
                el.style.setProperty('background-color', LIGHT_BG,   'important');
                el.style.setProperty('background',       LIGHT_BG,   'important');
                el.style.setProperty('color',            TEXT_COLOR, 'important');
                el.style.setProperty('border',           '1px solid rgba(0,0,0,0.12)', 'important');
                el.style.setProperty('border-radius',    '8px',      'important');
                el.style.setProperty('box-shadow',       '0 4px 20px rgba(0,0,0,0.12)', 'important');
            });
        root.querySelectorAll('[data-baseweb="popover"] div,[data-baseweb="popover"] ul,[data-baseweb="popover"] li,[data-baseweb="popover"] span')
            .forEach(function(el) {
                el.style.setProperty('background-color', LIGHT_BG,   'important');
                el.style.setProperty('color',            TEXT_COLOR, 'important');
            });
        root.querySelectorAll('[data-baseweb="option"]')
            .forEach(function(el) {
                el.style.setProperty('background-color', LIGHT_BG,   'important');
                el.style.setProperty('color',            TEXT_COLOR, 'important');
                if (!el._simHoverBound) {
                    el._simHoverBound = true;
                    el.addEventListener('mouseenter', function() {
                        el.style.setProperty('background-color', HOVER_BG, 'important');
                    });
                    el.addEventListener('mouseleave', function() {
                        el.style.setProperty('background-color', LIGHT_BG, 'important');
                    });
                }
            });
        root.querySelectorAll('[data-baseweb="menu"] ul,[data-baseweb="menu"] li')
            .forEach(function(el) {
                el.style.setProperty('background-color', LIGHT_BG,   'important');
                el.style.setProperty('color',            TEXT_COLOR, 'important');
            });
    }

    var observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(m) {
            m.addedNodes.forEach(function(node) {
                if (node.nodeType !== 1) return;
                styleDropdown(node.parentElement || document.body);
                styleDropdown(node);
            });
        });
        styleDropdown(document.body);
    });

    observer.observe(document.body, { childList: true, subtree: true });
    styleDropdown(document.body);
})();
</script>
""", unsafe_allow_html=True)

# ─── SESSION STATE ────────────────────────────────────────────────────────────
for key, default in {
    "screen": "login", "role": None,
    "dataset_loaded": False, "processing_done": False,
    "scan_result": None, "uploaded_df": None,
    "clusters": [], "clean_products": [],
    "catalog_category": "All", "drawer_product": None,
    "catalog_view_mode": "grid", "login_error": ""
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ─── HELPERS ──────────────────────────────────────────────────────────────────
CARD_COLORS = [
    ("e8f4f8","2980b9"),("f8f0e3","c0392b"),("f0f8e8","27ae60"),
    ("fdf2f8","8e44ad"),("fff8e1","f39c12"),("e8f8f5","1abc9c"),
    ("fef9e7","e67e22"),("eaf2ff","3498db"),("f5f5f5","555555"),
    ("fff0f0","e74c3c"),
]

def img_url(i, text):
    bg, fg = CARD_COLORS[i % len(CARD_COLORS)]
    short = text[:14].replace(" ", "+")
    return f"https://placehold.co/300x160/{bg}/{fg}?text={short}"

def confidence_badge(score):
    if score >= 90:
        return '<span style="background:#27ae6022;color:#27ae60;border:1px solid #27ae6044;border-radius:20px;padding:2px 10px;font-size:11px;font-weight:700;">✦ HIGH</span>'
    elif score >= 70:
        return '<span style="background:#f39c1222;color:#f39c12;border:1px solid #f39c1244;border-radius:20px;padding:2px 10px;font-size:11px;font-weight:700;">◆ MED</span>'
    else:
        return '<span style="background:#e74c3c22;color:#e74c3c;border:1px solid #e74c3c44;border-radius:20px;padding:2px 10px;font-size:11px;font-weight:700;">▲ LOW</span>'

def stars(score):
    n = round((score / 100) * 5)
    return "★" * n + "☆" * (5 - n) + f" {score}%"

def reason_badge(reason):
    return f'<span style="background:#fef3e2;color:#b7770d;border:1px solid #e67e22;border-radius:12px;padding:2px 10px;font-size:11px;font-weight:600;">{reason}</span>'

def section_header(emoji, title, subtitle="", step=""):
    step_html = f'<div style="color:#e74c3c;font-size:12px;letter-spacing:2px;text-transform:uppercase;margin-bottom:6px;font-weight:700;">{step}</div>' if step else ""
    sub_html  = f'<p style="color:#6c7a8d;margin:6px 0 0;font-size:14px;">{subtitle}</p>' if subtitle else ""
    st.markdown(f"""
    {step_html}
    <h2 style="margin:0;font-size:28px;font-weight:800;color:#1a1a2e;
        font-family:'EB Garamond',serif;">{emoji} {title}</h2>
    {sub_html}
    """, unsafe_allow_html=True)
    st.markdown("<div style='margin-bottom:24px'></div>", unsafe_allow_html=True)

def stat_row(items):
    cols = st.columns(len(items))
    for col, (label, value, icon, color) in zip(cols, items):
        with col:
            st.markdown(f"""
            <div style="background:#ffffff;border:1px solid rgba(0,0,0,0.12);
                border-radius:12px;padding:18px 16px;text-align:center;">
                <div style="font-size:24px;margin-bottom:6px;">{icon}</div>
                <div style="font-size:26px;font-weight:900;color:{color};">{value}</div>
                <div style="color:#4a5568;font-size:12px;text-transform:uppercase;
                    letter-spacing:1px;margin-top:4px;">{label}</div>
            </div>
            """, unsafe_allow_html=True)

def check_api():
    try:
        r = requests.get(f"{API}/health", timeout=3)
        return r.status_code == 200
    except Exception:
        return False

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
# ─── TOP NAVIGATION BAR ───────────────────────────────────────────────────────
def render_topnav():
    """
    Reliable top navbar using pure st.columns — no sidebar, no CSS hacks.
    Logo on the left | step buttons in the middle | role + logout on the right.
    """
    screen = st.session_state.screen
    role   = st.session_state.role

    # ── Navbar CSS ──
    st.markdown("""
    <style>
    /* Hide the Streamlit default sidebar toggle arrow entirely */
    section[data-testid="stSidebar"] { display: none !important; }
    button[data-testid="stBaseButton-header"] { display: none !important; }
    [data-testid="collapsedControl"]          { display: none !important; }

    /* Navbar wrapper with card styling */
    .sim-nav {
        background: #ffffff;
        border-bottom: 1.5px solid rgba(0,0,0,0.08);
        border-radius: 12px;
        padding: 8px 16px;
        margin-bottom: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        display: flex;
        align-items: center;
        gap: 6px;
    }

    /* Nav step buttons — HIGHER SPECIFICITY to beat global .stButton > button */
    div.sim-nav-wrap div.sim-nav-btn button[data-testid="stBaseButton-secondary"] {
        background: transparent !important;
        color: #6c7a8d !important;
        border: none !important;
        border-radius: 8px !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        padding: 8px 16px !important;
        height: auto !important;
        box-shadow: none !important;
        letter-spacing: 0 !important;
        transition: all 0.15s !important;
        white-space: nowrap !important;
    }
    div.sim-nav-wrap div.sim-nav-btn button[data-testid="stBaseButton-secondary"]:hover {
        background: rgba(231,76,60,0.08) !important;
        color: #1a1a2e !important;
        transform: none !important;
        box-shadow: none !important;
    }

    /* Active step — white bg, red text, red border */
    div.sim-nav-wrap div.sim-nav-active button[data-testid="stBaseButton-secondary"] {
        background: #ffffff !important;
        color: #e74c3c !important;
        border: 2px solid #e74c3c !important;
        border-radius: 8px !important;
        font-size: 13px !important;
        font-weight: 700 !important;
        padding: 8px 16px !important;
        height: auto !important;
        box-shadow: none !important;
        letter-spacing: 0 !important;
        white-space: nowrap !important;
    }
    div.sim-nav-wrap div.sim-nav-active button[data-testid="stBaseButton-secondary"]:hover {
        background: #ffffff !important;
        color: #e74c3c !important;
        transform: none !important;
        box-shadow: none !important;
    }

    /* Logout button in nav — compact styling */
    div.sim-nav-wrap div.sim-nav-logout button[data-testid="stBaseButton-secondary"] {
        background: #fff5f5 !important;
        color: #c0392b !important;
        border: 1.5px solid #f5c6c0 !important;
        border-radius: 8px !important;
        font-size: 12px !important;
        font-weight: 700 !important;
        padding: 4px 12px !important;
        height: auto !important;
        box-shadow: none !important;
        letter-spacing: 0 !important;
        white-space: nowrap !important;
        min-height: 32px !important;
    }
    div.sim-nav-wrap div.sim-nav-logout button[data-testid="stBaseButton-secondary"]:hover {
        background: #fdecea !important;
        color: #c0392b !important;
        transform: none !important;
        box-shadow: none !important;
    }

    /* Remove top padding so navbar sits flush */
    .block-container {
        padding-top: 8px !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── Define steps ──
    all_steps = [
        ("upload",  "📁 Upload",    True),
        ("browse",  "🔍 Browse",    False),
        ("clean",   "✏️ Clean",     False),
        ("catalog", "🛍️ Catalog",   False),
    ]
    # Filter out admin-only steps for guests
    visible_steps = [
        (key, label)
        for key, label, admin_only in all_steps
        if not (admin_only and role == "guest")
    ]

    # ── Build columns: logo | steps... | spacer | role | logout ──
    # Ratios: [2, 1.5, 1.5, 1.5, 1.5, 3, 2, 1] for [logo, upload, browse, clean, catalog, spacer, role, logout]
    n_steps   = len(visible_steps)
    col_sizes = [2] + [1.5] * n_steps + [3, 2, 1]
    cols      = st.columns(col_sizes)
    
    # Wrap navbar in container div for CSS targeting
    st.markdown('<div class="sim-nav-wrap">', unsafe_allow_html=True)

    # Logo
    with cols[0]:
        st.markdown("""
        <div style="display:flex;align-items:center;gap:8px;padding:10px 4px;">
            <span style="font-size:22px;">🛒</span>
            <span style="font-weight:800;font-size:16px;letter-spacing:2px;
                color:#1a1a2e;font-family:'EB Garamond',serif;">SIMILARA</span>
        </div>
        """, unsafe_allow_html=True)

    # Step nav buttons
    for i, (key, label) in enumerate(visible_steps):
        with cols[1 + i]:
            css_class = "sim-nav-active" if screen == key else "sim-nav-btn"
            st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
            if st.button(label, key=f"topnav_{key}", use_container_width=True):
                st.session_state.screen = key
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    # Spacer — skip cols[1+n_steps]

    # Role badge
    result     = st.session_state.scan_result
    role_label = "👤 Admin" if role == "admin" else "👁 Guest"
    loaded_txt = f" · {result['total_products']} products" if result else ""
    with cols[1 + n_steps + 1]:
        st.markdown(f"""
        <div style="text-align:right;padding:10px 4px 0;">
            <div style="color:#1a1a2e;font-size:12px;font-weight:700;">{role_label}</div>
            <div style="color:#27ae60;font-size:10px;">{loaded_txt}</div>
        </div>
        """, unsafe_allow_html=True)

    # Logout
    with cols[1 + n_steps + 2]:
        st.markdown('<div class="sim-nav-logout">', unsafe_allow_html=True)
        if st.button("🚪 Out", key="topnav_logout", use_container_width=False):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Close navbar wrapper
    st.markdown('</div>', unsafe_allow_html=True)

    # Divider line under navbar
    st.markdown("<hr style='margin:0 0 20px;border-color:rgba(0,0,0,0.07);'>",
                unsafe_allow_html=True)

# ─── SCREEN 1: LOGIN ──────────────────────────────────────────────────────────
def screen_login():
    st.markdown("""
    <style>
    section[data-testid="stSidebar"] { display: none; }
    .block-container { padding-top: 0 !important; }
    </style>
    """, unsafe_allow_html=True)

    _, center, _ = st.columns([1, 1.2, 1])
    with center:
        st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)

        st.markdown("""
        <div style="text-align:center;margin-bottom:32px;">
            <div style="font-size:52px;margin-bottom:10px;">🛒</div>
            <h1 style="color:#1a1a2e;margin:0;font-size:36px;font-weight:800;
                letter-spacing:3px;font-family:'EB Garamond',serif;">SIMILARA</h1>
            <p style="color:#6c7a8d;margin:8px 0 0;font-size:13px;letter-spacing:1px;">
                Scalable Multimodal Framework for Retail Product Matching
            </p>
        </div>
        """, unsafe_allow_html=True)

        with st.container():
            username = st.text_input("USERNAME", placeholder="Enter username",
                                      key="login_user")
            password = st.text_input("PASSWORD", placeholder="Enter password",
                                      type="password", key="login_pass")

            st.markdown('<p style="color:#6c7a8d;font-size:12px;margin-bottom:4px;">💡 Hint: admin / admin123</p>',
                        unsafe_allow_html=True)

            if st.session_state.login_error:
                st.markdown(f"""
                <div style="background:#fdecea;border:1px solid #f5c6c0;
                    border-radius:6px;padding:10px 14px;color:#c0392b;
                    font-size:13px;margin-bottom:4px;">
                    {st.session_state.login_error}
                </div>
                """, unsafe_allow_html=True)

            if st.button("Login →", use_container_width=True, key="login_btn"):
                if not check_api():
                    st.session_state.login_error = "❌ API server is offline. Start uvicorn first."
                    st.rerun()
                elif username == "admin" and password == "admin123":
                    st.session_state.role        = "admin"
                    st.session_state.screen      = "upload"
                    st.session_state.login_error = ""
                    st.rerun()
                else:
                    st.session_state.login_error = "❌ Invalid credentials. Try admin / admin123"
                    st.rerun()

            st.markdown('<p style="text-align:center;color:#6c7a8d;font-size:12px;margin:12px 0;">— or —</p>',
                        unsafe_allow_html=True)

            if st.button("Continue as Guest 👁", use_container_width=True,
                         key="guest_btn"):
                st.session_state.role            = "guest"
                st.session_state.dataset_loaded  = True
                st.session_state.processing_done = True
                st.session_state.screen          = "browse"
                st.rerun()

# ─── SCREEN 2: UPLOAD ─────────────────────────────────────────────────────────
def screen_upload():
    section_header("📁", "Upload Unclean Product Data",
                   "Upload your raw product catalog CSV up to 200MB.",
                   "Step 1 of 4")

    uploaded = st.file_uploader(
        "Drag & drop CSV file or browse",
        type=["csv"],
        key="uploaded_file",
        label_visibility="collapsed"
    )

    if uploaded:
        st.session_state.dataset_loaded = True
        try:
            df = pd.read_csv(uploaded)
            st.session_state.uploaded_df = df
        except Exception:
            st.error("Could not read CSV. Make sure it is a valid file.")
            return

        st.markdown("""
        <div style="background:#27ae6018;border:1px solid #27ae6033;
            border-radius:10px;padding:14px 18px;margin:16px 0;">
            <span style="color:#27ae60;font-weight:700;">✅ File uploaded successfully!</span>
        </div>
        """, unsafe_allow_html=True)

        stat_row([
            ("File Name",  uploaded.name[:20],           "📄", "#1a1a2e"),
            ("Format",     "CSV",                         "📊", "#3498db"),
            ("Size",       f"{uploaded.size // 1024} KB", "💾", "#f39c12"),
            ("Rows",       str(len(df)),                  "📦", "#27ae60"),
        ])

        st.markdown("<div style='margin:24px 0 8px'></div>", unsafe_allow_html=True)

        st.markdown(
            '<div style="color:#1a1a2e;font-size:12px;text-transform:uppercase;'
            'letter-spacing:1px;margin-bottom:8px;font-weight:700;">📋 Data Preview</div>',
            unsafe_allow_html=True
        )
        st.table(df.head(5))

        st.markdown("<div style='margin:16px 0 8px'></div>", unsafe_allow_html=True)

        if st.button("⚙️ Process Dataset for Similarity Analysis",
                     use_container_width=True, key="process_btn"):

            if "product_name" not in df.columns:
                st.error(f"CSV must have 'product_name' column. Found: {list(df.columns)}")
                return

            bar    = st.progress(0)
            status = st.empty()

            fake_steps = [
                (20, "🧹 Cleaning text data..."),
                (40, "🔤 Running fuzzy matching..."),
                (60, "🧠 Generating SBERT embeddings..."),
                (80, "🖼️ Processing CLIP image features..."),
                (95, "⚖️ Computing fusion scores..."),
            ]
            for pct, msg in fake_steps:
                status.markdown(
                    f'<p style="color:#6c7a8d;font-size:13px;">{msg}</p>',
                    unsafe_allow_html=True)
                bar.progress(pct)
                time.sleep(0.4)

            try:
                uploaded.seek(0)
                response = requests.post(
                    f"{API}/bulk/",
                    files={"file": ("catalog.csv", uploaded, "text/csv")},
                    timeout=300
                )

                if response.status_code == 400:
                    st.error(response.json().get("detail", "Bad request"))
                    return

                result = response.json()
                bar.progress(100)
                status.empty()

                st.session_state.scan_result     = result
                st.session_state.clusters        = result.get("clusters", [])
                st.session_state.clean_products  = result.get("clean_products", [])
                st.session_state.processing_done = True
                st.rerun()

            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to API. Make sure uvicorn is running.")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

    if st.session_state.processing_done and st.session_state.scan_result:
        result = st.session_state.scan_result
        st.markdown("""
        <div style="background:#27ae6014;border:1px solid #27ae6044;
            border-radius:12px;padding:20px 24px;margin:20px 0;">
            <div style="color:#27ae60;font-weight:700;font-size:15px;
                margin-bottom:14px;">✅ Processing Complete!</div>
        """, unsafe_allow_html=True)

        rows = [
            ("Original products",           str(result["total_products"])),
            ("Duplicate pairs found",        str(result["duplicate_count"])),
            ("Unique clean products",        str(result["clean_count"])),
            ("Duplicate groups (clusters)",  str(result["cluster_count"])),
        ]
        for label, val in rows:
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;padding:8px 0;
                border-bottom:1px solid rgba(0,0,0,0.08);">
                <span style="color:#6c7a8d;font-size:13px;">{label}</span>
                <span style="color:#1a1a2e;font-weight:700;font-size:13px;">{val}</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown(f"""
            <div style="background:#fdecea;border:1px solid #f5c6c0;
                border-radius:8px;padding:12px 16px;margin-top:14px;
                color:#c0392b;font-weight:700;font-size:14px;">
                🗑️ Duplicates identified for removal:
                <strong>{result["duplicate_count"]}</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("← Back to Login", use_container_width=True,
                     key="upload_back"):
            st.session_state.screen = "login"
            st.rerun()
    with col2:
        if st.button(
            "Next: Browse Products →",
            use_container_width=True,
            key="upload_next",
            disabled=not st.session_state.processing_done
        ):
            st.session_state.screen = "browse"
            st.rerun()

# ─── SCREEN 3: BROWSE & MATCH ─────────────────────────────────────────────────
def screen_browse():
    section_header("🔍", "Product Matching Preview",
                   "Select any product to inspect its similarity matches.",
                   "Step 2 of 4")

    clusters = st.session_state.clusters
    if not clusters:
        st.info("No scan results yet. Upload a CSV first.")
        if st.button("← Go to Upload"):
            st.session_state.screen = "upload"
            st.rerun()
        return

    options = [f"{p['id']} — {p['name']}" for p in clusters]
    selected_label = st.selectbox("Select Product to Analyze",
                                   options, key="browse_select")
    idx = options.index(selected_label)
    p   = clusters[idx]

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    left, right = st.columns(2, gap="medium")

    with left:
        st.markdown(f"""
        <div style="background:#ffffff;border:1px solid rgba(0,0,0,0.12);
            border-radius:14px;padding:24px;height:100%;">
            <div style="color:#e74c3c;font-size:12px;letter-spacing:2px;
                text-transform:uppercase;margin-bottom:14px;font-weight:700;">
                📦 Product Details
            </div>
            <img src="{img_url(idx, p['name'])}"
                style="width:100%;height:160px;object-fit:cover;
                border-radius:10px;margin-bottom:16px;" />
            <div style="font-size:18px;font-weight:800;color:#1a1a2e;
                margin-bottom:16px;font-family:'EB Garamond',serif;">
                {p['name']}
            </div>
        """, unsafe_allow_html=True)

        details = [
            ("ID",         p["id"]),
            ("Category",   p["category"]),
            ("Duplicates", str(p["duplicates_merged"])),
            ("Confidence", p["confidence"].upper()),
            ("Avg Score",  f"{p['avg_similarity']}%"),
        ]
        for label, val in details:
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;padding:8px 0;
                border-bottom:1px solid rgba(0,0,0,0.07);">
                <span style="color:#4a5568;font-size:13px;">{label}</span>
                <span style="color:#1a1a2e;font-weight:600;font-size:13px;">{val}</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        conf    = p["confidence"]
        c_color  = "#27ae60" if conf == "high" else ("#f39c12" if conf == "medium" else "#e74c3c")
        c_bg     = f"{c_color}18"
        c_border = f"{c_color}44"
        c_label  = f"{'✅ High' if conf == 'high' else ('⚠️ Medium' if conf == 'medium' else '🔴 Low')} confidence matches"
        avg      = p["avg_similarity"]

        st.markdown(f"""
        <div style="background:#ffffff;border:1px solid rgba(0,0,0,0.12);
            border-radius:14px;padding:24px;">
            <div style="color:#e74c3c;font-size:12px;letter-spacing:2px;
                text-transform:uppercase;margin-bottom:14px;font-weight:700;">
                🎯 Similarity Analysis
            </div>
            <div style="color:#4a5568;font-size:13px;margin-bottom:4px;">
                Average Similarity
            </div>
            <div style="font-size:52px;font-weight:900;color:#1a1a2e;margin-bottom:10px;
                font-family:'EB Garamond',serif;">{avg}%</div>
            <div style="background:#e8eaf0;border-radius:8px;height:12px;
                margin-bottom:16px;overflow:hidden;">
                <div style="width:{avg}%;height:100%;
                    background:linear-gradient(90deg,#e74c3c,#ff6b6b);
                    border-radius:8px;"></div>
            </div>
            <div style="padding:10px 14px;border-radius:8px;margin-bottom:20px;
                background:{c_bg};border:1px solid {c_border};
                color:{c_color};font-size:13px;font-weight:600;">
                {c_label}
            </div>
            <div style="color:#4a5568;font-size:12px;letter-spacing:1px;
                text-transform:uppercase;margin-bottom:12px;font-weight:700;">
                🔗 Similar Products ({len(p['matches'])} found)
            </div>
        """, unsafe_allow_html=True)

        for m in p["matches"][:3]:
            st.markdown(f"""
            <div style="background:#f0f2f8;border-radius:8px;padding:12px 14px;
                margin-bottom:8px;display:flex;justify-content:space-between;
                align-items:center;">
                <span style="color:#1a1a2e;font-size:13px;">▸ {m['name']}</span>
                <span style="background:#fde8e6;color:#c0392b;
                    border:1px solid #e74c3c;border-radius:20px;
                    padding:2px 10px;font-size:11px;font-weight:700;">
                    {m['score']}% match
                </span>
            </div>
            """, unsafe_allow_html=True)

        if len(p["matches"]) > 3:
            with st.expander(f"🔗 Show all {len(p['matches'])} matches — click to expand"):
                for m in p["matches"][3:]:
                    st.markdown(f"""
                    <div style="background:#f0f2f8;border-radius:8px;padding:12px 14px;
                        margin-bottom:8px;display:flex;justify-content:space-between;
                        align-items:center;">
                        <span style="color:#1a1a2e;font-size:13px;">▸ {m['name']}</span>
                        <span style="background:#fde8e6;color:#c0392b;
                            border:1px solid #e74c3c;border-radius:20px;
                            padding:2px 10px;font-size:11px;font-weight:700;">
                            {m['score']}% match
                        </span>
                    </div>
                    """, unsafe_allow_html=True)

        st.markdown("""
        <div style="margin-top:20px;">
            <div style="color:#4a5568;font-size:12px;letter-spacing:1px;
                text-transform:uppercase;margin-bottom:10px;font-weight:700;">
                Score Breakdown
            </div>
        """, unsafe_allow_html=True)

        for label, val, color in [
            ("Fuzzy Match",   p["fuzzy"], "#3498db"),
            ("Text Semantic", p["text"],  "#9b59b6"),
            ("Image Visual",  p["image"], "#f39c12"),
        ]:
            st.markdown(f"""
            <div style="margin-bottom:10px;">
                <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
                    <span style="color:#4a5568;font-size:12px;">{label}</span>
                    <span style="color:#1a1a2e;font-size:12px;font-weight:700;">{val}%</span>
                </div>
                <div style="background:#e8eaf0;border-radius:4px;height:7px;overflow:hidden;">
                    <div style="width:{val}%;height:100%;background:{color};
                        border-radius:4px;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div></div>", unsafe_allow_html=True)

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("← Back to Upload", use_container_width=True,
                     key="browse_back"):
            st.session_state.screen = "upload" if st.session_state.role == "admin" else "login"
            st.rerun()
    with col2:
        if st.button("Proceed to Cleaning →", use_container_width=True,
                     key="browse_next"):
            st.session_state.screen = "clean"
            st.rerun()

# ─── SCREEN 4: CLEAN & VISUALIZE ──────────────────────────────────────────────
def screen_clean():
    section_header("✏️", "Clean Data & Visualize", step="Step 3 of 4")

    result = st.session_state.scan_result
    if not result:
        st.info("No scan results yet. Upload a CSV first.")
        if st.button("← Go to Upload"):
            st.session_state.screen = "upload"
            st.rerun()
        return

    total     = result["total_products"]
    dup_count = result["duplicate_count"]
    clean_c   = result["clean_count"]
    clusters  = st.session_state.clusters

    left, right = st.columns(2, gap="medium")
    orig_df  = st.session_state.uploaded_df
    clean_df = pd.DataFrame(st.session_state.clean_products)

    with left:
        st.markdown(f"""
        <div style="background:#ffffff;border:1px solid rgba(0,0,0,0.06);
            border-radius:14px;padding:20px;">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:14px;">
                <span style="font-size:18px;">📦</span>
                <span style="color:#1a1a2e;font-weight:700;font-size:14px;">
                    Original Dataset</span>
                <span style="background:#f0f2f8;color:#6c7a8d;
                    border:1px solid rgba(0,0,0,0.10);border-radius:20px;
                    padding:2px 10px;font-size:11px;font-weight:700;">
                    {total} products</span>
            </div>
        """, unsafe_allow_html=True)
        if orig_df is not None:
            for _, row in orig_df.head(5).iterrows():
                name = str(row.get("product_name", ""))[:40]
                st.markdown(
                    f'<div style="padding:7px 0;border-bottom:1px solid rgba(0,0,0,0.06);'
                    f'color:#6c7a8d;font-size:12px;">{name}</div>',
                    unsafe_allow_html=True)
        st.markdown(
            f'<div style="color:#6c7a8d;font-size:11px;margin-top:8px;text-align:center;">'
            f'... {total-5} more rows</div></div>',
            unsafe_allow_html=True)

    with right:
        st.markdown(f"""
        <div style="background:#ffffff;border:1px solid #27ae6044;
            border-radius:14px;padding:20px;">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:14px;">
                <span style="font-size:18px;">✨</span>
                <span style="color:#1a1a2e;font-weight:700;font-size:14px;">
                    Cleaned Dataset</span>
                <span style="background:#27ae6022;color:#27ae60;
                    border:1px solid #27ae6044;border-radius:20px;
                    padding:2px 10px;font-size:11px;font-weight:700;">
                    {clean_c} products</span>
            </div>
        """, unsafe_allow_html=True)
        if not clean_df.empty:
            for _, row in clean_df.head(5).iterrows():
                name = str(row.get("product_name", ""))[:40]
                st.markdown(
                    f'<div style="padding:7px 0;border-bottom:1px solid rgba(0,0,0,0.06);'
                    f'color:#1a1a2e;font-size:12px;">{name}</div>',
                    unsafe_allow_html=True)
        st.markdown(
            f'<div style="color:#6c7a8d;font-size:11px;margin-top:8px;text-align:center;">'
            f'... {max(0, clean_c-5)} more rows</div></div>',
            unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    stat_row([
        ("Total Products",     str(total),          "📦", "#1a1a2e"),
        ("Unique Products",    str(clean_c),         "✅", "#27ae60"),
        ("Duplicate Groups",   str(len(clusters)),   "🏷", "#3498db"),
        ("Duplicates Removed", str(dup_count),       "🗑", "#e74c3c"),
    ])

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    st.markdown(
        '<div style="color:#1a1a2e;font-weight:700;font-size:16px;margin-bottom:16px;">'
        '📊 Analysis & Visualizations</div>',
        unsafe_allow_html=True)

    chart_left, chart_right = st.columns([2, 1], gap="medium")

    with chart_left:
        cat_counts = result.get("category_counts", {"All Products": total})
        cats   = list(cat_counts.keys())[:10]
        vals   = [cat_counts[c] for c in cats]
        colors = [f"hsl({i*36},70%,55%)" for i in range(len(cats))]
        fig_bar = go.Figure(go.Bar(
            x=cats, y=vals,
            marker_color=colors,
            text=vals, textposition="outside",
            textfont=dict(color="#6c7a8d", size=11),
        ))
        fig_bar.update_layout(
            title=dict(text="Products by Category",
                       font=dict(color="#1a1a2e", size=14), x=0),
            paper_bgcolor="#ffffff", plot_bgcolor="#ffffff",
            font=dict(color="#6c7a8d", family="DM Sans"),
            xaxis=dict(tickangle=-30,
                       gridcolor="rgba(0,0,0,0.07)",
                       tickfont=dict(size=10)),
            yaxis=dict(gridcolor="rgba(0,0,0,0.07)"),
            margin=dict(t=40, b=80, l=20, r=20),
            height=280, showlegend=False,
        )
        st.plotly_chart(fig_bar, use_container_width=True,
                        config={"displayModeBar": False})

    with chart_right:
        conf    = result.get("confidence_dist", {"high": 0, "medium": 0, "low": 0})
        fig_pie = go.Figure(go.Pie(
            labels=["High (>90%)", "Medium (70-90%)", "Low (<70%)"],
            values=[conf["high"], conf["medium"], conf["low"]],
            hole=0.5,
            marker=dict(colors=["#27ae60", "#f39c12", "#e74c3c"]),
            textfont=dict(color="#1a1a2e", size=11),
        ))
        fig_pie.update_layout(
            title=dict(text="Confidence Distribution",
                       font=dict(color="#1a1a2e", size=14), x=0),
            paper_bgcolor="#ffffff", plot_bgcolor="#ffffff",
            font=dict(color="#6c7a8d", family="DM Sans"),
            margin=dict(t=40, b=20, l=20, r=20),
            height=280,
            legend=dict(font=dict(color="#6c7a8d", size=11),
                        bgcolor="rgba(0,0,0,0)"),
        )
        st.plotly_chart(fig_pie, use_container_width=True,
                        config={"displayModeBar": False})

    # ── Bottom action row — all 3 buttons on the same line ──────────────────
    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

    # Inline CSS to make the download button match stButton height/style exactly
    st.markdown("""
    <style>
    div[data-testid="stHorizontalBlock"] [data-testid="stDownloadButton"] button {
        background: #f0f2f8 !important;
        color: #1a1a2e !important;
        border: 1.5px solid rgba(0,0,0,0.18) !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-family: 'DM Sans', sans-serif !important;
        height: 38px !important;
        min-height: 38px !important;
        width: 100% !important;
        padding: 0 !important;
        margin: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        line-height: 1 !important;
    }
    div[data-testid="stHorizontalBlock"] [data-testid="stDownloadButton"] {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("← Back", use_container_width=True, key="clean_back"):
            st.session_state.screen = "browse"
            st.rerun()
    with col2:
        clean_df_dl = pd.DataFrame(st.session_state.clean_products)
        csv_out     = clean_df_dl.to_csv(index=False) if not clean_df_dl.empty else ""
        st.download_button(
            "⬇ Download Cleaned CSV",
            csv_out,
            "clean_catalog.csv",
            "text/csv",
            use_container_width=True,
            disabled=clean_df_dl.empty
        )
    with col3:
        if st.button("View Catalog →", use_container_width=True,
                     key="clean_next"):
            st.session_state.screen = "catalog"
            st.rerun()

# ─── SCREEN 5: CATALOG VIEW ───────────────────────────────────────────────────
def screen_catalog():
    section_header("🛍️", "Clean Product Catalog",
                   "Deduplicated catalog — verify merges before final export.",
                   "Step 4 of 4")

    result   = st.session_state.scan_result
    clusters = st.session_state.clusters

    if not result or not clusters:
        st.info("No scan results yet. Upload a CSV first.")
        if st.button("← Go to Upload"):
            st.session_state.screen = "upload"
            st.rerun()
        return

    total   = result["total_products"]
    clean_c = result["clean_count"]
    dup_c   = result["duplicate_count"]

    stat_row([
        ("Original",     str(total),        "📦", "#1a1a2e"),
        ("After Clean",  str(clean_c),       "✅", "#27ae60"),
        ("Removed",      str(dup_c),         "🗑", "#e74c3c"),
        ("Groups Found", str(len(clusters)), "🔗", "#3498db"),
    ])

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    ctrl1, ctrl2, ctrl3 = st.columns([2, 1.2, 1])
    with ctrl1:
        search = st.text_input("", placeholder="🔍 Search products...",
                                key="catalog_search",
                                label_visibility="collapsed")
    with ctrl2:
        sort_by = st.selectbox(
            "", ["Most Merged", "Similarity Score"],
            key="catalog_sort", label_visibility="collapsed"
        )
    with ctrl3:
        view_mode = st.radio(
            "", ["⊞ Grid", "⇄ Before/After"],
            key="catalog_view", horizontal=True,
            label_visibility="collapsed"
        )

    filtered = [
        p for p in clusters
        if not search or search.lower() in p["name"].lower()
    ]
    if sort_by == "Most Merged":
        filtered = sorted(filtered,
                          key=lambda x: x["duplicates_merged"],
                          reverse=True)
    else:
        filtered = sorted(filtered,
                          key=lambda x: x["avg_similarity"],
                          reverse=True)

    st.markdown(
        f'<p style="color:#6c7a8d;font-size:12px;margin:8px 0 16px;">'
        f'{len(filtered)} groups shown</p>',
        unsafe_allow_html=True)

    # ── GRID VIEW ─────────────────────────────────────────
    if "Grid" in view_mode:
        cols_per_row = 4
        for row_start in range(0, len(filtered), cols_per_row):
            cols = st.columns(cols_per_row, gap="medium")
            for col_idx, col in enumerate(cols):
                prod_idx = row_start + col_idx
                if prod_idx >= len(filtered):
                    break
                p = filtered[prod_idx]
                orig_idx = clusters.index(p) if p in clusters else prod_idx
                with col:
                    badge_html = confidence_badge(p["avg_similarity"])
                    st.markdown(f"""
                    <div style="background:#ffffff;border:1px solid rgba(0,0,0,0.08);
                        border-radius:14px;overflow:hidden;">
                        <div style="position:relative;">
                            <img src="{img_url(orig_idx, p['name'])}"
                                style="width:100%;height:150px;object-fit:cover;display:block;" />
                            <div style="position:absolute;top:8px;right:8px;
                                background:#e74c3c;color:#fff;border-radius:20px;
                                padding:3px 10px;font-size:11px;font-weight:700;">
                                {p['duplicates_merged']} merged
                            </div>
                            <div style="position:absolute;top:8px;left:8px;">
                                {badge_html}
                            </div>
                        </div>
                        <div style="padding:14px 16px;">
                            <div style="font-size:14px;font-weight:700;color:#1a1a2e;
                                margin-bottom:8px;line-height:1.4;min-height:40px;">
                                {p['name']}
                            </div>
                            <div style="display:flex;justify-content:space-between;
                                align-items:center;margin-bottom:10px;">
                                <div style="font-size:13px;color:#6c7a8d;">
                                    Avg: {p['avg_similarity']}%
                                </div>
                                <span style="color:#f39c12;font-size:12px;">
                                    {stars(p['avg_similarity'])}
                                </span>
                            </div>
                            <div style="border-top:1px solid rgba(0,0,0,0.08);
                                padding-top:10px;display:flex;
                                justify-content:space-between;align-items:center;">
                                <span style="font-size:10px;color:#6c7a8d;">{p['id']}</span>
                                <span style="font-size:11px;color:#e74c3c;font-weight:700;">
                                    View Merges →
                                </span>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    if st.button("View Merges",
                                 key=f"view_{p['id']}",
                                 use_container_width=True):
                        st.session_state.drawer_product = p
                        st.rerun()

    # ── BEFORE / AFTER VIEW ───────────────────────────────
    else:
        for i, p in enumerate(filtered):
            orig_idx = clusters.index(p) if p in clusters else i
            st.markdown(f"""
            <div style="background:#ffffff;border:1px solid rgba(0,0,0,0.08);
                border-radius:14px;overflow:hidden;margin-bottom:16px;">
                <div style="display:flex;align-items:center;gap:14px;
                    padding:16px 20px;background:#27ae600f;
                    border-bottom:1px solid #27ae6033;">
                    <img src="{img_url(orig_idx, p['name'])}"
                        style="width:52px;height:52px;object-fit:cover;
                        border-radius:8px;border:1.5px solid #27ae6044;
                        flex-shrink:0;" />
                    <div style="flex:1;">
                        <div style="font-size:10px;color:#27ae60;
                            text-transform:uppercase;letter-spacing:1px;
                            font-weight:700;margin-bottom:3px;">
                            ✅ CLEAN PRODUCT — KEPT
                        </div>
                        <div style="font-weight:700;font-size:15px;color:#1a1a2e;">
                            {p['name']}
                        </div>
                        <div style="font-size:12px;color:#6c7a8d;margin-top:3px;">
                            Avg Similarity: {p['avg_similarity']}%
                            &nbsp;·&nbsp;
                            Confidence: {p['confidence'].upper()}
                        </div>
                    </div>
                    <div style="background:#e74c3c;color:#fff;border-radius:20px;
                        padding:4px 14px;font-size:12px;font-weight:700;
                        flex-shrink:0;">
                        {p['duplicates_merged']} removed
                    </div>
                </div>
                <div style="text-align:center;padding:6px;color:#6c7a8d;
                    font-size:11px;letter-spacing:2px;background:#e8eaf0;">
                    ↓ &nbsp; DUPLICATES REMOVED &nbsp; ↓
                </div>
            </div>
            """, unsafe_allow_html=True)

            if p["originals"]:
                dup_cols = st.columns(min(len(p["originals"]), 3), gap="small")
                for j, orig in enumerate(p["originals"]):
                    with dup_cols[j % 3]:
                        st.markdown(f"""
                        <div style="background:#f8f9fc;border-left:3px solid #e74c3c;
                            padding:12px 14px;border-radius:0 8px 8px 0;
                            margin-bottom:8px;">
                            <div style="display:flex;justify-content:space-between;
                                margin-bottom:4px;">
                                <span style="font-size:10px;color:#e74c3c;
                                    font-weight:700;text-transform:uppercase;">
                                    🗑 Removed #{j+1}
                                </span>
                            </div>
                            <div style="font-weight:600;font-size:13px;
                                color:#1a1a2e;margin-bottom:6px;">
                                {orig['name']}
                            </div>
                            <div style="display:flex;justify-content:space-between;
                                align-items:center;">
                                <span style="font-size:12px;color:#4a5568;">
                                    Score: {orig['final_score']}%
                                </span>
                                {reason_badge(orig['reason'])}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

            st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    # ── DRAWER ────────────────────────────────────────────
    if st.session_state.drawer_product:
        p        = st.session_state.drawer_product
        orig_idx = clusters.index(p) if p in clusters else 0

        st.markdown("---")
        st.markdown(f"""
        <div style="background:#ffffff;border:1px solid rgba(0,0,0,0.12);
            border-radius:16px;padding:28px;margin-top:8px;
            box-shadow:0 4px 20px rgba(0,0,0,0.08);">
            <div style="color:#e74c3c;font-size:10px;letter-spacing:2px;
                text-transform:uppercase;margin-bottom:4px;">Merge Details</div>
            <div style="color:#1a1a2e;font-weight:700;font-size:16px;
                font-family:'EB Garamond',serif;">{p['name']}</div>
            <img src="{img_url(orig_idx, p['name'])}"
                style="width:100%;max-height:200px;object-fit:cover;
                border-radius:10px;margin:16px 0;" />
            <div style="font-size:11px;color:#27ae60;text-transform:uppercase;
                font-weight:700;letter-spacing:1px;margin-bottom:12px;">
                ✅ Final Clean Product
            </div>
        """, unsafe_allow_html=True)

        d_col1, d_col2 = st.columns(2)
        detail_items = [
            ("Product ID",        p["id"]),
            ("Confidence",        p["confidence"].upper()),
            ("Avg Similarity",    f"{p['avg_similarity']}%"),
            ("Duplicates Merged", str(p["duplicates_merged"])),
            ("Fuzzy Score",       f"{p['fuzzy']}%"),
            ("Text Score",        f"{p['text']}%"),
        ]
        for i, (label, val) in enumerate(detail_items):
            with (d_col1 if i % 2 == 0 else d_col2):
                st.markdown(f"""
                <div style="background:#f0f2f8;border-radius:8px;
                    padding:10px 12px;margin-bottom:10px;">
                    <div style="font-size:10px;color:#4a5568;
                        text-transform:uppercase;letter-spacing:1px;">
                        {label}
                    </div>
                    <div style="font-weight:700;font-size:13px;
                        color:#1a1a2e;margin-top:3px;">{val}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown(f"""
        </div>
        <div style="background:#ffffff;border:1px solid rgba(0,0,0,0.12);
            border-radius:16px;padding:24px;margin-top:12px;
            box-shadow:0 4px 20px rgba(0,0,0,0.08);">
            <div style="font-size:11px;color:#e74c3c;text-transform:uppercase;
                font-weight:700;letter-spacing:1px;margin-bottom:16px;">
                🗑 Removed Duplicates ({p['duplicates_merged']})
            </div>
        """, unsafe_allow_html=True)

        for j, orig in enumerate(p["originals"]):
            st.markdown(f"""
            <div style="border-left:3px solid #e74c3c;padding-left:14px;
                margin-bottom:16px;">
                <div style="font-size:12px;font-weight:700;color:#1a1a2e;
                    margin-bottom:4px;">#{j+1} — {orig['name']}</div>
                <div style="display:flex;justify-content:space-between;
                    align-items:center;">
                    <span style="font-size:12px;color:#4a5568;">
                        Score: {orig['final_score']}%
                    </span>
                    {reason_badge(orig['reason'])}
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        if st.button("✕ Close", key="close_drawer"):
            st.session_state.drawer_product = None
            st.rerun()

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="btn-ghost">', unsafe_allow_html=True)
        if st.button("← Back to Clean", use_container_width=True,
                     key="catalog_back"):
            st.session_state.screen = "clean"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        clean_df_export = pd.DataFrame(st.session_state.clean_products)
        if not clean_df_export.empty:
            st.markdown('<div class="btn-green">', unsafe_allow_html=True)
            csv_out = clean_df_export.to_csv(index=False)
            st.download_button(
                "⬇ Export Final Catalog",
                csv_out,
                "final_clean_catalog.csv",
                "text/csv",
                use_container_width=True
            )
            st.markdown("</div>", unsafe_allow_html=True)

# ─── MAIN ROUTER ──────────────────────────────────────────────────────────────
# ─── MAIN ROUTER ──────────────────────────────────────────────────────────────
def main():
    screen = st.session_state.get("screen", "login")

    if screen == "login":
        screen_login()
        return

    render_topnav()

    if screen == "upload":
        screen_upload()
    elif screen == "browse":
        screen_browse()
    elif screen == "clean":
        screen_clean()
    elif screen == "catalog":
        screen_catalog()

if __name__ == "__main__":
    main()

# # Terminal 1 — Start FastAPI
# cd similara
# uvicorn api.main:app --reload --port 8000

# # Terminal 2 — Start Streamlit
# cd similara
# streamlit run ui/app.py