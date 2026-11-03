
import streamlit as st
import pandas as pd
from datetime import date

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
        background-color: #F5F7FB;
    }

    [data-testid="stSidebar"] {
        background-color: #172554;
    }

    [data-testid="stSidebar"] * {
        color: white;
    }

    .main-title {
        font-size: 32px;
        font-weight: 700;
        color: #172554;
    }

    .subtitle {
        color: #64748B;
        font-size: 15px;
    }

    div[data-testid="stMetric"] {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.04);
    }

    .section-title {
        color: #172554;
        font-size: 21px;
        font-weight: 600;
    }

    div.stButton > button {
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# =====================================
# SESSION STATE
# =====================================

if "transactions" not in st.session_state:
    st.session_state.transactions = []

if "monthly_budget" not in st.session_state:
    st.session_state.monthly_budget = 0.0
    # =====================================
# LOGIN SYSTEM
# =====================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Demo credentials
USERNAME = "admin"
PASSWORD = "admin123"

if not st.session_state.logged_in:

    st.markdown("""
        <div style="text-align:center; padding:35px 0 10px;">
            <h1 style="color:#2563EB;">💰 Smart Budget Tracker</h1>
            <p style="color:gray;">
                Personal Finance Management System
            </p>
        </div>
    """, unsafe_allow_html=True)

    left, center, right = st.columns([1, 1.2, 1])

    with center:

        st.markdown("### Welcome Back!")
        st.write("Please login to continue.")

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
                "Login",
                use_container_width=True
            )

            if login_button:

                if username == USERNAME and password == PASSWORD:

                    st.session_state.logged_in = True

                    st.success("Login successful!")

                    st.rerun()

                else:

                    st.error(
                        "Incorrect username or password."
                    )

        st.caption(
            "Demo Username: admin | Password: admin123"
        )

    st.stop()

# =====================================
# SIDEBAR
# =====================================

with st.sidebar:

    st.title("💰 Smart Budget")
    st.caption("Personal Finance Management")

    st.divider()

    menu = st.radio(
        "MAIN MENU",
        [
            "Dashboard",
            "Add Income",
            "Add Expense",
            "Budget Management",
            "Transaction History"
        ]
    )

    st.divider()

    st.caption("Smart Budget Tracker v2.0")
    st.divider()

    if st.button("🚪 Logout", use_container_width=True):

        st.session_state.logged_in = False

        st.rerun()

# =====================================
# MONTHLY CALCULATIONS
# =====================================

today = date.today()

monthly_transactions = [
    t for t in st.session_state.transactions
    if t["date"].month == today.month
    and t["date"].year == today.year
]

total_income = sum(
    t["amount"] for t in monthly_transactions
    if t["type"] == "Income"
)

total_expenses = sum(
    t["amount"] for t in monthly_transactions
    if t["type"] == "Expense"
)

balance = total_income - total_expenses

budget = st.session_state.monthly_budget

remaining_budget = budget - total_expenses

# =====================================
# APPLICATION HEADER
# =====================================

st.markdown(
    '<div class="main-title">Smart Budget Tracker</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Manage your money. Control your spending. '
    'Build better financial habits.</div>',
    unsafe_allow_html=True
)

st.write("")

# =====================================
# DASHBOARD
# =====================================

