# Smart Budget Tracker

A personal finance application built with Python and Streamlit. Record income and expenses in Malaysian Ringgit (RM), set monthly budgets, track savings goals, explore spending charts, and export records to CSV.

The application stores records in a local SQLite database and includes a rule-based budget assistant that runs without an external AI service or API key.

**Project status:** working personal/demo application. The interface identifies the app as v2.0. Authentication uses a shared demo account; the application does not currently provide separate user accounts or data isolation.

## Features

| Page | What you can do |
| --- | --- |
| Dashboard | View current-month income, expenses, net balance, budget usage, spending charts, five recent transactions, and up to three savings goals. |
| Add Income | Record an amount, category, optional description, and transaction date. |
| Add Expense | Record spending manually, or upload a receipt photo, extract its merchant/total/date, and confirm an editable expense draft. |
| Budget Management | Save a separate spending limit for each month and view expenses and remaining budget. |
| Transaction History | Search descriptions and categories, filter by type/category/month, edit or delete transactions, and export filtered results. |
| Savings Goals | Create a goal, manually update the total saved, view progress, and delete a goal. An optional deadline field exists but has a known form issue. |
| Monthly Reports | Review a selected month's transactions and totals, category spending, and income/expense trends across recorded months. |
| Download Reports | Export all transactions, savings goals, and monthly budgets as separate CSV files. |
| Budget Assistant | Discuss recorded finances, follow up on a month/category, calculate savings plans and loan payments, and explore purchases or monthly income/expense scenarios. |

The interface uses a shared glass theme with local background assets and light/dark theme synchronization. See [the asset notes](assets/README.md) for details.

## Technology

| Component | Technology |
| --- | --- |
| Application and interface | Python, Streamlit |
| Data tables and CSV generation | pandas |
| Bar and trend charts | Altair |
| Spending breakdown chart | Plotly Express |
| Persistent storage | SQLite through Python's built-in `sqlite3` module |
| Receipt scanning | Pillow image validation; local Apple Vision on macOS or Tesseract OCR on other systems |
| Theme | Local CSS, HTML/JavaScript, and image assets |

No Node.js build step, cloud database, or AI API key is required to run the current application.

## Getting started

Run the following commands from the project directory. Keep the Python files, `receipt_ocr.swift`, and the `assets/` directory together.

### 1. Create a virtual environment

On macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

The environment inspected during the project review used Python **3.9.6**. `requirements.txt` pins the observed Python dependencies, including Pillow for receipt images. A fresh installation and compatibility with other environments have not been verified.

```bash
python -m pip install -r requirements.txt
```

SQLite and the remaining Python modules used by the app are included with Python. Internet access is needed to download dependencies; the application's core features use local resources afterward. Receipt scanning also needs a local OCR engine; see below.

### 3. Start the application

```bash
python -m streamlit run Smart_Budget_Tracker_Professional.py
```

Open the local address printed in the terminal, normally `http://localhost:8501`. Press `Ctrl+C` in the terminal to stop the server.

### 4. Log in

| Field | Demo value |
| --- | --- |
| Username | `admin` |
| Password | `admin123` |

These credentials are hardcoded and also shown on the login screen. Use this setup for a local demonstration; shared deployment requires an authentication and data-isolation design.

## Suggested first use

1. Add income, such as a salary or allowance.
2. Add an expense with its category and transaction date.
3. Open **Budget Management** and set a budget for that month.
4. Review totals and budget alerts on the **Dashboard**.
5. Create a savings goal and manually update its saved total as you make progress.
6. Use **Transaction History** or **Monthly Reports** to review records and download CSV files.

Default income categories are Salary, Allowance, Scholarship, Business, and Other. Default expense categories are Food, Transportation, Shopping, Bills, Education, Entertainment, Health, and Other. Editing an existing transaction allows a custom category name.

## Receipt scanner

Open **Add Expense → Scan receipt** and upload a JPG, PNG, or WebP receipt photo (up to 10 MB and 20 megapixels). Click **Extract receipt details**, then check the merchant, final amount, purchase date, and expense category against the photo. Add optional notes, tick the confirmation box, and click **Confirm & save expense**. The merchant and optional notes are saved in the expense's description, so they appear in history, search, and reports without a database migration.

The scanner runs locally on the computer hosting Streamlit and requires no API key:

