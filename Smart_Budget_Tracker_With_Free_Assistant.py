
import streamlit as st
import pandas as pd
from datetime import date, datetime
import sqlite3
from pathlib import Path
import io
import re
import calendar

# =====================================
# PAGE CONFIGURATION
# =====================================

st.set_page_config(
    page_title="Smart Budget Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================
# CUSTOM CSS
# =====================================

st.markdown("""
<style>
    .stApp {
        background-image: linear-gradient(rgba(249, 247, 255, 0.76), rgba(248, 245, 255, 0.83)), url("data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNjAwIiBoZWlnaHQ9IjEwMDAiIHZpZXdCb3g9IjAgMCAxNjAwIDEwMDAiPjxkZWZzPjxsaW5lYXJHcmFkaWVudCBpZD0iYmciIHgyPSIxIiB5Mj0iMSI+PHN0b3Agc3RvcC1jb2xvcj0iI2U3ZGNmZiIvPjxzdG9wIG9mZnNldD0iLjQ4IiBzdG9wLWNvbG9yPSIjYjliMWVkIi8+PHN0b3Agb2Zmc2V0PSIxIiBzdG9wLWNvbG9yPSIjNzY2NGM3Ii8+PC9saW5lYXJHcmFkaWVudD48cmFkaWFsR3JhZGllbnQgaWQ9Imdsb3ciPjxzdG9wIHN0b3AtY29sb3I9IiNmZmYiIHN0b3Atb3BhY2l0eT0iLjgiLz48c3RvcCBvZmZzZXQ9IjEiIHN0b3AtY29sb3I9IiNmZmYiIHN0b3Atb3BhY2l0eT0iMCIvPjwvcmFkaWFsR3JhZGllbnQ+PGxpbmVhckdyYWRpZW50IGlkPSJnb2xkIiB4Mj0iLjMiIHkyPSIxIj48c3RvcCBzdG9wLWNvbG9yPSIjZmZlNWEwIi8+PHN0b3Agb2Zmc2V0PSIxIiBzdG9wLWNvbG9yPSIjZDZhMzViIi8+PC9saW5lYXJHcmFkaWVudD48ZmlsdGVyIGlkPSJibHVyIj48ZmVHYXVzc2lhbkJsdXIgc3RkRGV2aWF0aW9uPSIzNCIvPjwvZmlsdGVyPjwvZGVmcz48cmVjdCB3aWR0aD0iMTYwMCIgaGVpZ2h0PSIxMDAwIiBmaWxsPSJ1cmwoI2JnKSIvPjxjaXJjbGUgY3g9IjI2MCIgY3k9IjE0MCIgcj0iMzYwIiBmaWxsPSJ1cmwoI2dsb3cpIi8+PGNpcmNsZSBjeD0iMTM3MCIgY3k9Ijg1MCIgcj0iNDQwIiBmaWxsPSIjYjhhM2Y4IiBvcGFjaXR5PSIuNTUiIGZpbHRlcj0idXJsKCNibHVyKSIvPjxwYXRoIGQ9Ik0wIDc2MFEyODAgNjIwIDU0MCA3OTBUMTA5MCA3MDBUMTYwMCA3MzBWMTAwMEgwWiIgZmlsbD0iIzhmN2NkNCIgb3BhY2l0eT0iLjMiLz48ZyBvcGFjaXR5PSIuMjMiIGZpbGw9IiNmZmYiPjxyZWN0IHg9IjkzMCIgeT0iNDQwIiB3aWR0aD0iNjgiIGhlaWdodD0iMjQwIiByeD0iMTUiLz48cmVjdCB4PSIxMDMwIiB5PSIzNTAiIHdpZHRoPSI2OCIgaGVpZ2h0PSIzMzAiIHJ4PSIxNSIvPjxyZWN0IHg9IjExMzAiIHk9IjI2NSIgd2lkdGg9IjY4IiBoZWlnaHQ9IjQxNSIgcng9IjE1Ii8+PHJlY3QgeD0iMTIzMCIgeT0iMTkwIiB3aWR0aD0iNjgiIGhlaWdodD0iNDkwIiByeD0iMTUiLz48L2c+PHBhdGggZD0iTTg0MCA1NDBROTYwIDQ5MCAxMDUwIDQxMFQxMjAwIDMwMFQxNDIwIDEyNSIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjZmZmIiBzdHJva2Utd2lkdGg9IjIwIiBvcGFjaXR5PSIuMjciIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIvPjxwYXRoIGQ9Im0xMzcwIDEzNyA2MS0yMi0xMyA2NSIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjZmZmIiBzdHJva2Utd2lkdGg9IjIwIiBvcGFjaXR5PSIuMyIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIi8+PGcgb3BhY2l0eT0iLjYiPjxlbGxpcHNlIGN4PSIyNDAiIGN5PSI4NTAiIHJ4PSIxODAiIHJ5PSIyOCIgZmlsbD0iIzY2NTJhYSIgb3BhY2l0eT0iLjIiLz48ZyBmaWxsPSJ1cmwoI2dvbGQpIiBzdHJva2U9IiNjNThmNGMiIHN0cm9rZS13aWR0aD0iMyI+PHJlY3QgeD0iMTEwIiB5PSI3NTAiIHdpZHRoPSIxMTUiIGhlaWdodD0iMjIiIHJ4PSIxMCIvPjxyZWN0IHg9IjExMCIgeT0iNzI3IiB3aWR0aD0iMTE1IiBoZWlnaHQ9IjIyIiByeD0iMTAiLz48cmVjdCB4PSIxMTAiIHk9IjcwNCIgd2lkdGg9IjExNSIgaGVpZ2h0PSIyMiIgcng9IjEwIi8+PHJlY3QgeD0iMjQwIiB5PSI3NzAiIHdpZHRoPSIxMTUiIGhlaWdodD0iMjIiIHJ4PSIxMCIvPjxyZWN0IHg9IjI0MCIgeT0iNzQ3IiB3aWR0aD0iMTE1IiBoZWlnaHQ9IjIyIiByeD0iMTAiLz48cmVjdCB4PSIyNDAiIHk9IjcyNCIgd2lkdGg9IjExNSIgaGVpZ2h0PSIyMiIgcng9IjEwIi8+PHJlY3QgeD0iMjQwIiB5PSI3MDEiIHdpZHRoPSIxMTUiIGhlaWdodD0iMjIiIHJ4PSIxMCIvPjxyZWN0IHg9IjI0MCIgeT0iNjc4IiB3aWR0aD0iMTE1IiBoZWlnaHQ9IjIyIiByeD0iMTAiLz48L2c+PGNpcmNsZSBjeD0iMzcwIiBjeT0iNjEwIiByPSI3MiIgZmlsbD0idXJsKCNnb2xkKSIgc3Ryb2tlPSIjZmNlM2ExIiBzdHJva2Utd2lkdGg9IjkiLz48dGV4dCB4PSIzNzAiIHk9IjYzNSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSI2NiIgZm9udC1mYW1pbHk9IkFyaWFsIiBmb250LXdlaWdodD0iYm9sZCIgZmlsbD0iI2FkN2EzOCI+JDwvdGV4dD48L2c+PGcgb3BhY2l0eT0iLjE1IiBmaWxsPSJub25lIiBzdHJva2U9IiNmZmYiIHN0cm9rZS13aWR0aD0iNCI+PGNpcmNsZSBjeD0iMTQxMCIgY3k9IjM0MCIgcj0iMTMwIi8+PGNpcmNsZSBjeD0iMTQxMCIgY3k9IjM0MCIgcj0iOTQiLz48Y2lyY2xlIGN4PSIxNDEwIiBjeT0iMzQwIiByPSI1NyIvPjwvZz48L3N2Zz4=");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #241a57 0%, #4d2e9d 100%);
    }

    [data-testid="stSidebar"] * {
        color: white;
    }

    .main-title {
        font-size: 32px;
        font-weight: 700;
        color: #123F3B;
    }

    .subtitle {
        color: #64748B;
        font-size: 15px;
    }

    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.87);
        backdrop-filter: blur(12px);
        padding: 20px;
        border-radius: 14px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 3px 12px rgba(18, 63, 59, 0.05);
    }

    .section-title {
        color: #123F3B;
        font-size: 21px;
        font-weight: 600;
    }

    div.stButton > button,
    div[data-testid="stFormSubmitButton"] > button {
        border-radius: 10px;
        min-height: 44px;
        font-weight: 600;
    }

    .login-brand {
        color: #087F73;
        font-size: 17px;
        font-weight: 750;
        letter-spacing: 0.2px;
        margin-bottom: 34px;
    }

    .login-eyebrow {
        color: #087F73;
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 12px;
    }

    .login-hero-title {
        color: #142E2B;
        font-size: clamp(38px, 5vw, 62px);
        line-height: 1.08;
        font-weight: 750;
        letter-spacing: -2px;
        margin: 0 0 18px 0;
    }

    .login-hero-title span {
        color: #078477;
    }

    .login-hero-copy {
        color: #64748B;
        font-size: 16px;
        line-height: 1.7;
        max-width: 520px;
    }

    .login-art {
        margin-top: 30px;
        min-height: 220px;
        border-radius: 28px;
        background: linear-gradient(135deg, #E4F5F1 0%, #F5F7E9 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 16px;
        overflow: hidden;
        position: relative;
    }

    .login-art .wallet {
        font-size: 104px;
        filter: drop-shadow(0 12px 12px rgba(18, 63, 59, 0.14));
        z-index: 1;
    }

    .login-art .coin {
        font-size: 48px;
        position: relative;
        top: -38px;
    }

    .login-art .piggy {
        font-size: 76px;
        position: relative;
        top: 38px;
    }

    .login-feature {
        color: #47615D;
        font-size: 13px;
        margin-top: 18px;
    }

    .login-card-title {
        color: #173B36;
        font-size: 27px;
        font-weight: 750;
        margin-bottom: 4px;
    }

    .login-card-copy {
        color: #71817E;
        font-size: 14px;
        margin-bottom: 22px;
    }

    [data-testid="stForm"] {
        background: rgba(255, 255, 255, 0.91);
        backdrop-filter: blur(14px);
        border: 1px solid rgba(255,255,255,.75);
        border-radius: 20px;
        padding: 26px;
        box-shadow: 0 12px 40px rgba(18, 63, 59, 0.08);
    }

    [data-testid="stTextInput"] label {
        color: #36514C;
        font-weight: 600;
    }


    /* Keep content readable over the finance background */
    [data-testid="stAppViewContainer"] > .main {
        background: transparent;
    }
    [data-testid="stDataFrame"],
    [data-testid="stAlert"],
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 14px;
    }
    [data-testid="stHeader"] {
        background: rgba(248, 245, 255, 0.40);
        backdrop-filter: blur(8px);
    }
    [data-testid="stSidebar"] {
        backdrop-filter: blur(14px);
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        color: white;
    }

    @media (max-width: 700px) {
        .login-brand {
            margin-bottom: 20px;
        }
        .login-hero-title {
            font-size: 39px;
            letter-spacing: -1px;
        }
        .login-art {
            min-height: 150px;
        }
        .login-art .wallet {
            font-size: 75px;
        }
        .login-art .coin {
            font-size: 34px;
        }
        .login-art .piggy {
            font-size: 55px;
        }
    }

/* ===== VIOLET GLASS DESIGN: LOGIN + ALL PAGES ===== */
:root { --violet:#6236e9; --deep:#171044; --ink:#21174e; }
.stApp { color:var(--ink); }
[data-testid="stAppViewContainer"] .block-container { padding-top:2.3rem; padding-bottom:3rem; max-width:1320px; }
h1,h2,h3,h4,p, [data-testid="stMarkdownContainer"] { color:var(--ink); }
.main-title { color:#1b124e; font-size:clamp(30px,3.4vw,44px); font-weight:800; letter-spacing:-1.3px; }
.subtitle { color:#514777; font-size:15px; margin-bottom:14px; }
.section-title { color:#21144e; }
[data-testid="stSidebar"] { background:linear-gradient(170deg,#1d164c,#34207b 72%,#5935bb) !important; border-right:1px solid rgba(255,255,255,.15); }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span { color:#fff !important; }
[data-testid="stSidebar"] [role="radiogroup"] label { border-radius:13px; padding:9px 10px; transition:background .2s; }
[data-testid="stSidebar"] [role="radiogroup"] label:hover { background:rgba(255,255,255,.12); }
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) { background:rgba(132,94,255,.52); }
[data-testid="stSidebar"] button { color:#fff !important; background:linear-gradient(100deg,#7048ef,#5932c5) !important; border:1px solid rgba(255,255,255,.2) !important; }
[data-testid="stMetric"] { background:rgba(255,255,255,.84) !important; border:1px solid rgba(255,255,255,.9) !important; box-shadow:0 12px 36px rgba(59,36,133,.12) !important; border-radius:21px !important; backdrop-filter:blur(16px); padding:23px !important; }
[data-testid="stMetricLabel"] *,[data-testid="stMetricValue"] * { color:#21174e !important; }
[data-testid="stMetricValue"] { font-weight:800; }
[data-testid="stForm"] { background:rgba(255,255,255,.88) !important; border:1px solid rgba(255,255,255,.95) !important; box-shadow:0 18px 55px rgba(56,28,119,.15) !important; border-radius:24px !important; backdrop-filter:blur(20px); }
[data-testid="stForm"] label,[data-testid="stForm"] p { color:#30245c !important; }
[data-testid="stFormSubmitButton"] button[kind="primary"],button[kind="primary"] { background:linear-gradient(105deg,#9562ff,#5226dd) !important; color:#fff !important; border:none !important; box-shadow:0 8px 19px rgba(90,47,205,.26); }
[data-testid="stFormSubmitButton"] button { background:linear-gradient(105deg,#8d5df4,#572bd6) !important; color:#fff !important; border:none !important; }
[data-testid="stFormSubmitButton"] button:hover,button[kind="primary"]:hover { filter:brightness(1.06); }
[data-testid="stTextInput"] input,[data-testid="stNumberInput"] input,[data-testid="stDateInput"] input { background:rgba(255,255,255,.94); border-radius:11px; }
[data-testid="stDataFrame"], [data-testid="stAlert"] { border-radius:17px; overflow:hidden; }
[data-testid="stProgress"] > div > div { background:linear-gradient(90deg,#9562ff,#5929d9); }
hr { border-color:rgba(87,51,171,.15) !important; }
.login-brand { color:#30206f; font-weight:850; font-size:19px; margin-bottom:23px; }
.login-eyebrow { color:#6033d4; font-weight:800; }
.login-hero-title { color:#1a1150; font-size:clamp(40px,5vw,65px); line-height:1.07; }
.login-hero-title span { color:#6538e8; }
.login-hero-copy { color:#463b78; font-size:17px; max-width:570px; }
.login-art { background:linear-gradient(90deg,rgba(63,34,134,.05),rgba(71,39,140,.05)),url("data:image/webp;base64,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") center 63% / cover; min-height:275px; border:1px solid rgba(255,255,255,.65); box-shadow:0 14px 45px rgba(62,37,138,.15); }
.login-art .wallet,.login-art .coin,.login-art .piggy { display:none; }
.login-feature { color:#322361; font-size:14px; font-weight:650; background:rgba(255,255,255,.62); padding:13px 17px; border-radius:15px; }
.login-card-title { color:#24155b; font-size:34px; font-weight:800; text-align:center; margin-top:9px; }
.login-card-copy { color:#5c5285; font-size:15px; text-align:center; margin-bottom:20px; }
.login-lock { width:76px; height:76px; margin:0 auto 12px; display:grid; place-items:center; border-radius:50%; background:linear-gradient(135deg,#a27bff,#5022d5); box-shadow:0 10px 28px rgba(91,49,204,.24); color:white; font-size:34px; }
.login-demo { background:rgba(232,222,255,.8); border-radius:13px; padding:14px; color:#2e1e68; text-align:center; font-size:14px; margin-top:14px; }
.login-footer { color:#483d7d; text-align:center; font-size:12px; margin-top:28px; }
@media(max-width:700px){.login-art{min-height:190px}.login-brand{margin-bottom:15px}.login-hero-title{font-size:42px}[data-testid="stAppViewContainer"] .block-container{padding-top:1.2rem}}

</style>
""", unsafe_allow_html=True)


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Demo credentials
USERNAME = "admin"
PASSWORD = "admin123"

if not st.session_state.logged_in:

    st.markdown(
        """
        <div class="login-brand">◈ &nbsp; SMART BUDGET TRACKER</div>
        """,
        unsafe_allow_html=True
    )

    hero_col, login_col = st.columns([1.15, 0.85], gap="large")

    with hero_col:
        st.markdown(
            """
            <div class="login-eyebrow">PERSONAL FINANCE, MADE SIMPLE</div>
            <div class="login-hero-title">
                Smart Budget<br>
                <span>Tracker.</span>
            </div>
            <div class="login-hero-copy">
                Manage your money. Control your spending. Build better financial habits with your personal finance dashboard.
            </div>
            <div class="login-art">

            </div>
            <div class="login-feature">
                ✓ Track expenses &nbsp;&nbsp; ✓ Set monthly budgets<br>
                ✓ Visualize spending &nbsp;&nbsp; ✓ Reach your goals
            </div>
            """,
            unsafe_allow_html=True
        )

    with login_col:
        st.write("")
        st.write("")
        st.markdown(
            """
            <div class="login-lock">🔒</div>
            <div class="login-card-title">Welcome Back!</div>
            <div class="login-card-copy">
                Log in to continue managing your money.
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.form("login_form"):
            username = st.text_input(
                "Username",
                placeholder="Enter your username"
            )

            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password"
            )

            login_button = st.form_submit_button(
                "Log In",
                use_container_width=True,
                type="primary"
            )

            if login_button:
                if username == USERNAME and password == PASSWORD:
                    st.session_state.logged_in = True
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Incorrect username or password.")

        st.markdown('<div class="login-demo">Demo Credentials<br><b>Username:</b> admin &nbsp; | &nbsp; <b>Password:</b> admin123</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-footer">💜 Smart Budget Tracker v2.0</div>', unsafe_allow_html=True)

    st.stop()



# =====================================
# LOCAL SQLITE STORAGE
# =====================================
# Database lives beside this Python file. Keep this file and .db together.
DB_PATH = Path(__file__).resolve().parent / "smart_budget_tracker.db"

def connect_db():
    conn = sqlite3.connect(str(DB_PATH), timeout=15)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with connect_db() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL CHECK(type IN ('Income','Expense')),
            amount REAL NOT NULL CHECK(amount > 0),
            category TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            date TEXT NOT NULL
        )""")
        conn.execute("""CREATE TABLE IF NOT EXISTS budgets (
            month TEXT PRIMARY KEY, amount REAL NOT NULL DEFAULT 0
        )""")
        conn.execute("""CREATE TABLE IF NOT EXISTS savings_goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            target REAL NOT NULL CHECK(target > 0),
            saved REAL NOT NULL DEFAULT 0 CHECK(saved >= 0),
            deadline TEXT
        )""")

def db_rows(sql, args=()):
    with connect_db() as conn:
        return [dict(r) for r in conn.execute(sql, args).fetchall()]

def db_write(sql, args=()):
    with connect_db() as conn:
        conn.execute(sql, args)

def transaction_frame(items):
    return pd.DataFrame([{
        "ID": t["id"], "Date": t["date"], "Type": t["type"],
        "Category": t["category"], "Description": t["description"],
        "Amount (RM)": round(t["amount"], 2)
    } for t in items], columns=["ID", "Date", "Type", "Category", "Description", "Amount (RM)"])

def money(amount):
    return f"RM {amount:,.2f}"

init_db()

# =====================================
# FREE RULE-BASED FINANCIAL ASSISTANT
# =====================================
def assistant_reply(question, all_transactions, month_budgets, goals, reference_date):
    """Answer supported budgeting questions using local data; no external API."""
    q = question.lower().strip()
    if not q:
        return "Type a question about your income, expenses, budget, or savings goals."

    month = reference_date.strftime("%Y-%m")
    explicit_month = re.search(r"\b(20\d{2})-(0[1-9]|1[0-2])\b", q)
    if explicit_month:
        month = explicit_month.group(0)
    elif "last month" in q or "previous month" in q:
        year, mon = reference_date.year, reference_date.month - 1
        if mon == 0:
            year, mon = year - 1, 12
        month = f"{year:04d}-{mon:02d}"
    elif "this month" not in q:
        for m in range(1, 13):
            if re.search(r"\b" + calendar.month_name[m].lower() + r"\b", q):
                year_match = re.search(r"\b20\d{2}\b", q)
                year = int(year_match.group()) if year_match else reference_date.year
                month = f"{year:04d}-{m:02d}"
                break

    month_rows = [t for t in all_transactions if t["date"].startswith(month)]
    earned = sum(float(t["amount"]) for t in month_rows if t["type"] == "Income")
    spent = sum(float(t["amount"]) for t in month_rows if t["type"] == "Expense")
    net = earned - spent
    limit = float(month_budgets.get(month, 0))
    categories = {}
    for t in month_rows:
        if t["type"] == "Expense":
            categories[t["category"]] = categories.get(t["category"], 0) + float(t["amount"])
    label = f"{calendar.month_name[int(month[5:])]} {month[:4]}"

    if any(x in q for x in ("help", "what can you do", "example", "how to use")):
        return ("I can answer questions about monthly income, expenses, balance, budgets, "
                "top spending categories, savings goals, and basic savings tips. "
                "Try: 'How much did I spend this month?', 'Top category last month', "
                "'Budget status', 'Savings goals', or 'Expenses in 2026-10'.")
    if any(x in q for x in ("goal", "saving target", "savings progress")):
        if not goals:
            return "You have no savings goals yet. Create one on the Savings Goals page."
        parts = []
        for goal in goals[:8]:
            saved, target = float(goal["saved"]), float(goal["target"])
            parts.append(f"• {goal['name']}: {money(saved)} of {money(target)} ({min(saved/target*100, 100):.0f}% complete)")
        more = f"\n…and {len(goals)-8} more goals." if len(goals) > 8 else ""
        return "Your savings goals:\n" + "\n".join(parts) + more
    if any(x in q for x in ("budget", "limit", "overspend", "alert")):
        if limit <= 0:
            return f"No budget has been set for {label}. Set one in Budget Management."
        used = spent / limit * 100
        status = "over budget" if used > 100 else "at your limit" if used >= 100 else "close to your limit" if used >= 80 else "within your budget"
        return (f"{label}: Budget {money(limit)}, spent {money(spent)} ({used:.1f}%). "
                f"You are {status}. Remaining budget: {money(limit-spent)}.")
    if any(x in q for x in ("category", "categories", "most spend", "biggest", "highest", "where", "breakdown")):
        if not categories:
            return f"There are no recorded expenses for {label}."
        named = next((name for name in categories if name.lower() in q), None)
        if named:
            return f"You spent {money(categories[named])} on {named} in {label}."
        ordered = sorted(categories.items(), key=lambda x: x[1], reverse=True)
        return f"Expense categories for {label}:\n" + "\n".join(f"• {k}: {money(v)}" for k,v in ordered[:8])
    if any(x in q for x in ("tip", "advice", "suggest", "save more", "reduce spending", "improve")):
        if not month_rows:
            return "Start by recording your income and expenses. Then I can suggest which categories to review."
        if categories:
            biggest = max(categories, key=categories.get)
            detail = f"Your highest expense category this month is {biggest} ({money(categories[biggest])}). Review it for optional costs. "
        else:
            detail = "You have not recorded expenses this month. "
        return detail + ("Your spending is above your recorded income; consider reviewing recurring expenses. " if net < 0 else "") + "Set a realistic monthly budget and track a savings goal. These are general budgeting tips, not personalized investment advice."
    if any(x in q for x in ("balance", "left", "remaining", "net", "profit")):
        return f"Your recorded net balance for {label} is {money(net)} (income {money(earned)} minus expenses {money(spent)}). This is not your bank balance."
    if any(x in q for x in ("income", "earned", "received", "salary")):
        return f"Your recorded income for {label} is {money(earned)}."
    if any(x in q for x in ("expense", "spent", "spending", "cost", "paid")):
        return f"Your recorded expenses for {label} are {money(spent)} across {sum(t['type']=='Expense' for t in month_rows)} transactions."
    if any(x in q for x in ("hello", "hi", "hey")):
        return "Hello! Ask me about your budget, income, expenses, savings goals, or spending categories."
    return ("I couldn't match that question to a supported topic. Try asking 'How much did I spend this month?', "
            "'What's my balance?', 'Budget status', or 'Show my savings goals'.")

# =====================================
# SIDEBAR
# =====================================
with st.sidebar:
    st.title("👛 Smart Budget Tracker")
    st.caption("Personal Finance Management")
    st.divider()
    menu = st.radio("MAIN MENU", [
        "Dashboard", "Add Income", "Add Expense", "Budget Management",
        "Transaction History", "Savings Goals", "Monthly Reports", "Download Reports", "🤖 Budget Assistant"
    ])
    st.divider()
    st.caption("💾 Data saved locally • SQLite")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

now = date.today()
current_month = now.strftime("%Y-%m")
transactions = db_rows("SELECT * FROM transactions ORDER BY date DESC, id DESC")
month_transactions = [t for t in transactions if t["date"].startswith(current_month)]
income = sum(t["amount"] for t in month_transactions if t["type"] == "Income")
expenses = sum(t["amount"] for t in month_transactions if t["type"] == "Expense")
balance = income - expenses
budget_rows = db_rows("SELECT amount FROM budgets WHERE month=?", (current_month,))
budget = float(budget_rows[0]["amount"]) if budget_rows else 0.0

st.markdown('<div class="main-title">Smart Budget Tracker</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Your money, your goals, your future.</div>', unsafe_allow_html=True)
st.write("")

if menu == "Dashboard":
    st.markdown("## 📊 Financial Overview")
    st.caption(now.strftime("%B %Y") + " • Monthly financial summary")
    a, b, c = st.columns(3)
    a.metric("💵 Total Income", money(income))
    b.metric("💸 Total Expenses", money(expenses))
    c.metric("💰 Remaining Balance", money(balance))
    st.markdown("### 🎯 Budget Progress")
    if budget > 0:
        percent = expenses / budget * 100
        st.progress(min(expenses / budget, 1.0))
        st.caption(f"{percent:.1f}% used • {money(budget - expenses)} remaining")
        if percent >= 100:
            st.error("🚨 You have reached or exceeded your monthly budget!")
        elif percent >= 80:
            st.warning("⚠️ You have used at least 80% of your monthly budget.")
        elif percent >= 50:
            st.info("You have used at least half your monthly budget.")
        else:
            st.success("You're comfortably within your monthly budget.")
    else:
        st.info("Set a monthly budget in Budget Management to enable alerts.")
    st.markdown("### 📈 Spending Analysis")
    categories = {}
    for t in month_transactions:
        if t["type"] == "Expense":
            categories[t["category"]] = categories.get(t["category"], 0) + t["amount"]
    left, right = st.columns(2)
    if categories:
        chart_df = pd.DataFrame({"Category": list(categories), "Amount": list(categories.values())})
        with left:
            st.markdown("#### Spending Breakdown")
            import plotly.express as px
            fig = px.pie(chart_df, names="Category", values="Amount", hole=.52,
                         color_discrete_sequence=px.colors.sequential.Purples_r)
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="#352365", margin=dict(l=10,r=10,t=10,b=10))
            st.plotly_chart(fig, use_container_width=True)
        with right:
            st.markdown("#### Category Comparison")
            st.bar_chart(chart_df.set_index("Category"), color="#8559df")
    else:
        st.info("Add an expense to see your spending charts.")
    st.markdown("### 🕒 Recent Transactions")
    if transactions:
        st.dataframe(transaction_frame(transactions[:5]), use_container_width=True, hide_index=True)
    else:
        st.info("No transactions yet. Start by adding income or expenses.")
    goals = db_rows("SELECT * FROM savings_goals ORDER BY id DESC")
    if goals:
        st.markdown("### 🌟 Savings Goals")
        for goal in goals[:3]:
            st.write(f"**{goal['name']}** — {money(goal['saved'])} / {money(goal['target'])}")
            st.progress(min(goal["saved"] / goal["target"], 1.0))

