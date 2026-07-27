import io
import os
from datetime import datetime, date
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from fpdf import FPDF

DATA_FILE = "transactions.csv"
BUDGET_FILE = "budgets.csv"
GOALS_FILE = "goals.csv"

COLUMNS = ["ID", "Type", "Amount", "Category", "Date", "Time", "Description"]
BUDGET_COLUMNS = ["Category", "Limit"]
GOALS_COLUMNS = ["ID", "GoalName", "TargetAmount", "CurrentAmount", "CreatedDate"]

INCOME_CATEGORIES = ["Salary", "Freelance", "Business", "Investment", "Gift", "Other Income"]
EXPENSE_CATEGORIES = [
    "Food & Dining", "Transportation", "Shopping", "Entertainment",
    "Bills & Utilities", "Health & Fitness", "Education", "Rent",
    "Groceries", "Travel", "Other Expense",
]

BLUE = "#3B82F6"
BLUE_DARK = "#1D4ED8"
BLUE_LIGHT = "#93C5FD"
BLACK = "#000000"
CARD_BG = "#0E121A"
CARD_BG_2 = "#141A24"
BORDER = "#1E2733"
TEXT_MUTED = "#9CA3AF"
GREEN = "#22C55E"
RED = "#EF4444"
AMBER = "#F59E0B"

st.set_page_config(
    page_title="Personal Finance Dashboard",
    page_icon="icon/budget.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {BLACK};
        color: #F4F4F5;
    }}

    section[data-testid="stSidebar"] {{
        background-color: #050709;
        border-right: 1px solid {BORDER};
    }}
    section[data-testid="stSidebar"] * {{
        color: #F4F4F5;
    }}

    h1, h2, h3, h4 {{
        color: #F4F4F5 !important;
        font-weight: 700;
    }}

    div[data-testid="stMetric"] {{
        background: linear-gradient(145deg, {CARD_BG}, {CARD_BG_2});
        border: 1px solid {BORDER};
        border-radius: 14px;
        padding: 18px 20px;
        box-shadow: 0 4px 14px rgba(59, 130, 246, 0.10);
    }}
    div[data-testid="stMetricLabel"] {{
        color: {TEXT_MUTED} !important;
    }}
    div[data-testid="stMetricValue"] {{
        color: {BLUE_LIGHT} !important;
    }}

    .stButton > button, .stDownloadButton > button {{
        background: linear-gradient(135deg, {BLUE}, {BLUE_DARK});
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.55em 1.4em;
        font-weight: 600;
        transition: all 0.2s ease;
    }}
    .stButton > button:hover, .stDownloadButton > button:hover {{
        box-shadow: 0 0 16px rgba(59, 130, 246, 0.55);
        transform: translateY(-1px);
    }}

    .stTextInput input, .stNumberInput input, .stDateInput input,
    .stTimeInput input, .stSelectbox div[data-baseweb="select"] > div,
    .stTextArea textarea {{
        background-color: {CARD_BG} !important;
        color: #F4F4F5 !important;
        border: 1px solid {BORDER} !important;
        border-radius: 8px !important;
    }}

    .stTabs [data-baseweb="tab-list"] {{
        gap: 6px;
    }}
    .stTabs [data-baseweb="tab"] {{
        background-color: {CARD_BG};
        border-radius: 8px 8px 0 0;
        color: {TEXT_MUTED};
        padding: 10px 18px;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {BLUE_DARK} !important;
        color: white !important;
    }}

    div[data-testid="stDataFrame"] {{
        border: 1px solid {BORDER};
        border-radius: 10px;
        overflow: hidden;
    }}

    .fd-title {{
        font-size: 1.6rem;
        font-weight: 800;
        background: linear-gradient(90deg, {BLUE_LIGHT}, {BLUE});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }}
    .fd-subtitle {{
        color: {TEXT_MUTED};
        margin-top: -6px;
        margin-bottom: 20px;
    }}

    /* Modern dashboard card used for budgets / goals / insights */
    .fd-card {{
        background: linear-gradient(145deg, {CARD_BG}, {CARD_BG_2});
        border: 1px solid {BORDER};
        border-radius: 14px;
        padding: 18px 20px;
        margin-bottom: 14px;
    }}
    .fd-card-title {{
        font-weight: 700;
        font-size: 1.05rem;
        color: #F4F4F5;
        margin-bottom: 6px;
    }}
    .fd-card-sub {{
        color: {TEXT_MUTED};
        font-size: 0.85rem;
    }}
    .fd-progress-track {{
        background-color: {BORDER};
        border-radius: 8px;
        height: 12px;
        width: 100%;
        overflow: hidden;
        margin: 8px 0;
    }}
    .fd-progress-fill {{
        height: 100%;
        border-radius: 8px;
    }}
    .fd-warning {{
        color: {RED};
        font-weight: 600;
    }}
    .fd-ok {{
        color: {GREEN};
        font-weight: 600;
    }}

    hr {{ border-color: {BORDER} !important; }}

    ::-webkit-scrollbar {{ width: 10px; height: 10px; }}
    ::-webkit-scrollbar-track {{ background: {BLACK}; }}
    ::-webkit-scrollbar-thumb {{ background: {BLUE_DARK}; border-radius: 10px; }}
    </style>
    """,
    unsafe_allow_html=True,
)

PLOTLY_TEMPLATE = go.layout.Template(
    layout=dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#F4F4F5"),
        colorway=[BLUE, BLUE_LIGHT, "#60A5FA", "#2563EB", "#1E40AF",
                  "#BFDBFE", GREEN, RED, AMBER, "#38BDF8"],
        xaxis=dict(gridcolor=BORDER, zerolinecolor=BORDER),
        yaxis=dict(gridcolor=BORDER, zerolinecolor=BORDER),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
    )
)

def load_data() -> pd.DataFrame:
    """Load transactions from CSV, creating the file if it doesn't exist."""
    try:
        if not os.path.exists(DATA_FILE):
            df = pd.DataFrame(columns=COLUMNS)
            df.to_csv(DATA_FILE, index=False)
            return df

        df = pd.read_csv(DATA_FILE)
        if df.empty:
            return pd.DataFrame(columns=COLUMNS)

        df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.date
        df = df.dropna(subset=["Amount", "Date"])
        return df
    except Exception as e:
        st.error(f"Error loading transactions: {e}")
        return pd.DataFrame(columns=COLUMNS)