- **macOS:** uses [Apple Vision](https://developer.apple.com/documentation/vision/vnrecognizetextrequest) through the included Swift helper when Swift is available. Install Apple's Command Line Tools with `xcode-select --install` if needed. The first scan can take longer while Swift prepares its module cache.
- **Linux:** install [Tesseract](https://tesseract-ocr.github.io/tessdoc/Installation.html) and English language data, for example `sudo apt-get install tesseract-ocr tesseract-ocr-eng` on Debian/Ubuntu.
- **Windows:** install Tesseract with English language data and add its installation directory to PATH.
- **Streamlit Community Cloud:** `packages.txt` declares the Linux OCR packages. Other hosts need the OCR engine installed separately. Restart the app after installing an engine.

Missing fields remain empty and must be entered before confirmation. The parser prioritizes labeled final totals over subtotals, cash tendered, and change. It warns about conflicting totals or dates, ambiguous numeric dates (day/month/year is assumed), and unclear or foreign currencies. The tracker stores RM only: foreign receipt totals do not prefill the RM amount, and users must enter the RM equivalent themselves. No automatic currency conversion or category prediction is performed; the initial category is Other.

Scanning never creates a transaction on its own. Expenses with the same date and amount trigger a duplicate warning and need a separate acknowledgment to save. Replacing/removing/discarding the upload, a failed rescan, successful saving, or signing out clears the pending draft. A database save failure retains the draft for retrying. Manual entry remains available without an OCR engine.

Photos are validated from their contents, phone orientation is applied, and image metadata is removed before OCR. Receipt photos and extracted text stay in the active session and are not stored in SQLite or sent to an external OCR service. The application does not intentionally write receipt photos to disk; the Swift module cache contains compiler artifacts. Only confirmed expense fields are persisted. Scanning currently targets English/Latin-text receipts; blurry, handwritten, unusual-layout, or other-language receipts may need manual entry or correction. Browser layout and camera-specific behavior have not been verified.

## How calculations work

- **Monthly income/expenses:** sums of transactions dated in the selected month, or the current month on the Dashboard.
- **Net balance:** recorded income minus recorded expenses for that month. It does not include an opening account balance and does not represent a live bank balance.
- **Remaining budget:** the month's spending limit minus that month's recorded expenses. A negative result means spending exceeds the limit.
- **Budget alerts:** the Dashboard shows messages at 50%, 80%, and 100% usage. A zero budget disables usage alerts.
- **Savings goals:** saved amounts are entered manually and are independent of transaction balances. Updating a goal replaces its saved total; it does not add a contribution transaction.

The current month comes from the date of the machine running the Python server. Amounts display to two decimal places but are currently stored and calculated using floating-point numbers.

## Budget assistant

The assistant uses local language rules, conversation context, and decimal-based calculations. It remembers the active topic, month, category, and calculator inputs within the current conversation, and asks for missing values. It cannot modify records, retrieve bank information, or understand arbitrary questions like a general-purpose language model.

Examples supported by the current rules:

```text
What is my balance?
Budget status
Expenses in 2026-10
How much did I spend on Food this month?
And last month?
Top spending category
Savings goals
Give me savings tips
Save RM 3,000 in 6 months
Already saved RM 600
What if RM 300 per month?
I earn RM 3,000 and spend RM 2,000. How much is left?
Can I afford RM 250?
How much can I spend per day?
Loan RM 10,000 at 6% over 3 years
Calculate (income - expenses) / 2
15% of 200
```

It supports explicit `YYYY-MM` dates, full or abbreviated English month names with an optional year, and references such as “last month.” Short follow-ups reuse the selected month or active calculator. Chat history and calculator context are held in Streamlit session state rather than stored in SQLite. **Clear conversation**, signing out, or a new browser session clears the relevant session conversation; `start over` resets calculator and topic context without deleting the visible transcript.

Savings plans assume no interest or fees and RM 0 already saved unless you provide a saved amount or name an existing goal. Loan estimates use a fixed annual nominal rate, monthly payments, and a reducing balance; they exclude fees, insurance, and lender-specific rounding. Daily allowances divide the current month's remaining budget over days left, including today. Hypothetical income/expense scenarios use the numbers you supply and identify them separately from stored records. No calculation changes the database.

Arithmetic accepts numbers, percentages, `+`, `-`, `*`, `/`, parentheses, and the variables `income`, `expenses`, `balance`, `budget`, and `remaining` for the conversation's selected month. It validates an arithmetic syntax tree and does not execute Python supplied through chat. Monetary inputs and arithmetic results are bounded to 1 trillion in magnitude. Amounts in conversational calculators can use `k` for thousands, such as `3k`.

## Project structure

```text
.
├── Smart_Budget_Tracker_Professional.py  # Application interface and database helpers
├── budget_assistant.py                 # Conversation rules and financial calculators
├── receipt_scanner.py                  # Image validation, local OCR, and receipt parsing
├── receipt_ui.py                       # Upload and editable confirmation workflow
├── receipt_ocr.swift                   # Local macOS Apple Vision helper
├── requirements.txt                    # Python dependency pins
├── packages.txt                        # Linux OCR packages for Streamlit Cloud
├── smart_budget_tracker.db              # Local financial records
├── README.md                           # Setup and usage guide
├── PRD.md                              # Product requirements and improvement priorities
├── tests/
│   ├── test_budget_assistant.py          # Conversation and calculation regression checks
│   ├── test_receipt_scanner.py           # Receipt parsing, image validation, and OCR errors
│   └── test_receipt_ui.py                # Confirmation, duplicate checks, and isolated saving
├── .streamlit/
│   └── config.toml                      # Streamlit configuration
└── assets/
    ├── glass-theme.css                  # Shared interface styling
    ├── graphite-texture.png             # Active background texture
    ├── theme-sync.html                  # Light/dark theme bridge
    ├── warm-interior.jpg                # Previous optional background
    └── README.md                        # Theme and asset notes
```

## Storage and backups

The app opens `smart_budget_tracker.db` beside the Python file. If the database is missing, it creates the database and its tables after a successful login. The project directory must be writable.

The database contains three application tables: `transactions`, `budgets`, and `savings_goals`. There is no user table or built-in database encryption. When hosted, “local storage” means storage on the server running Streamlit.

To back up records, stop the application and copy `smart_budget_tracker.db` to a safe location. To restore, stop the application, preserve a copy of the current database, replace it with the backup under the same filename, and restart. CSV downloads are useful for analysis, but the app has no CSV import or automated restore feature.

The database is not currently excluded by `.gitignore`. Check that real financial records are excluded before sharing or publishing the project.

## Known limitations

| Area | Current limitation |
| --- | --- |
| Authentication | One shared demo login; no registration, password management, or user-specific records. |
| Assistant language | Local rules handle supported topics, rather than unrestricted language understanding. Use explicit amounts and units, and rephrase if asked. |
| Goal deadlines | Enabling the deadline checkbox inside the form can save today's date before the user can select their intended date. |
| Goal deletion | Clicking Delete Goal immediately removes the record without confirmation or undo. |
| Monthly reporting | The page mentions budget comparison, but its metrics and trend chart currently compare income and expenses only. Months without transactions are omitted from trends unless they are the current month. |
| Monetary precision | SQLite `REAL` columns and Python floats can introduce rounding differences; integer sen storage is a proposed improvement. |
| Recovery | Database backup and restore are manual; no import workflow is provided. |
| Maintenance | Assistant and receipt regression tests exist; broader application coverage and fresh dependency installation remain unverified. Streamlit currently emits warnings for `use_container_width`. |

## Validation and roadmap

Run assistant and receipt checks using Python's standard-library test runner:

```bash
python -m unittest discover -s tests -v
```

During the November 18, 2026 review, Python syntax parsing and the existing database's SQLite integrity check passed. Following the assistant update, 27 regression tests passed, covering follow-ups, savings and loan calculations, cash-flow scenarios, month selection, invalid inputs, and safe arithmetic. A temporary copy also passed login and rendering checks for all nine pages, chat follow-ups across page navigation, and conversation/sign-out resets. The original financial database remained unchanged. The separately identified goal deadline issue remains unresolved. Browser layout, accessibility, and a fresh dependency installation were not validated by those checks.

Following the receipt update, all 58 regression tests passed. Receipt verification adds parser and image checks plus Streamlit AppTest checks for draft-only extraction, editable confirmation, required fields, foreign currencies, duplicates, upload changes, failed OCR, save failure, and sign-out cleanup. The database integration check saves into a temporary copy of the application and confirms the expense appears in Transaction History. An actual Apple Vision smoke test on a generated receipt extracted SUNRISE CAFE, RM 31.80, and November 18, 2026 correctly. Apple Vision requires execution outside the development tool's sandbox; the normal local app uses the host framework. Tesseract execution and browser layout remain unverified.

See [PRD.md](PRD.md) for product goals, functional requirements, acceptance criteria, and proposed priorities. This README documents the current implementation; roadmap items are not implemented features.