elif menu in ("Add Income", "Add Expense"):
    kind = "Income" if menu == "Add Income" else "Expense"
    st.markdown(f"## {'💵' if kind == 'Income' else '💸'} Add {kind}")
    cats = (["Salary", "Allowance", "Scholarship", "Business", "Other"] if kind == "Income"
            else ["Food", "Transportation", "Shopping", "Bills", "Education", "Entertainment", "Health", "Other"])
    with st.form(f"new_{kind.lower()}"):
        amount = st.number_input("Amount (RM)", min_value=0.01, step=1.0, format="%.2f")
        category = st.selectbox("Category", cats)
        description = st.text_input("Description", placeholder="What was this for?")
        when = st.date_input("Transaction Date", value=now)
        if st.form_submit_button(f"➕ Save {kind}", use_container_width=True):
            db_write("INSERT INTO transactions(type,amount,category,description,date) VALUES(?,?,?,?,?)",
                     (kind, float(amount), category, description.strip(), when.isoformat()))
            st.success(f"{kind} saved successfully!")
            st.rerun()

elif menu == "Budget Management":
    st.markdown("## 🎯 Budget Management")
    st.caption("Budgets are stored separately for each month.")
    chosen_month = st.date_input("Select a month", value=now, key="budget_month").strftime("%Y-%m")
    existing = db_rows("SELECT amount FROM budgets WHERE month=?", (chosen_month,))
    saved_budget = float(existing[0]["amount"]) if existing else 0.0
    with st.form(f"budget_{chosen_month}"):
        new_budget = st.number_input("Monthly Budget (RM)", min_value=0.0,
                                     value=saved_budget, step=50.0, format="%.2f")
        if st.form_submit_button("Save Monthly Budget", use_container_width=True):
            db_write("INSERT INTO budgets(month,amount) VALUES(?,?) ON CONFLICT(month) DO UPDATE SET amount=excluded.amount",
                     (chosen_month, float(new_budget)))
            st.success("Budget saved!")
            st.rerun()
    chosen_expenses = sum(t["amount"] for t in transactions if t["type"] == "Expense" and t["date"].startswith(chosen_month))
    a, b, c = st.columns(3)
    a.metric("Monthly Budget", money(saved_budget))
    b.metric("Expenses", money(chosen_expenses))
    c.metric("Remaining", money(saved_budget - chosen_expenses))
    if saved_budget > 0:
        st.progress(min(chosen_expenses / saved_budget, 1.0))