if menu == "Dashboard":

    st.markdown("## 📊 Financial Overview")

    st.caption(
        today.strftime("%B %Y") +
        " | Your monthly financial summary"
    )

    # Summary Cards

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "💵 Total Income",
        f"RM {total_income:,.2f}"
    )

    col2.metric(
        "💸 Total Expenses",
        f"RM {total_expenses:,.2f}"
    )

    col3.metric(
        "💰 Remaining Balance",
        f"RM {balance:,.2f}"
    )

    st.write("")

    # Budget Progress

    st.markdown("### 🎯 Monthly Budget")

    if budget > 0:

        budget_col1, budget_col2 = st.columns(2)

        with budget_col1:
            st.metric(
                "Monthly Limit",
                f"RM {budget:,.2f}"
            )

        with budget_col2:
            st.metric(
                "Budget Remaining",
                f"RM {remaining_budget:,.2f}"
            )

        progress = min(total_expenses / budget, 1.0)

        st.progress(progress)

        percentage = (total_expenses / budget) * 100

        st.caption(
            f"You have used {percentage:.1f}% of your monthly budget."
        )

        if remaining_budget < 0:
            st.error("Warning: You have exceeded your budget!")

        else:
            st.success("You are within your monthly budget.")

    else:
        st.info("Set your monthly budget to monitor your spending.")

    st.divider()

    # Financial Charts

    st.markdown("### 📈 Financial Analysis")

    chart_col1, chart_col2 = st.columns(2)

    expense_data = {}

    for t in monthly_transactions:

        if t["type"] == "Expense":

            category = t["category"]

            expense_data[category] = (
                expense_data.get(category, 0) + t["amount"]
            )

    with chart_col1:

         st.markdown("#### 🥧 Spending Breakdown")

         if expense_data:

            pie_df = pd.DataFrame(
            list(expense_data.items()),
            columns=["Category", "Amount"]
        )

            st.plotly_chart(
            {
                "data": [{
                    "type": "pie",
                    "labels": pie_df["Category"],
                    "values": pie_df["Amount"],
                    "hole": 0.45,
                    "textinfo": "label+percent",
                    "hovertemplate":
                        "%{label}<br>RM %{value:.2f}"
                        "<extra></extra>"
                }],
                "layout": {
                    "showlegend": True,
                    "height": 350,
                    "margin": {
                        "l": 10,
                        "r": 10,
                        "t": 20,
                        "b": 10
                    }
                }
            },
            use_container_width=True
        )

         else:
            st.info("Add expenses to display the pie chart.")
    
            
            

        
        

    with chart_col2:

        st.markdown("#### Spending Comparison")

        if expense_data:

            bar_df = pd.DataFrame(
                list(expense_data.items()),
                columns=["Category", "Amount"]
            )

            st.bar_chart(
                bar_df,
                x="Category",
                y="Amount"
            )

        else:
            st.info("Add expenses to view the comparison.")

    st.divider()

    # Recent Transactions

    st.markdown("### 🕒 Recent Transactions")

    recent = st.session_state.transactions[-5:]

    if recent:

        recent_data = []

        for t in reversed(recent):

            recent_data.append({
                "Date": t["date"].strftime("%d %b %Y"),
                "Type": t["type"],
                "Category": t["category"],
                "Description": t["description"],
                "Amount (RM)": t["amount"]
            })

        st.dataframe(
            pd.DataFrame(recent_data),
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("No transactions recorded yet.")

# =====================================
# ADD INCOME
# =====================================

elif menu == "Add Income":

    st.markdown("## 💵 Add New Income")

    st.write("Record money received.")

    with st.form("income_form"):

        amount = st.number_input(
            "Income Amount (RM)",
            min_value=0.01,
            step=10.0
        )

        category = st.selectbox(
            "Income Category",
            [
                "Salary",
                "Allowance",
                "Scholarship",
                "Business",
                "Other"
            ]
        )

        description = st.text_input(
            "Description",
            placeholder="Example: Monthly allowance"
        )

        transaction_date = st.date_input(
            "Transaction Date",
            value=date.today()
        )

        submit = st.form_submit_button(
            "➕ Add Income",
            use_container_width=True
        )

        if submit:

            st.session_state.transactions.append({
                "type": "Income",
                "amount": amount,
                "category": category,
                "description": description,
                "date": transaction_date
            })

            st.success("Income added successfully!")
            st.rerun()

# =====================================
# ADD EXPENSE
# =====================================

elif menu == "Add Expense":

    st.markdown("## 💸 Add New Expense")

    st.write("Record your daily spending.")

    with st.form("expense_form"):

        amount = st.number_input(
            "Expense Amount (RM)",
            min_value=0.01,
            step=1.0
        )

        category = st.selectbox(
            "Expense Category",
            [
                "Food",
                "Transportation",
                "Shopping",
                "Bills",
                "Education",
                "Entertainment",
                "Health",
                "Other"
            ]
        )

        description = st.text_input(
            "Description",
            placeholder="Example: Lunch"
        )

        transaction_date = st.date_input(
            "Transaction Date",
            value=date.today()
        )

        submit = st.form_submit_button(
            "➕ Add Expense",
            use_container_width=True
        )

        if submit:

            st.session_state.transactions.append({
                "type": "Expense",
                "amount": amount,
                "category": category,
                "description": description,
                "date": transaction_date
            })

            st.success("Expense added successfully!")
            st.rerun()

# =====================================
# BUDGET MANAGEMENT
# =====================================

elif menu == "Budget Management":

    st.markdown("## 🎯 Budget Management")

    st.write("Set your monthly spending limit.")

    with st.form("budget_form"):

        new_budget = st.number_input(
            "Monthly Budget (RM)",
            min_value=0.0,
            value=float(st.session_state.monthly_budget),
            step=50.0
        )

        submit = st.form_submit_button(
            "Save Budget",
            use_container_width=True
        )

        if submit:

            st.session_state.monthly_budget = new_budget

            st.success("Budget saved successfully!")
            st.rerun()

    st.divider()

    st.markdown("### Current Budget Information")

    st.metric(
        "Monthly Budget",
        f"RM {budget:,.2f}"
    )

    st.metric(
        "Current Expenses",
        f"RM {total_expenses:,.2f}"
    )

    if budget > 0:

        st.metric(
            "Remaining Budget",
            f"RM {remaining_budget:,.2f}"
        )

# =====================================
# TRANSACTION HISTORY
# =====================================

elif menu == "Transaction History":

    st.markdown("## 📋 Transaction History")

    transactions = st.session_state.transactions

    if transactions:

        history_data = []

        for index, t in enumerate(transactions):

            history_data.append({
                "Number": index + 1,
                "Date": t["date"].strftime("%d %b %Y"),
                "Type": t["type"],
                "Category": t["category"],
                "Description": t["description"],
                "Amount (RM)": t["amount"]
            })

        st.dataframe(
            pd.DataFrame(history_data),
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.markdown("### 🗑️ Delete Transaction")

        selected = st.selectbox(
            "Select Transaction",
            range(len(transactions)),
            format_func=lambda i:
                f"{i + 1}. {transactions[i]['type']} - "
                f"RM {transactions[i]['amount']:.2f}"
        )

        if st.button(
            "Delete Selected Transaction",
            use_container_width=True
        ):

            st.session_state.transactions.pop(selected)

            st.success("Transaction deleted successfully!")
            st.rerun()

    else:

        st.info("No transaction history available.")

# =====================================
# FOOTER
# =====================================

st.divider()

st.caption(
    "Smart Budget Tracker System | "
    "Personal Finance Management Application"
)


