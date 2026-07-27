# Personal Finance Dashboard

A modern, dark themed personal finance tracker built with Python and Streamlit. Data is stored locally in a CSV file — no database needed.

## Features
- **Dashboard** — Total Income, Total Expenses, Current Balance, Total Transactions, plus quick charts and recent activity
- **Add Transaction** — log Income or Expense with amount, category, date, time, and description
- **Transaction History** — searchable, filterable table (by date range, type, category, keyword) with delete support
- **Analytics** — Income vs Expense line chart, expense-by-category pie chart, daily spending bar chart, income-by-category chart
- **Export** — download all transactions as a CSV file

## Project Structure
```
finance_dashboard/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── data/
│   └── transactions.csv   # Transaction data store (auto-created if missing)
└── README.md
```

## Setup (VS Code / Cline)

1. Open this folder in VS Code.
2. Open a terminal (``Ctrl+` ``) and create a virtual environment (recommended):
   ```bash
   python -m venv venv
   ```
   Activate it:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the app:
   ```bash
   streamlit run app.py
   ```
5. Streamlit will open automatically in your browser at `http://localhost:8501`.

## Notes
- All data lives in `data/transactions.csv`. Delete this file (or its rows) to reset the dashboard.
- The color theme (black + violet) is defined via custom CSS inside `app.py` — search for `CUSTOM_CSS` to tweak colors, and `PLOTLY_TEMPLATE` to adjust chart styling.
- To extend later (per the project roadmap): AI-generated insights, budgeting assistant, cash-flow forecasting, OCR receipt scanning, investment recommendations, and user authentication can all be added as new pages/modules without changing the core CSV storage layer.
