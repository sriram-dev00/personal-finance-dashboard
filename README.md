# Personal Finance Dashboard

A modern, dark-themed personal finance tracker built with Python and Streamlit — record income and expenses, plan budgets, track savings goals, and export financial reports, all backed by local CSV storage.

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.38%2B-FF4B4B?logo=streamlit&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.2%2B-150458?logo=pandas&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-5.24%2B-3F4F75?logo=plotly&logoColor=white)

## Overview

Personal Finance Dashboard is a single-file Streamlit application for tracking personal income and expenses without needing a database. Every transaction, budget, and savings goal is stored in local CSV files, and the app surfaces that data through an interactive dashboard, analytics charts, a budget planner, a savings-goal tracker, and multi-format export (CSV, Excel, and PDF). All monetary values are displayed in Indian Rupees (₹).

## Key Features

- **Dashboard** — Total Income, Total Expenses, Current Balance, Total Savings, Average Daily Spending, Highest Expense, Highest Income, and Transaction count, alongside an income-vs-expense trend chart, an expense-by-category chart, and a recent-transactions table.
- **Add Transaction** — log an Income or Expense entry with amount, category, date, time, and description.
- **Transaction History** — a searchable, filterable table (by date range, transaction type, category, and keyword) with inline **edit** and **delete** support.
- **Analytics** — income vs. expense trend, expense distribution by category, daily spending trend, monthly expense comparison, monthly income comparison, cumulative savings growth, a category breakdown table, and automatically generated financial insights (highest/lowest spending category, month-over-month spending change, savings-rate feedback).
- **Budget Planner** — set an overall or category-wise monthly spending limit, with progress bars showing amount used, amount remaining, and an over-budget warning.
- **Savings Goals** — create named savings goals with a target amount, update the amount saved over time, and track progress toward each goal.
- **Export & Reports** — download all transaction data as CSV, export a multi-sheet Excel workbook (transactions, monthly summary, category summary, budgets, and goals), or generate a full PDF financial report (summary, monthly breakdown, category analysis, budget overview, goals overview, and insights).
- **Local CSV storage** — no external database is required; data persists in `transactions.csv`, `budgets.csv`, and `goals.csv`.
- **Currency** — all amounts are displayed in Indian Rupees (₹).
- **Modern dark UI** — a black-background theme with blue accent styling, custom CSS, and card-based layouts.

## Technology Stack

| Layer | Technology |
|---|---|
| Language | Python |
| Web framework | Streamlit |
| Data handling | Pandas |
| Charting | Plotly (Express & Graph Objects) |
| PDF generation | fpdf2 |
| Excel export | openpyxl |
| Data storage | Local CSV files |

## Application Workflow

1. The user enters a transaction (or a budget / savings goal) through a Streamlit form.
2. The application validates the input (e.g., amount must be greater than zero).
3. Valid data is written to the corresponding local CSV file (`transactions.csv`, `budgets.csv`, or `goals.csv`).
4. The Dashboard reads the current CSV data and calculates financial metrics (income, expenses, balance, savings, averages, and highs).
5. The Analytics page generates interactive Plotly charts and derives automatic insights from the same data.
6. The user can filter, search, edit, or delete transactions from the Transaction History page at any time.
7. The user can review budget usage and savings-goal progress on their respective pages.
8. The user can export the current data as a CSV file, an Excel workbook, or a generated PDF report from the Export & Reports page.

## Project Structure

```
personal-finance-dashboard/
├── app.py               # Main Streamlit application
├── requirements.txt     # Python dependencies
├── transactions.csv     # Transaction data store (auto-created if missing)
├── budgets.csv          # Budget data store (auto-created if missing)
├── goals.csv            # Savings goal data store (auto-created if missing)
├── screenshots/         # Application screenshots used in this README
└── README.md
```

## Installation and Setup

```bash
git clone https://github.com/sriram-dev00/personal-finance-dashboard.git
cd personal-finance-dashboard
python -m venv venv
```

**Activate the virtual environment**

Windows PowerShell:
```powershell
.\venv\Scripts\Activate.ps1
```

Windows Command Prompt:
```cmd
venv\Scripts\activate
```