elif menu == "Transaction History":
    st.markdown("## 📋 Transaction History")
    st.caption("Search, filter, edit, and delete your saved transactions.")
    search = st.text_input("🔎 Search description or category")
    f1, f2, f3 = st.columns(3)
    type_filter = f1.selectbox("Transaction type", ["All", "Income", "Expense"])
    category_filter = f2.selectbox("Category", ["All"] + sorted({t["category"] for t in transactions}))
    month_filter = f3.selectbox("Month", ["All"] + sorted({t["date"][:7] for t in transactions}, reverse=True))
    filtered = [t for t in transactions
                if (type_filter == "All" or t["type"] == type_filter)
                and (category_filter == "All" or t["category"] == category_filter)
                and (month_filter == "All" or t["date"].startswith(month_filter))
                and (not search or search.lower() in (t["description"] + " " + t["category"]).lower())]
    st.caption(f"Showing {len(filtered)} of {len(transactions)} transactions")
    st.dataframe(transaction_frame(filtered), use_container_width=True, hide_index=True)
    st.download_button("⬇️ Download filtered transactions (CSV)",
                       transaction_frame(filtered).to_csv(index=False).encode("utf-8-sig"),
                       "filtered_transactions.csv", "text/csv", use_container_width=True)
    if filtered:
        labels = {t["id"]: f"#{t['id']} • {t['date']} • {t['type']} • {t['category']} • {money(t['amount'])}" for t in filtered}
        chosen_id = st.selectbox("Choose a transaction to edit or delete", list(labels), format_func=lambda i: labels[i])
        selected = next(t for t in filtered if t["id"] == chosen_id)
        with st.expander("✏️ Edit selected transaction", expanded=False):
            with st.form(f"edit_{chosen_id}"):
                new_type = st.selectbox("Type", ["Income", "Expense"], index=0 if selected["type"] == "Income" else 1)
                new_amount = st.number_input("Amount (RM)", min_value=0.01, value=float(selected["amount"]), format="%.2f")
                new_category = st.text_input("Category", value=selected["category"])
                new_description = st.text_input("Description", value=selected["description"])
                new_date = st.date_input("Date", value=date.fromisoformat(selected["date"]))
                if st.form_submit_button("💾 Save Changes", use_container_width=True):
                    if not new_category.strip():
                        st.error("Category cannot be empty.")
                    else:
                        db_write("UPDATE transactions SET type=?,amount=?,category=?,description=?,date=? WHERE id=?",
                                 (new_type, float(new_amount), new_category.strip(), new_description.strip(), new_date.isoformat(), chosen_id))
                        st.success("Transaction updated!")
                        st.rerun()
        with st.expander("🗑️ Delete selected transaction"):
            confirm = st.checkbox("I understand this will permanently delete the selected transaction", key=f"confirm_{chosen_id}")
            if st.button("Delete Transaction", disabled=not confirm, use_container_width=True):
                db_write("DELETE FROM transactions WHERE id=?", (chosen_id,))
                st.success("Transaction deleted.")
                st.rerun()