def save_data(df: pd.DataFrame) -> None:
    try:
        df.to_csv(DATA_FILE, index=False)
    except Exception as e:
        st.error(f"Error saving transactions: {e}")


def add_transaction(t_type, amount, category, t_date, t_time, description):
    df = load_data()
    new_id = int(df["ID"].max()) + 1 if not df.empty else 1
    new_row = {
        "ID": new_id,
        "Type": t_type,
        "Amount": round(float(amount), 2),
        "Category": category,
        "Date": t_date,
        "Time": t_time,
        "Description": description,
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    save_data(df)
    return new_id


def update_transaction(t_id, t_type, amount, category, t_date, t_time, description) -> bool:
    """Update an existing transaction in place. Returns True on success."""
    df = load_data()
    idx = df.index[df["ID"] == t_id]
    if len(idx) == 0:
        return False
    i = idx[0]
    df.loc[i, "Type"] = t_type
    df.loc[i, "Amount"] = round(float(amount), 2)
    df.loc[i, "Category"] = category
    df.loc[i, "Date"] = t_date
    df.loc[i, "Time"] = t_time
    df.loc[i, "Description"] = description
    save_data(df)
    return True


def delete_transactions(ids_to_delete):
    df = load_data()
    df = df[~df["ID"].isin(ids_to_delete)]
    save_data(df)


def load_budgets() -> pd.DataFrame:
    try:
        if not os.path.exists(BUDGET_FILE):
            df = pd.DataFrame(columns=BUDGET_COLUMNS)
            df.to_csv(BUDGET_FILE, index=False)
            return df
        df = pd.read_csv(BUDGET_FILE)
        if df.empty:
            return pd.DataFrame(columns=BUDGET_COLUMNS)
        df["Limit"] = pd.to_numeric(df["Limit"], errors="coerce").fillna(0)
        return df
    except Exception as e:
        st.error(f"Error loading budgets: {e}")
        return pd.DataFrame(columns=BUDGET_COLUMNS)


def save_budgets(df: pd.DataFrame) -> None:
    try:
        df.to_csv(BUDGET_FILE, index=False)
    except Exception as e:
        st.error(f"Error saving budgets: {e}")


def set_budget(category: str, limit: float) -> None:
    df = load_budgets()
    if category in df["Category"].values:
        df.loc[df["Category"] == category, "Limit"] = round(float(limit), 2)
    else:
        df = pd.concat(
            [df, pd.DataFrame([{"Category": category, "Limit": round(float(limit), 2)}])],
            ignore_index=True,
        )
    save_budgets(df)


def delete_budget(category: str) -> None:
    df = load_budgets()
    df = df[df["Category"] != category]
    save_budgets(df)


def load_goals() -> pd.DataFrame:
    try:
        if not os.path.exists(GOALS_FILE):
            df = pd.DataFrame(columns=GOALS_COLUMNS)
            df.to_csv(GOALS_FILE, index=False)
            return df
        df = pd.read_csv(GOALS_FILE)
        if df.empty:
            return pd.DataFrame(columns=GOALS_COLUMNS)
        df["TargetAmount"] = pd.to_numeric(df["TargetAmount"], errors="coerce").fillna(0)
        df["CurrentAmount"] = pd.to_numeric(df["CurrentAmount"], errors="coerce").fillna(0)
        return df
    except Exception as e:
        st.error(f"Error loading savings goals: {e}")
        return pd.DataFrame(columns=GOALS_COLUMNS)


def save_goals(df: pd.DataFrame) -> None:
    try:
        df.to_csv(GOALS_FILE, index=False)
    except Exception as e:
        st.error(f"Error saving savings goals: {e}")


def add_goal(name: str, target: float, current: float) -> int:
    df = load_goals()
    new_id = int(df["ID"].max()) + 1 if not df.empty else 1
    row = {
        "ID": new_id,
        "GoalName": name,
        "TargetAmount": round(float(target), 2),
        "CurrentAmount": round(float(current), 2),
        "CreatedDate": date.today(),
    }
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    save_goals(df)
    return new_id


def update_goal_amount(goal_id: int, new_amount: float) -> None:
    df = load_goals()
    df.loc[df["ID"] == goal_id, "CurrentAmount"] = round(float(new_amount), 2)
    save_goals(df)


def delete_goal(goal_id: int) -> None:
    df = load_goals()
    df = df[df["ID"] != goal_id]
    save_goals(df)


def compute_summary(df: pd.DataFrame):
    """Return (total_income, total_expense, balance, savings)."""
    total_income = df.loc[df["Type"] == "Income", "Amount"].sum()
    total_expense = df.loc[df["Type"] == "Expense", "Amount"].sum()
    balance = total_income - total_expense
    savings = balance
    return total_income, total_expense, balance, savings


def avg_daily_spending(df: pd.DataFrame) -> float:
    exp_df = df[df["Type"] == "Expense"]
    if exp_df.empty:
        return 0.0
    days = (exp_df["Date"].max() - exp_df["Date"].min()).days + 1
    days = max(days, 1)
    return exp_df["Amount"].sum() / days


def monthly_totals(df: pd.DataFrame) -> pd.DataFrame:
    """Return a DataFrame indexed by Month (YYYY-MM) with Income/Expense columns."""
    if df.empty:
        return pd.DataFrame(columns=["Income", "Expense"])
    dfm = df.copy()
    dfm["Month"] = pd.to_datetime(dfm["Date"]).dt.strftime("%Y-%m")
    monthly = dfm.groupby(["Month", "Type"])["Amount"].sum().unstack(fill_value=0)
    for col in ["Income", "Expense"]:
        if col not in monthly.columns:
            monthly[col] = 0
    return monthly.sort_index()


def generate_insights(df: pd.DataFrame) -> dict:
    """Compute automatic financial insights and return a dict of results + messages."""
    messages = []
    result = {"highest_category": None, "lowest_category": None, "mom_change_pct": None, "messages": messages}

    exp_df = df[df["Type"] == "Expense"]
    if exp_df.empty:
        messages.append("Not enough expense data yet to generate insights.")
        return result

    cat_sum = exp_df.groupby("Category")["Amount"].sum().sort_values(ascending=False)
    highest_cat, lowest_cat = cat_sum.index[0], cat_sum.index[-1]
    result["highest_category"] = highest_cat
    result["lowest_category"] = lowest_cat
    messages.append(f"Highest spending category: {highest_cat} (₹{cat_sum.iloc[0]:,.2f}).")
    messages.append(f"Lowest spending category: {lowest_cat} (₹{cat_sum.iloc[-1]:,.2f}).")

    dfm = df.copy()
    dfm["Month"] = pd.to_datetime(dfm["Date"]).dt.to_period("M")
    months_sorted = sorted(dfm["Month"].unique())
    if len(months_sorted) >= 2:
        current_month, prev_month = months_sorted[-1], months_sorted[-2]
        cur_exp = dfm[(dfm["Month"] == current_month) & (dfm["Type"] == "Expense")]["Amount"].sum()
        prev_exp = dfm[(dfm["Month"] == prev_month) & (dfm["Type"] == "Expense")]["Amount"].sum()
        if prev_exp > 0:
            change_pct = ((cur_exp - prev_exp) / prev_exp) * 100
            result["mom_change_pct"] = change_pct
            if change_pct > 0:
                messages.append(f"Spending increased {change_pct:.1f}% vs. last month.")
            elif change_pct < 0:
                messages.append(f"Spending decreased {abs(change_pct):.1f}% vs. last month — nice work.")
            else:
                messages.append("Spending is unchanged from last month.")

    total_income, _, _, savings = compute_summary(df)
    if total_income > 0:
        savings_rate = (savings / total_income) * 100
        if savings_rate < 10:
            messages.append(f"Savings rate is {savings_rate:.1f}%. Aim for at least 20% of income saved.")
        else:
            messages.append(f"Savings rate is {savings_rate:.1f}% — solid progress.")

    return result


def generate_pdf_report(df: pd.DataFrame, budgets_df: pd.DataFrame, goals_df: pd.DataFrame) -> bytes:
    """Build a full PDF financial report and return it as bytes."""
    total_income, total_expense, balance, savings = compute_summary(df)
    insights = generate_insights(df)
    monthly = monthly_totals(df)

    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(29, 78, 216)
    pdf.cell(0, 10, "Personal Finance Report", ln=True, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 8, f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align="C")
    pdf.ln(6)

    pdf.set_text_color(20, 20, 20)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 9, "Financial Summary", ln=True)
    pdf.set_font("Helvetica", "", 11)
    for label, val in [
        ("Total Income", f"₹{total_income:,.2f}"),
        ("Total Expenses", f"₹{total_expense:,.2f}"),
        ("Current Balance", f"₹{balance:,.2f}"),
        ("Total Savings", f"₹{savings:,.2f}"),
    ]:
        pdf.cell(95, 8, label)
        pdf.cell(95, 8, val, ln=True)
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 9, "Monthly Summary", ln=True)
    if monthly.empty:
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 8, "No transaction data available.", ln=True)
    else:
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(60, 7, "Month", border=1)
        pdf.cell(60, 7, "Income", border=1)
        pdf.cell(60, 7, "Expense", border=1, ln=True)
        pdf.set_font("Helvetica", "", 10)
        for month, row in monthly.iterrows():
            pdf.cell(60, 7, str(month), border=1)
            pdf.cell(60, 7, f"₹{row['Income']:,.2f}", border=1)
            pdf.cell(60, 7, f"₹{row['Expense']:,.2f}", border=1, ln=True)
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 9, "Expense Category Analysis", ln=True)
    exp_df = df[df["Type"] == "Expense"]
    if exp_df.empty:
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 8, "No expense data available.", ln=True)
    else:
        cat_sum = exp_df.groupby("Category")["Amount"].sum().sort_values(ascending=False)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(90, 7, "Category", border=1)
        pdf.cell(90, 7, "Total Spent", border=1, ln=True)
        pdf.set_font("Helvetica", "", 10)
        for cat, amt in cat_sum.items():
            pdf.cell(90, 7, str(cat), border=1)
            pdf.cell(90, 7, f"₹{amt:,.2f}", border=1, ln=True)
    pdf.ln(4)

    if not budgets_df.empty:
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 9, "Budget Overview", ln=True)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(63, 7, "Category", border=1)
        pdf.cell(63, 7, "Limit", border=1)
        pdf.cell(64, 7, "Spent", border=1, ln=True)
        pdf.set_font("Helvetica", "", 10)
        exp_by_cat = exp_df.groupby("Category")["Amount"].sum() if not exp_df.empty else pd.Series(dtype=float)
        for _, brow in budgets_df.iterrows():
            spent = exp_by_cat.get(brow["Category"], 0.0)
            pdf.cell(63, 7, str(brow["Category"]), border=1)
            pdf.cell(63, 7, f"₹{brow['Limit']:,.2f}", border=1)
            pdf.cell(64, 7, f"₹{spent:,.2f}", border=1, ln=True)
        pdf.ln(4)

    if not goals_df.empty:
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 9, "Savings Goals", ln=True)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(60, 7, "Goal", border=1)
        pdf.cell(45, 7, "Target", border=1)
        pdf.cell(45, 7, "Saved", border=1)
        pdf.cell(40, 7, "Progress", border=1, ln=True)
        pdf.set_font("Helvetica", "", 10)
        for _, grow in goals_df.iterrows():
            pct = (grow["CurrentAmount"] / grow["TargetAmount"] * 100) if grow["TargetAmount"] > 0 else 0
            pdf.cell(60, 7, str(grow["GoalName"]), border=1)
            pdf.cell(45, 7, f"₹{grow['TargetAmount']:,.2f}", border=1)
            pdf.cell(45, 7, f"₹{grow['CurrentAmount']:,.2f}", border=1)
            pdf.cell(40, 7, f"{pct:.1f}%", border=1, ln=True)
        pdf.ln(4)

    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 9, "Financial Insights", ln=True)
    pdf.set_font("Helvetica", "", 10)
    for line in insights["messages"]:
        pdf.multi_cell(0, 7, f"- {line}")

    return bytes(pdf.output())


