
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import altair as alt
from datetime import date
import sqlite3
from pathlib import Path
import base64

from budget_assistant import reply as assistant_reply
from deployment_config import load_settings
from receipt_ui import clear_receipt_session, render_receipt_scanner

# =====================================
# PAGE CONFIGURATION
# =====================================

st.set_page_config(
    page_title="Smart Budget Tracker",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="auto"
)

# =====================================
# SHARED GLASS THEME — LOGIN + EVERY PAGE
# =====================================
APP_DIR = Path(__file__).resolve().parent

@st.cache_data(show_spinner=False)
def glass_theme_assets(css_revision, background_revision):
    """Embed local assets so the theme also works without an internet connection."""
    css = (APP_DIR / "assets" / "glass-theme.css").read_text()
    texture = base64.b64encode((APP_DIR / "assets" / "graphite-texture.png").read_bytes()).decode("ascii")
    return css.replace("__BACKGROUND_IMAGE__", f"data:image/png;base64,{texture}")

theme_css = glass_theme_assets(
    (APP_DIR / "assets" / "glass-theme.css").stat().st_mtime_ns,
    (APP_DIR / "assets" / "graphite-texture.png").stat().st_mtime_ns,
)
st.markdown(f"<style>{theme_css}</style>", unsafe_allow_html=True)
with st.container(key="theme-sync"):
    components.html((APP_DIR / "assets" / "theme-sync.html").read_text(), height=0)


def glass_chart(chart):
    """Keep chart canvases transparent over the shared frosted surface."""
    chart = (chart.properties(background="transparent", height=280)
             .configure_view(strokeOpacity=0)
             .configure_axis(domainOpacity=0, tickOpacity=0, labelPadding=8))
    st.altair_chart(chart, use_container_width=True, theme="streamlit")


def spending_bar_chart(frame):
    glass_chart(alt.Chart(frame).mark_bar(color="#b39a7a", cornerRadiusTopLeft=4,
                                         cornerRadiusTopRight=4).encode(
        x=alt.X("Category:N", title=None, axis=alt.Axis(labelAngle=-25)),
        y=alt.Y("Amount:Q", title="Amount (RM)"),
        tooltip=["Category:N", alt.Tooltip("Amount:Q", format=",.2f")],
    ))


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

try:
    settings = load_settings(APP_DIR)
except ValueError as exc:
    st.error(str(exc))
    st.stop()

if settings.ephemeral_storage:
    st.warning("This deployment uses temporary storage. Records may disappear when the server restarts or scales. Use it only for testing.")