elif menu == "Savings Goals":
    st.markdown("## 🌟 Savings Goals")
    st.caption("Track savings goals manually. Goal contributions are not deducted from your income balance.")
    with st.expander("➕ Create a new goal", expanded=True):
        with st.form("new_goal"):
            name = st.text_input("Goal name", placeholder="e.g. New laptop")
            target = st.number_input("Target amount (RM)", min_value=1.0, step=50.0)
            use_deadline = st.checkbox("Add a target date")
            deadline = st.date_input("Target date", value=now) if use_deadline else None
            if st.form_submit_button("Create Goal", use_container_width=True):
                if not name.strip():
                    st.error("Please enter a goal name.")
                else:
                    db_write("INSERT INTO savings_goals(name,target,saved,deadline) VALUES(?,?,?,?)",
                             (name.strip(), float(target), 0.0, deadline.isoformat() if deadline else None))
                    st.success("Savings goal created!")
                    st.rerun()
    goals = db_rows("SELECT * FROM savings_goals ORDER BY id DESC")
    if not goals:
        st.info("Create your first savings goal above.")
    for goal in goals:
        with st.container(border=True):
            st.markdown(f"### 🎯 {goal['name']}")
            st.write(f"Saved **{money(goal['saved'])}** of **{money(goal['target'])}**")
            st.progress(min(goal["saved"] / goal["target"], 1.0))
            if goal["deadline"]:
                st.caption(f"Target date: {goal['deadline']}")
            if goal["saved"] >= goal["target"]:
                st.success("Goal reached! 🎉")
            with st.form(f"update_goal_{goal['id']}"):
                new_saved = st.number_input("Total saved so far (RM)", min_value=0.0,
                                            value=float(goal["saved"]), step=10.0, format="%.2f")
                if st.form_submit_button("Update Savings"):
                    db_write("UPDATE savings_goals SET saved=? WHERE id=?", (float(new_saved), goal["id"]))
                    st.rerun()
            if st.button("Delete Goal", key=f"delete_goal_{goal['id']}"):
                db_write("DELETE FROM savings_goals WHERE id=?", (goal["id"],))
                st.rerun()