def generate_excel_bytes(df: pd.DataFrame, budgets_df: pd.DataFrame, goals_df: pd.DataFrame) -> bytes:
    """Build a multi-sheet Excel workbook and return it as bytes."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        (df if not df.empty else pd.DataFrame(columns=COLUMNS)).to_excel(
            writer, index=False, sheet_name="Transactions"
        )
        monthly = monthly_totals(df)
        (monthly if not monthly.empty else pd.DataFrame(columns=["Income", "Expense"])).to_excel(
            writer, sheet_name="Monthly Summary"
        )
        exp_df = df[df["Type"] == "Expense"]
        if not exp_df.empty:
            cat_sum = exp_df.groupby("Category")["Amount"].sum().sort_values(ascending=False)
            cat_sum.to_frame("Total Spent").to_excel(writer, sheet_name="Category Summary")
        if not budgets_df.empty:
            budgets_df.to_excel(writer, index=False, sheet_name="Budgets")
        if not goals_df.empty:
            goals_df.to_excel(writer, index=False, sheet_name="Savings Goals")
    return output.getvalue()


st.sidebar.markdown(
    f"""
    <div style="text-align:center; padding: 10px 0 20px 0;">
        <div style="font-size: 2.2rem;"></div>
        <div style="font-size:1.25rem; font-weight:800; color:{BLUE_LIGHT};">
            Finance Dashboard
        </div>
        <div style="color:{TEXT_MUTED}; font-size:0.85rem;">Track. Analyze. Grow.</div>
    </div>
    <hr>
    """,
    unsafe_allow_html=True,
)

page = st.sidebar.radio(
    "Navigate",
    [
        "Dashboard",
        "Add Transaction",
        "Transaction History",
        "Analytics",
        "Budget Planner",
        "Savings Goals",
        "Export & Reports",
    ],
    label_visibility="collapsed",
)

st.sidebar.markdown("<hr>", unsafe_allow_html=True)
st.sidebar.caption(f"Data file: `{DATA_FILE}`")

df_all = load_data()
budgets_all = load_budgets()
goals_all = load_goals()

if page == "Dashboard":
    st.markdown('<div class="fd-title">Dashboard Overview</div>', unsafe_allow_html=True)
    st.markdown('<div class="fd-subtitle">Your financial health at a glance</div>', unsafe_allow_html=True)

    total_income, total_expense, balance, savings = compute_summary(df_all)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Income", f"₹{total_income:,.2f}")
    c2.metric("Total Expenses", f"₹{total_expense:,.2f}")
    c3.metric("Current Balance", f"₹{balance:,.2f}", delta=("Positive" if balance >= 0 else "Negative"))
    c4.metric("Total Savings", f"₹{savings:,.2f}")

    if not df_all.empty:
        exp_df = df_all[df_all["Type"] == "Expense"]
        inc_df = df_all[df_all["Type"] == "Income"]
        highest_expense = exp_df["Amount"].max() if not exp_df.empty else 0.0
        highest_income = inc_df["Amount"].max() if not inc_df.empty else 0.0
        avg_daily = avg_daily_spending(df_all)
        total_txn = len(df_all)
    else:
        highest_expense = highest_income = avg_daily = 0.0
        total_txn = 0

    d1, d2, d3, d4 = st.columns(4)
    d1.metric("Avg. Daily Spending", f"₹{avg_daily:,.2f}")
    d2.metric("Highest Expense", f"₹{highest_expense:,.2f}")
    d3.metric("Highest Income", f"₹{highest_income:,.2f}")
    d4.metric("Transactions", f"{total_txn}")

    st.markdown("<br>", unsafe_allow_html=True)

    if df_all.empty:
        st.info("No transactions yet. Head to **Add Transaction** to get started!")
    else:
        col_a, col_b = st.columns([1.3, 1])

        with col_a:
            st.markdown("#### Income vs Expense Over Time")
            trend = df_all.groupby(["Date", "Type"])["Amount"].sum().reset_index()
            fig = px.line(
                trend, x="Date", y="Amount", color="Type", markers=True,
                template=PLOTLY_TEMPLATE,
                color_discrete_map={"Income": GREEN, "Expense": RED},
            )
            fig.update_layout(height=350, margin=dict(t=20, l=10, r=10, b=10))
            st.plotly_chart(fig, use_container_width=True)

        with col_b:
            st.markdown("#### Expense by Category")
            exp_df = df_all[df_all["Type"] == "Expense"]
            if not exp_df.empty:
                cat_sum = exp_df.groupby("Category")["Amount"].sum().reset_index()
                fig2 = px.pie(cat_sum, names="Category", values="Amount", hole=0.5, template=PLOTLY_TEMPLATE)
                fig2.update_layout(height=350, margin=dict(t=20, l=10, r=10, b=10))
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("No expenses recorded yet.")

        st.markdown("#### Recent Transactions")
        recent = df_all.sort_values(by=["Date", "Time"], ascending=False).head(5)
        st.dataframe(recent, use_container_width=True, hide_index=True)

elif page == "Add Transaction":
    st.markdown('<div class="fd-title">Add a Transaction</div>', unsafe_allow_html=True)
    st.markdown('<div class="fd-subtitle">Record a new income or expense entry</div>', unsafe_allow_html=True)

    with st.form("add_transaction_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            t_type = st.radio("Transaction Type", ["Income", "Expense"], horizontal=True)
            amount = st.number_input("Amount (₹)", min_value=0.0, step=0.01, format="%.2f")
            category_list = INCOME_CATEGORIES if t_type == "Income" else EXPENSE_CATEGORIES
            category = st.selectbox("Category", category_list)
        with col2:
            t_date = st.date_input("Date", value=date.today())
            t_time = st.time_input("Time", value=datetime.now().time().replace(microsecond=0))
            description = st.text_area("Description", placeholder="e.g. Weekly groceries at the market", height=95)

        submitted = st.form_submit_button("Save Transaction", use_container_width=True)

        if submitted:
            if amount <= 0:
                st.error("Please enter an amount greater than 0.")
            else:
                try:
                    new_id = add_transaction(t_type, amount, category, t_date, t_time, description)
                    st.success(f"{t_type} of ₹{amount:,.2f} saved successfully! (ID #{new_id})")
                    st.balloons()
                except Exception as e:
                    st.error(f"Could not save transaction: {e}")

elif page == "Transaction History":
    st.markdown('<div class="fd-title">Transaction History</div>', unsafe_allow_html=True)
    st.markdown('<div class="fd-subtitle">Browse, search, filter, edit, and delete records</div>', unsafe_allow_html=True)

    if df_all.empty:
        st.info("No transactions yet. Head to **Add Transaction** to get started!")
    else:
        with st.container():
            f1, f2, f3, f4 = st.columns([1, 1, 1, 1.4])
            with f1:
                type_filter = st.multiselect("Type", ["Income", "Expense"], default=["Income", "Expense"])
            with f2:
                min_date, max_date = df_all["Date"].min(), df_all["Date"].max()
                date_range = st.date_input("Date range", value=(min_date, max_date),
                                            min_value=min_date, max_value=max_date)
            with f3:
                all_cats = sorted(df_all["Category"].dropna().unique().tolist())
                cat_filter = st.multiselect("Category", all_cats, default=all_cats)
            with f4:
                search_term = st.text_input("Search description", placeholder="Type to search...")

        filtered = df_all[df_all["Type"].isin(type_filter)]
        filtered = filtered[filtered["Category"].isin(cat_filter)]

        if isinstance(date_range, tuple) and len(date_range) == 2:
            start_d, end_d = date_range
            filtered = filtered[(filtered["Date"] >= start_d) & (filtered["Date"] <= end_d)]

        if search_term:
            filtered = filtered[
                filtered["Description"].astype(str).str.contains(search_term, case=False, na=False)
            ]

        filtered = filtered.sort_values(by=["Date", "Time"], ascending=False)

        st.markdown(f"**{len(filtered)}** transaction(s) found")
        st.dataframe(filtered, use_container_width=True, hide_index=True)

        st.markdown("---")
        col_edit, col_delete = st.columns(2)

        with col_edit:
            st.markdown("#### Edit a Transaction")
            edit_id = st.selectbox(
                "Select transaction ID to edit",
                options=[None] + filtered["ID"].tolist(),
                format_func=lambda x: "— choose —" if x is None else f"#{x}",
                key="edit_select",
            )
            if edit_id is not None:
                row = df_all[df_all["ID"] == edit_id].iloc[0]
                with st.form("edit_transaction_form"):
                    e_type = st.radio("Type", ["Income", "Expense"],
                                       index=0 if row["Type"] == "Income" else 1, horizontal=True)
                    e_amount = st.number_input("Amount (₹)", min_value=0.0, step=0.01,
                                                value=float(row["Amount"]), format="%.2f")
                    e_cat_list = INCOME_CATEGORIES if e_type == "Income" else EXPENSE_CATEGORIES
                    e_cat_default = row["Category"] if row["Category"] in e_cat_list else e_cat_list[0]
                    e_category = st.selectbox("Category", e_cat_list, index=e_cat_list.index(e_cat_default))
                    e_date = st.date_input("Date", value=row["Date"])
                    e_description = st.text_area("Description", value=str(row.get("Description", "")))
                    save_edit = st.form_submit_button("Update Transaction", use_container_width=True)

                    if save_edit:
                        if e_amount <= 0:
                            st.error("Amount must be greater than 0.")
                        else:
                            try:
                                ok = update_transaction(
                                    edit_id, e_type, e_amount, e_category, e_date,
                                    row.get("Time", "00:00:00"), e_description,
                                )
                                if ok:
                                    st.success(f"Transaction #{edit_id} updated.")
                                    st.rerun()
                                else:
                                    st.error("Transaction not found.")
                            except Exception as e:
                                st.error(f"Could not update transaction: {e}")

        with col_delete:
            st.markdown("#### Delete Transactions")
            ids_to_delete = st.multiselect(
                "Select transaction ID(s) to delete",
                options=filtered["ID"].tolist(),
            )
            if st.button("Delete Selected", use_container_width=True):
                if ids_to_delete:
                    try:
                        delete_transactions(ids_to_delete)
                        st.success(f"Deleted {len(ids_to_delete)} transaction(s).")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Could not delete transactions: {e}")
                else:
                    st.warning("Select at least one transaction to delete.")

elif page == "Analytics":
    st.markdown('<div class="fd-title">Analytics</div>', unsafe_allow_html=True)
    st.markdown('<div class="fd-subtitle">Deeper insight into your financial patterns</div>', unsafe_allow_html=True)

    if df_all.empty:
        st.info("No transactions yet. Head to **Add Transaction** to get started!")
    else:
        st.markdown("#### Income vs Expense")
        trend = df_all.groupby(["Date", "Type"])["Amount"].sum().reset_index()
        fig1 = px.line(
            trend, x="Date", y="Amount", color="Type", markers=True,
            template=PLOTLY_TEMPLATE,
            color_discrete_map={"Income": GREEN, "Expense": RED},
        )
        fig1.update_layout(height=380, margin=dict(t=20, l=10, r=10, b=10))
        st.plotly_chart(fig1, use_container_width=True)

        col_a, col_b = st.columns(2)
        exp_df = df_all[df_all["Type"] == "Expense"]

        with col_a:
            st.markdown("#### Expense Distribution by Category")
            if not exp_df.empty:
                cat_sum = exp_df.groupby("Category")["Amount"].sum().reset_index()
                fig2 = px.pie(cat_sum, names="Category", values="Amount", hole=0.5, template=PLOTLY_TEMPLATE)
                fig2.update_layout(height=380, margin=dict(t=20, l=10, r=10, b=10))
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("No expenses recorded yet.")

        with col_b:
            st.markdown("#### Daily Spending Trend")
            if not exp_df.empty:
                daily = exp_df.groupby("Date")["Amount"].sum().reset_index()
                fig3 = px.bar(daily, x="Date", y="Amount", template=PLOTLY_TEMPLATE)
                fig3.update_traces(marker_color=BLUE)
                fig3.update_layout(height=380, margin=dict(t=20, l=10, r=10, b=10))
                st.plotly_chart(fig3, use_container_width=True)
            else:
                st.info("No expenses recorded yet.")

        col_c, col_d = st.columns(2)
        monthly = monthly_totals(df_all)

        with col_c:
            st.markdown("#### Monthly Expense Comparison")
            if not monthly.empty:
                fig4 = px.bar(monthly.reset_index(), x="Month", y="Expense", template=PLOTLY_TEMPLATE)
                fig4.update_traces(marker_color=RED)
                fig4.update_layout(height=350, margin=dict(t=20, l=10, r=10, b=10))
                st.plotly_chart(fig4, use_container_width=True)
            else:
                st.info("No monthly data available yet.")

        with col_d:
            st.markdown("#### Monthly Income Comparison")
            if not monthly.empty:
                fig5 = px.bar(monthly.reset_index(), x="Month", y="Income", template=PLOTLY_TEMPLATE)
                fig5.update_traces(marker_color=GREEN)
                fig5.update_layout(height=350, margin=dict(t=20, l=10, r=10, b=10))
                st.plotly_chart(fig5, use_container_width=True)
            else:
                st.info("No monthly data available yet.")

        st.markdown("#### Savings Growth Over Time")
        if not monthly.empty:
            savings_df = monthly.copy()
            savings_df["Net Savings"] = savings_df["Income"] - savings_df["Expense"]
            savings_df["Cumulative Savings"] = savings_df["Net Savings"].cumsum()
            fig6 = px.area(savings_df.reset_index(), x="Month", y="Cumulative Savings", template=PLOTLY_TEMPLATE)
            fig6.update_traces(line_color=BLUE_LIGHT, fillcolor="rgba(59,130,246,0.25)")
            fig6.update_layout(height=350, margin=dict(t=20, l=10, r=10, b=10))
            st.plotly_chart(fig6, use_container_width=True)
        else:
            st.info("No monthly data available yet.")

        st.markdown("#### Category Breakdown Table")
        summary = df_all.groupby(["Type", "Category"])["Amount"].agg(["sum", "count"]).reset_index()
        summary.columns = ["Type", "Category", "Total Amount", "Transaction Count"]
        summary = summary.sort_values(by="Total Amount", ascending=False)
        st.dataframe(summary, use_container_width=True, hide_index=True)

        st.markdown("#### Financial Insights")
        insights = generate_insights(df_all)
        for msg in insights["messages"]:
            st.markdown(f'<div class="fd-card">{msg}</div>', unsafe_allow_html=True)

elif page == "Budget Planner":
    st.markdown('<div class="fd-title">Budget Planner</div>', unsafe_allow_html=True)
    st.markdown('<div class="fd-subtitle">Set monthly limits and track how much you have used</div>', unsafe_allow_html=True)

    with st.form("set_budget_form"):
        b1, b2 = st.columns(2)
        with b1:
            budget_category = st.selectbox("Category", ["Overall (All Expenses)"] + EXPENSE_CATEGORIES)
        with b2:
            budget_limit = st.number_input("Monthly Limit (₹)", min_value=0.0, step=10.0, format="%.2f")
        set_submitted = st.form_submit_button("Save Budget", use_container_width=True)
        if set_submitted:
            if budget_limit <= 0:
                st.error("Please enter a limit greater than 0.")
            else:
                try:
                    set_budget(budget_category, budget_limit)
                    st.success(f"Budget for '{budget_category}' set to ₹{budget_limit:,.2f}.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Could not save budget: {e}")

    st.markdown("---")
    budgets_all = load_budgets()

    if budgets_all.empty:
        st.info("No budgets set yet. Use the form above to create one.")
    else:
        this_month = date.today().strftime("%Y-%m")
        exp_df = df_all[df_all["Type"] == "Expense"].copy()
        if not exp_df.empty:
            exp_df["Month"] = pd.to_datetime(exp_df["Date"]).dt.strftime("%Y-%m")
            exp_this_month = exp_df[exp_df["Month"] == this_month]
        else:
            exp_this_month = exp_df

        for _, brow in budgets_all.iterrows():
            category, limit = brow["Category"], brow["Limit"]
            if category == "Overall (All Expenses)":
                spent = exp_this_month["Amount"].sum() if not exp_this_month.empty else 0.0
            else:
                spent = (
                    exp_this_month.loc[exp_this_month["Category"] == category, "Amount"].sum()
                    if not exp_this_month.empty else 0.0
                )

            pct_used = min((spent / limit) * 100, 100) if limit > 0 else 0
            remaining = limit - spent
            bar_color = RED if spent > limit else (AMBER if pct_used >= 80 else GREEN)

            col_info, col_delete = st.columns([5, 1])
            with col_info:
                st.markdown(
                    f"""
                    <div class="fd-card">
                        <div class="fd-card-title">{category}</div>
                        <div class="fd-card-sub">Limit: ₹{limit:,.2f} &nbsp;|&nbsp; Spent: ₹{spent:,.2f}
                        &nbsp;|&nbsp; Remaining: ₹{remaining:,.2f}</div>
                        <div class="fd-progress-track">
                            <div class="fd-progress-fill" style="width:{pct_used}%; background-color:{bar_color};"></div>
                        </div>
                        {'<div class="fd-warning">Budget exceeded!</div>' if spent > limit else f'<div class="fd-ok">{pct_used:.1f}% used</div>'}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with col_delete:
                if st.button("Remove", key=f"del_budget_{category}"):
                    delete_budget(category)
                    st.rerun()