macOS/Linux:
```bash
source venv/bin/activate
```

**Install dependencies**
```bash
pip install -r requirements.txt
```

**Run the application**
```bash
streamlit run app.py
```

Streamlit will start a local server and open the app in your browser, typically at `http://localhost:8501`.

## Usage Guide

- **Add an income transaction** — go to *Add Transaction*, select "Income", choose a category (e.g., Salary, Freelance, Business), enter the amount, date, time, and an optional description, then submit.
- **Add an expense transaction** — go to *Add Transaction*, select "Expense", choose a category (e.g., Food & Dining, Rent, Transportation), enter the details, and submit.
- **View financial summaries** — the *Dashboard* page shows total income, total expenses, current balance, total savings, and other key metrics at a glance.
- **Use filters** — on *Transaction History*, filter by transaction type, date range, and category, or search by keyword in the description.
- **Review transaction history** — browse the filtered table, and use the built-in form to edit any transaction's type, amount, category, date, or description.
- **Delete a transaction** — select one or more transaction IDs on *Transaction History* and click delete.
- **Analyze spending** — visit *Analytics* for income-vs-expense trends, category breakdowns, monthly comparisons, savings growth, and automatically generated insights.
- **Plan a budget** — on *Budget Planner*, set an overall or category-specific monthly limit and monitor usage against it.
- **Track a savings goal** — on *Savings Goals*, create a goal with a target amount and update your saved amount as it grows.
- **Export data** — on *Export & Reports*, download your data as a CSV file, an Excel workbook, or a generated PDF report.

## Data Storage

The application currently uses local CSV files (`transactions.csv`, `budgets.csv`, and `goals.csv`) for all persistence and does not require a database. Each file is created automatically the first time the app runs if it does not already exist.

## Screenshots

### Dashboard
Total income, expenses, balance, savings, and quick-glance metrics alongside an income-vs-expense trend and expense-by-category breakdown.

![Dashboard](screenshots/dashboard.png)

### Add Transaction
Log an income or expense entry with amount, category, date, time, and description.

![Add Transaction](screenshots/add-transaction.png)

### Transaction History
Filter by type, date range, and category, search by description, and edit or delete individual records.

![Transaction History](screenshots/transaction-history.png)

### Analytics
Income vs. expense trends, expense distribution, and daily spending patterns.

![Analytics — Trends](screenshots/analytics-1.png)

Monthly comparisons, cumulative savings growth, category breakdown, and automatically generated financial insights.

![Analytics — Monthly Breakdown & Insights](screenshots/analytics-2.png)

### Budget Planner
Set an overall or category-specific monthly limit and track usage in real time.

![Budget Planner](screenshots/budget-planner.png)

### Savings Goals
Create named goals with a target amount and track progress as you save.

![Savings Goals](screenshots/savings-goals.png)

## Future Improvements

The following are planned enhancements and are **not** currently implemented:

- AI-generated financial insights
- AI-powered expense categorization
- Personalized budgeting assistant
- Monthly expense prediction
- Cash-flow forecasting
- Advanced savings recommendations
- OCR-based receipt scanning
- User authentication
- PostgreSQL or MongoDB integration
- Cloud deployment
- Multi-user support
- Improved data validation
- Automated testing

## Learning Outcomes

This project demonstrates:

- Python application development
- Streamlit dashboard development
- Data processing using Pandas
- CSV-based data management
- Financial data analysis
- Interactive data visualization with Plotly
- User-interface customization with custom CSS
- CRUD-style transaction operations
- File-based report generation (PDF with fpdf2, Excel with openpyxl)

## Author

**Sriram M**

- GitHub: [sriram-dev00](https://github.com/sriram-dev00)
- LinkedIn: [Sriram M J](https://www.linkedin.com/in/sriram-m-j-5491a7322/)
- LeetCode: [sriram221](https://leetcode.com/u/sriram221/)

## Contributing

Contributions are welcome. To contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature-name`).
3. Make your changes and commit them (`git commit -m "Add your feature"`).
4. Push to your branch (`git push origin feature/your-feature-name`).
5. Open a pull request describing your changes.

## License

This project is currently intended for educational and portfolio purposes.