elif menu == "Monthly Reports":
    st.markdown("## 📅 Monthly Reports")
    st.caption("Compare your income, expenses, and budget month by month.")
    months = sorted({t["date"][:7] for t in transactions} | {current_month}, reverse=True)
    selected_month = st.selectbox("Choose month", months)
    mt = [t for t in transactions if t["date"].startswith(selected_month)]
    mi = sum(t["amount"] for t in mt if t["type"] == "Income")
    me = sum(t["amount"] for t in mt if t["type"] == "Expense")
    a, b, c = st.columns(3)
    a.metric("Income", money(mi))
    b.metric("Expenses", money(me))
    c.metric("Net Balance", money(mi-me))
    report_categories = {}
    for t in mt:
        if t["type"] == "Expense":
            report_categories[t["category"]] = report_categories.get(t["category"], 0) + t["amount"]
    if report_categories:
        st.markdown("### Expenses by category")
        st.bar_chart(pd.DataFrame({"Category": list(report_categories), "Amount": list(report_categories.values())}).set_index("Category"), color="#8559df")
    st.markdown("### Monthly Trends")
    all_months = sorted({t["date"][:7] for t in transactions} | {current_month})
    trends = [{"Month": m,
               "Income": sum(t["amount"] for t in transactions if t["date"].startswith(m) and t["type"] == "Income"),
               "Expenses": sum(t["amount"] for t in transactions if t["date"].startswith(m) and t["type"] == "Expense")}
              for m in all_months]
    st.line_chart(pd.DataFrame(trends).set_index("Month"))
    st.markdown("### Transactions for selected month")
    st.dataframe(transaction_frame(mt), use_container_width=True, hide_index=True)
    st.download_button("⬇️ Download monthly transactions (CSV)",
                       transaction_frame(mt).to_csv(index=False).encode("utf-8-sig"),
                       f"budget_report_{selected_month}.csv", "text/csv", use_container_width=True)