if not st.session_state.logged_in:

    st.markdown(
        """
        <div class="login-brand">◈ &nbsp; SMART BUDGET TRACKER</div>
        """,
        unsafe_allow_html=True
    )

    hero_col, login_col = st.columns([1.15, 0.85], gap="large")

    with hero_col, st.container(key="login-intro"):
        st.markdown(
            """
            <div class="login-eyebrow">YOUR FINANCES, REIMAGINED</div>
            <div class="login-hero-title">
                Smart Budget<br>
                <span>Tracker.</span>
            </div>
            <div class="login-hero-copy">
                A clearer perspective on your money. Track every move, understand your spending, and shape your financial future.
            </div>
            <div class="login-art" aria-hidden="true">
                <div class="login-art-label">A LITTLE CLARITY. EVERY DAY.</div>
                <div class="login-art-heading">Make room for what matters.</div>
                <svg viewBox="0 0 500 140" fill="none" preserveAspectRatio="none">
                    <defs><linearGradient id="balance-fill" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#655744" stop-opacity=".24"/><stop offset="1" stop-color="#655744" stop-opacity="0"/></linearGradient></defs>
                    <path d="M0 110L45 94L90 103L135 68L180 78L225 50L270 58L315 28L360 45L405 15L450 25L500 5V140H0Z" fill="url(#balance-fill)"/>
                    <path class="login-chart-line" d="M0 110L45 94L90 103L135 68L180 78L225 50L270 58L315 28L360 45L405 15L450 25L500 5" stroke="currentColor" stroke-width="2.5" stroke-linejoin="round"/>
                </svg>
            </div>
            <div class="login-feature">
                ✓ Track expenses &nbsp;&nbsp; ✓ Set monthly budgets<br>
                ✓ Visualize spending &nbsp;&nbsp; ✓ Reach your goals
            </div>
            """,
            unsafe_allow_html=True
        )

    with login_col, st.container(key="login-panel"):
        st.write("")
        st.write("")
        st.markdown(
            """
            <div class="login-lock" aria-hidden="true"><svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><rect x="5" y="10" width="14" height="11" rx="3"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/><path d="M12 14v3"/></svg></div>
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
                if settings.authenticate(username, password):
                    st.session_state.logged_in = True
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Incorrect username or password.")

        if settings.demo_login:
            st.markdown('<div class="login-demo">Demo Credentials<br><b>Username:</b> admin &nbsp; | &nbsp; <b>Password:</b> admin123</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-footer">Smart Budget Tracker · v2.0</div>', unsafe_allow_html=True)

    st.stop()



# =====================================
# LOCAL SQLITE STORAGE
# =====================================
# Hosted deployments point to a persistent disk; local use keeps its existing file.
DB_PATH = settings.database_path
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

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

def save_transaction(kind, amount, category, description, when):
    db_write("INSERT INTO transactions(type,amount,category,description,date) VALUES(?,?,?,?,?)",
             (kind, float(amount), category, description.strip(), when.isoformat()))

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
# SIDEBAR
# =====================================
with st.sidebar:
    st.markdown("""<div class="sb-brand"><span class="sb-brand-icon"><svg viewBox="0 0 24 24" width="25" height="25" fill="none" stroke="currentColor" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><path d="m7 16 4-5 4 3 5-7"/></svg></span><span>SMART<span class="sb-brand-accent">BUDGET</span><small>FINANCIAL WORKSPACE</small></span></div>""", unsafe_allow_html=True)
    st.markdown('<p class="sb-brand-caption">Personal Finance Management</p>', unsafe_allow_html=True)
    st.divider()
    menu = st.radio("MAIN MENU", [
        "Dashboard", "Add Income", "Add Expense", "Budget Management",
        "Transaction History", "Savings Goals", "Monthly Reports", "Download Reports", "Budget Assistant"
    ])
    st.divider()
    st.caption("Private records · SQLite")
    if st.button("Sign out", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.pop("budget_chat", None)
        st.session_state.pop("budget_assistant_context", None)
        clear_receipt_session()
        st.session_state.pop("receipt_saved_notice", None)
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
    st.markdown("""<div class="sb-hero"><div class="sb-eyebrow"><span class="sb-dot"></span> PERSONAL FINANCE / OVERVIEW</div><div class="sb-hero-title">Clarity for every<br><em>financial decision.</em></div><div class="sb-hero-copy">Track your money, understand your spending, and move toward your goals with confidence.</div><div class="sb-hero-art" aria-hidden="true"><div class="sb-orbit sb-orbit-one"></div><div class="sb-orbit sb-orbit-two"></div><div class="sb-orbit sb-orbit-three"></div><div class="sb-center-mark">S</div></div></div>""", unsafe_allow_html=True)
    st.markdown("## Financial overview")
    st.caption(now.strftime("%B %Y") + " • Monthly financial summary")
    a, b, c = st.columns(3)
    a.metric("Total income", money(income))
    b.metric("Total expenses", money(expenses))
    c.metric("Net balance", money(balance))
    st.markdown("### Monthly budget")
    if budget > 0:
        percent = expenses / budget * 100
        st.progress(min(expenses / budget, 1.0))
        st.caption(f"{percent:.1f}% used • {money(budget - expenses)} remaining")
        if percent >= 100:
            st.error("You have reached or exceeded your monthly budget!")
        elif percent >= 80:
            st.warning("You have used at least 80% of your monthly budget.")
        elif percent >= 50:
            st.info("You have used at least half your monthly budget.")
        else:
            st.success("You're comfortably within your monthly budget.")
    else:
        st.info("Set a monthly budget in Budget Management to enable alerts.")
    st.markdown("### Spending insights")
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
                         color_discrete_sequence=["#494235", "#94806a", "#baa58b", "#d1c2a8", "#79816b", "#a5ab94", "#c7b6a6", "#80766b"])
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=10,r=10,t=10,b=10))
            st.plotly_chart(fig, use_container_width=True)
        with right:
            st.markdown("#### Category Comparison")
            spending_bar_chart(chart_df)
    else:
        st.info("Add an expense to see your spending charts.")
    st.markdown("### Recent activity")
    if transactions:
        st.dataframe(transaction_frame(transactions[:5]), use_container_width=True, hide_index=True)
    else:
        st.info("No transactions yet. Start by adding income or expenses.")
    goals = db_rows("SELECT * FROM savings_goals ORDER BY id DESC")
    if goals:
        st.markdown("### Savings goals")
        for goal in goals[:3]:
            st.write(f"**{goal['name']}** — {money(goal['saved'])} / {money(goal['target'])}")
            st.progress(min(goal["saved"] / goal["target"], 1.0))

elif menu in ("Add Income", "Add Expense"):
    kind = "Income" if menu == "Add Income" else "Expense"
    st.markdown(f"## Add {kind}")
    cats = (["Salary", "Allowance", "Scholarship", "Business", "Other"] if kind == "Income"
            else ["Food", "Transportation", "Shopping", "Bills", "Education", "Entertainment", "Health", "Other"])
    entry_method = st.radio("Entry method", ["Manual entry", "Scan receipt"], horizontal=True) if kind == "Expense" else "Manual entry"
    if entry_method == "Scan receipt":
        render_receipt_scanner(transactions, lambda **expense: save_transaction("Expense", **expense))
    else:
        with st.form(f"new_{kind.lower()}"):
            amount = st.number_input("Amount (RM)", min_value=0.01, step=1.0, format="%.2f")
            category = st.selectbox("Category", cats)
            description = st.text_input("Description", placeholder="What was this for?")
            when = st.date_input("Transaction Date", value=now)
            if st.form_submit_button(f"Save {kind}", use_container_width=True):
                save_transaction(kind, amount, category, description, when)
                st.success(f"{kind} saved successfully!")
                st.rerun()

elif menu == "Budget Management":
    st.markdown("## Budget management")
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
    st.markdown("## Transaction history")
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
    st.markdown("## Savings goals")
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
            st.markdown(f"###  {goal['name']}")
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
    st.markdown("## Monthly reports")
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
        spending_bar_chart(pd.DataFrame({"Category": list(report_categories), "Amount": list(report_categories.values())}))
    st.markdown("### Monthly trends")
    all_months = sorted({t["date"][:7] for t in transactions} | {current_month})
    trends = [{"Month": m,
               "Income": sum(t["amount"] for t in transactions if t["date"].startswith(m) and t["type"] == "Income"),
               "Expenses": sum(t["amount"] for t in transactions if t["date"].startswith(m) and t["type"] == "Expense")}
              for m in all_months]
    trend_frame = pd.DataFrame(trends).melt(id_vars="Month", var_name="Type", value_name="Amount")
    glass_chart(alt.Chart(trend_frame).mark_line(point=True, strokeWidth=2.5).encode(
        x=alt.X("Month:O", title=None, axis=alt.Axis(labelAngle=-25)),
        y=alt.Y("Amount:Q", title="Amount (RM)"),
        color=alt.Color("Type:N", scale=alt.Scale(domain=["Income", "Expenses"],
                                                range=["#494235", "#a38e76"]), title=None),
        tooltip=["Month:O", "Type:N", alt.Tooltip("Amount:Q", format=",.2f")],
    ))
    st.markdown("### Transactions for selected month")
    st.dataframe(transaction_frame(mt), use_container_width=True, hide_index=True)
    st.download_button("⬇️ Download monthly transactions (CSV)",
                       transaction_frame(mt).to_csv(index=False).encode("utf-8-sig"),
                       f"budget_report_{selected_month}.csv", "text/csv", use_container_width=True)

elif menu == "Budget Assistant":
    st.markdown("## Budget assistant")
    st.caption("Free, private, rule-based help using your locally saved data. No API key or internet needed.")
    st.info("Ask about your records or work through a calculation. I remember follow-up details in this conversation and ask for missing numbers. Local rules handle supported topics; records stay unchanged.")
    st.markdown("**Try a question:**")
    suggestions = ["How much did I spend this month?", "Compare this month with last month", "How much can I spend per day?", "Save RM 3,000 in 6 months", "Can I afford RM 250?", "What can you do?"]
    cols = st.columns(3)
    picked = None
    for i, suggestion in enumerate(suggestions):
        if cols[i % 3].button(suggestion, key=f"assistant_suggestion_{i}", use_container_width=True):
            picked = suggestion
    if "budget_chat" not in st.session_state:
        st.session_state.budget_chat = [{"role": "assistant", "content": "Hi! Tell me what you want to work out. I can review spending, compare months, or calculate a savings plan, purchase scenario, or loan payment."}]
    if "budget_assistant_context" not in st.session_state:
        st.session_state.budget_assistant_context = {}
    if st.button("🧹 Clear conversation", key="clear_budget_chat"):
        st.session_state.budget_assistant_context = {}
        st.session_state.budget_chat = [{"role": "assistant", "content": "Conversation cleared. What would you like to know?"}]
        st.rerun()
    for message in st.session_state.budget_chat:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    prompt = st.chat_input("Ask a question, give me numbers, or follow up on a calculation...")
    question = picked or prompt
    if question:
        budgets = {b["month"]: b["amount"] for b in db_rows("SELECT month, amount FROM budgets")}
        goals = db_rows("SELECT * FROM savings_goals ORDER BY id DESC")
        answer = assistant_reply(question, transactions, budgets, goals, now,
                                 context=st.session_state.budget_assistant_context)
        st.session_state.budget_chat.extend([
            {"role": "user", "content": question},
            {"role": "assistant", "content": answer},
        ])
        st.rerun()

elif menu == "Download Reports":
    st.markdown("## Download reports")
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