elif page == "Savings Goals":
    st.markdown('<div class="fd-title">Savings Goals</div>', unsafe_allow_html=True)
    st.markdown('<div class="fd-subtitle">Create goals and track your progress</div>', unsafe_allow_html=True)

    with st.form("add_goal_form", clear_on_submit=True):
        g1, g2, g3 = st.columns(3)
        with g1:
            goal_name = st.text_input("Goal Name", placeholder="e.g. Emergency Fund")
        with g2:
            goal_target = st.number_input("Target Amount (₹)", min_value=0.0, step=50.0, format="%.2f")
        with g3:
            goal_current = st.number_input("Already Saved (₹)", min_value=0.0, step=10.0, format="%.2f")
        goal_submitted = st.form_submit_button("Create Goal", use_container_width=True)

        if goal_submitted:
            if not goal_name.strip():
                st.error("Please enter a goal name.")
            elif goal_target <= 0:
                st.error("Target amount must be greater than 0.")
            else:
                try:
                    add_goal(goal_name.strip(), goal_target, goal_current)
                    st.success(f"Goal '{goal_name}' created.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Could not create goal: {e}")

    st.markdown("---")
    goals_all = load_goals()

    if goals_all.empty:
        st.info("No savings goals yet. Create one above to start tracking progress.")
    else:
        for _, grow in goals_all.iterrows():
            goal_id = int(grow["ID"])
            target, current = grow["TargetAmount"], grow["CurrentAmount"]
            pct = min((current / target) * 100, 100) if target > 0 else 0
            remaining = max(target - current, 0)

            col_info, col_update, col_delete = st.columns([4, 2, 1])
            with col_info:
                st.markdown(
                    f"""
                    <div class="fd-card">
                        <div class="fd-card-title">{grow['GoalName']}</div>
                        <div class="fd-card-sub">Target: ₹{target:,.2f} &nbsp;|&nbsp; Saved: ₹{current:,.2f}
                        &nbsp;|&nbsp; Remaining: ₹{remaining:,.2f}</div>
                        <div class="fd-progress-track">
                            <div class="fd-progress-fill" style="width:{pct}%; background-color:{BLUE};"></div>
                        </div>
                        <div class="fd-ok">{pct:.1f}% complete</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with col_update:
                new_amount = st.number_input(
                    "Update saved amount", min_value=0.0, value=float(current),
                    step=10.0, format="%.2f", key=f"goal_update_{goal_id}",
                )
                if st.button("Update", key=f"goal_btn_{goal_id}"):
                    update_goal_amount(goal_id, new_amount)
                    st.rerun()
            with col_delete:
                st.write("")
                if st.button("Remove", key=f"goal_del_{goal_id}"):
                    delete_goal(goal_id)
                    st.rerun()

elif page == "Export & Reports":
    st.markdown('<div class="fd-title">Export &amp; Reports</div>', unsafe_allow_html=True)
    st.markdown('<div class="fd-subtitle">Download your data as CSV, Excel, or a full PDF report</div>', unsafe_allow_html=True)

    if df_all.empty:
        st.info("No transactions to export yet.")
    else:
        st.dataframe(df_all, use_container_width=True, hide_index=True)

        e1, e2, e3 = st.columns(3)

        with e1:
            csv_data = df_all.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Download CSV",
                data=csv_data,
                file_name=f"transactions_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True,
            )

        with e2:
            try:
                excel_data = generate_excel_bytes(df_all, budgets_all, goals_all)
                st.download_button(
                    label="Download Excel (.xlsx)",
                    data=excel_data,
                    file_name=f"finance_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )
            except Exception as e:
                st.error(f"Could not generate Excel file: {e}")

        with e3:
            try:
                pdf_bytes = generate_pdf_report(df_all, budgets_all, goals_all)
                st.download_button(
                    label="Download PDF Report",
                    data=pdf_bytes,
                    file_name=f"finance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
            except Exception as e:
                st.error(f"Could not generate PDF report: {e}")