elif menu == "🤖 Budget Assistant":
    st.markdown("## 🤖 Smart Budget Assistant")
    st.caption("Free, private, rule-based help using your locally saved data. No API key or internet needed.")
    st.info("This assistant follows predefined rules. It cannot understand every question or make changes to your records.")
    st.markdown("**Try a question:**")
    suggestions = ["How much did I spend this month?", "What is my balance?", "Budget status", "Top spending category", "Savings goals", "Give me savings tips"]
    cols = st.columns(3)
    picked = None
    for i, suggestion in enumerate(suggestions):
        if cols[i % 3].button(suggestion, key=f"assistant_suggestion_{i}", use_container_width=True):
            picked = suggestion
    if "budget_chat" not in st.session_state:
        st.session_state.budget_chat = [{"role": "assistant", "content": "Hello! Ask me about your recorded finances, budgets, or savings goals."}]
    if st.button("🧹 Clear conversation", key="clear_budget_chat"):
        st.session_state.budget_chat = [{"role": "assistant", "content": "Conversation cleared. What would you like to know?"}]
        st.rerun()
    for message in st.session_state.budget_chat:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    prompt = st.chat_input("Ask about income, expenses, budget, or goals...")
    question = picked or prompt
    if question:
        budgets = {b["month"]: b["amount"] for b in db_rows("SELECT month, amount FROM budgets")}
        goals = db_rows("SELECT * FROM savings_goals ORDER BY id DESC")
        answer = assistant_reply(question, transactions, budgets, goals, now)
        st.session_state.budget_chat.extend([
            {"role": "user", "content": question},
            {"role": "assistant", "content": answer},
        ])
        st.rerun()

elif menu == "Download Reports":
    st.markdown("## 📥 Download Reports")
    st.caption("Export your financial records to CSV files for Excel or Google Sheets.")
    st.download_button("⬇️ All Transactions (CSV)",
                       transaction_frame(transactions).to_csv(index=False).encode("utf-8-sig"),
                       "all_transactions.csv", "text/csv", use_container_width=True)
    goals = db_rows("SELECT * FROM savings_goals ORDER BY id")
    st.download_button("⬇️ Savings Goals (CSV)",
                       pd.DataFrame(goals, columns=["id","name","target","saved","deadline"]).to_csv(index=False).encode("utf-8-sig"),
                       "savings_goals.csv", "text/csv", use_container_width=True)
    budgets = db_rows("SELECT * FROM budgets ORDER BY month DESC")
    st.download_button("⬇️ Monthly Budgets (CSV)",
                       pd.DataFrame(budgets, columns=["month","amount"]).to_csv(index=False).encode("utf-8-sig"),
                       "monthly_budgets.csv", "text/csv", use_container_width=True)
    st.info("Your database is stored in smart_budget_tracker.db next to this Python file. Back up that file to preserve your records.")

st.divider()
st.caption("Smart Budget Tracker • Personal Finance Management • Local data storage")
