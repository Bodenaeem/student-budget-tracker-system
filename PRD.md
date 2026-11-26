# Product Requirements Document: Smart Budget Tracker

| Field | Value |
| --- | --- |
| Product | Smart Budget Tracker |
| Document revision | 1.0 |
| Updated | November 18, 2026 |
| Current application label | v2.0 |
| Product stage | Personal/demo application with proposed improvements |
| Implementation baseline | `Smart_Budget_Tracker_Professional.py`, `budget_assistant.py`, and local assets |

## 1. Product overview

Smart Budget Tracker helps individuals record income and expenses, understand monthly spending, set spending limits, and track savings goals in Malaysian Ringgit (RM). It provides a browser interface powered by Streamlit and persists financial records in a local SQLite database.

This PRD documents the existing product and proposes requirements for its next improvement cycle. **Implemented** means functionality exists in the current code, not that every acceptance criterion has been fully tested. **Partial** means functionality exists with a known gap. **Proposed** means work remains and has no committed delivery date.

## 2. Problem and intended users

People who manually track finances need a consistent way to record transactions, identify spending patterns, and compare expenses with a monthly limit. Separate notes and spreadsheets can make those tasks repetitive and difficult to review together.

The intended audience is individuals managing personal budgets in RM, including students tracking allowances or scholarships and earners tracking salaries or other income. The current deployment model serves one personal dataset. It does not support separate records for multiple users.

| User need | Product response |
| --- | --- |
| “Where did my money go this month?” | Monthly totals and spending by category. |
| “Am I staying within my limit?” | A monthly budget, remaining amount, and usage alerts. |
| “Can I correct a record?” | Searchable transaction history with editing and deletion. |
| “How close am I to my target?” | Manually maintained savings totals and progress indicators. |
| “Can I review my records elsewhere?” | CSV downloads for transactions, budgets, and goals. |
| “Can I discuss a budgeting calculation?” | A local conversational assistant with follow-ups, missing-input questions, and financial calculators. |

## 3. Goals and scope

### Product goals

1. Make manual income and expense recording straightforward.
2. Present consistent monthly totals across the dashboard, reports, and assistant.
3. Make budget usage and savings progress easy to interpret.
4. Preserve records between application sessions.
5. Keep core functionality usable without paid APIs or external data services.

### Current scope

The product includes the demo login, nine navigation pages, transaction management, budgets by month, manual savings tracking, charts, CSV exports, a rule-based assistant, and a shared light/dark visual theme.

### Outside the current scope

- Bank connections, payment processing, and automatic transaction imports.
- Multiple currencies or currency conversion.
- Investment management, tax preparation, and accounting compliance.
- Multiple user accounts, household roles, and shared budgeting permissions.
- Automatic savings transfers, contribution ledgers, and recurring transactions.
- An external language model or unrestricted financial advice.
- Native mobile applications and cloud synchronization.

These are scope boundaries for the current product, rather than promises of future implementation.

## 4. Primary user journeys

### Record and review a transaction

1. Log in using the demo credentials.
2. Select Add Income or Add Expense.
3. Enter a positive amount, select a category and date, and optionally add a description.
4. Save the transaction.
5. Find the saved record in Transaction History and see its effect on the relevant month's totals.

### Manage a monthly budget

1. Open Budget Management and select a date in the desired month.
2. Save a non-negative monthly limit.
3. Review that month's spending and remaining budget.
4. Review threshold alerts on the Dashboard when the budget belongs to the current month.

### Track a savings goal

1. Create a named goal with a positive target.
2. Optionally choose a deadline; the current deadline form needs correction.
3. Replace the total saved as progress changes.
4. View progress and a completion message when the saved total reaches the target.

Savings tracking remains independent of transaction accounting. The interface must explain that recording savings does not deduct money from net balance.

### Review and export records

1. Filter transactions or choose a reporting month.
2. Review matching records, totals, and charts.
3. Download the relevant CSV, or export complete datasets through Download Reports.

## 5. Functional requirements

The acceptance criteria below describe required behavior. They form a validation checklist; they are not a statement that the current implementation passes every case.

| ID | Requirement | Current status | Acceptance criteria |
| --- | --- | --- | --- |
| FR-01 | Provide a login gate and sign-out action. | Implemented for demo use | Correct demo credentials open the app; incorrect credentials show an error; sign-out returns to login. Production authentication is a separate proposed requirement. |
| FR-02 | Record income and expenses. | Implemented | Each record has a type, amount of at least RM 0.01, category, optional description, and date; saving persists it once and makes it available in history. |
| FR-03 | Show the current month's financial overview. | Implemented | Income and expense totals match transactions for the current server month; net balance equals their difference; recent activity shows up to five records ordered by date and ID descending. |
| FR-04 | Store one budget per month. | Implemented | Saving again for the same month updates that month's amount; other months retain their amounts; zero disables usage alerts. |
| FR-05 | Display budget usage and alerts. | Implemented | For a positive current-month budget, show usage and remaining budget; messages change at 50%, 80%, and 100%; the progress bar caps at 100% while the numeric usage may exceed it. |
| FR-06 | Search and filter transactions. | Implemented | Type, category, month, and case-insensitive description/category search combine; the count and CSV reflect the same filtered records. |
| FR-07 | Edit and delete transactions. | Implemented | Changes update the chosen record and relevant totals; blank categories are rejected; deletion requires the confirmation checkbox. |
| FR-08 | Create and maintain savings goals. | Partial | A nonblank name and target of at least RM 1 are required; saved total is non-negative; progress caps visually at 100%; a selected deadline is available before submission and is stored accurately. The deadline criterion currently fails. |
| FR-09 | Confirm destructive goal actions. | Proposed | Deleting a goal requires explicit confirmation; cancellation leaves it unchanged. Current goal deletion is immediate. |
| FR-10 | Provide monthly reporting. | Partial | Show income, expenses, net balance, category spending, and transactions for the selected month. A proposed extension adds that month's budget, remaining budget, and zero-activity months in trends. |
| FR-11 | Export financial datasets. | Implemented | Provide CSV downloads for all transactions, filtered transactions, selected-month transactions, goals, and budgets, including column headers when datasets are empty. |
| FR-12 | Answer supported local finance questions. | Implemented for supported rules | Supported questions use the requested month and local records; income, expenses, budget, balance, categories, and goals match their underlying data; every displayed suggestion returns its intended topic. Short month/category follow-ups retain context. |
| FR-13 | Handle unsupported assistant input. | Implemented | Unmatched questions receive supported examples; the assistant explains its rule-based limits and cannot change financial records. |
| FR-14 | Preserve records locally. | Implemented | Data remains after restarting; missing database tables are created after login; creating an empty database does not require manual SQL. |
| FR-15 | Apply a consistent visual theme. | Implemented; browser validation pending | Login and application pages use shared local styling; light/dark changes keep controls and charts readable; navigation and forms remain usable on smaller screens. |
| FR-16 | Calculate savings plans conversationally. | Implemented | Given a target, saved amount, and either timeframe or monthly contribution, calculate the missing result; ask for missing inputs; use an existing named goal when requested; retain inputs across follow-ups and disclose zero-saved/no-interest assumptions. |
| FR-17 | Explore affordability and cash-flow scenarios. | Implemented | A purchase query compares its price with the selected month's recorded surplus and budget. Explicit income/expense inputs create a separate hypothetical monthly scenario, with missing values requested and no database changes. |
| FR-18 | Estimate daily allowances and loan payments. | Implemented | Divide a positive remaining current-month budget over days left including today; estimate a fixed-rate reducing-balance loan payment from principal, annual rate, and whole-month term, disclosing assumptions and exclusions. |
| FR-19 | Provide bounded arithmetic. | Implemented | Calculate supported arithmetic, percentages, and selected-month variables using decimal values; reject division by zero, unsupported syntax, executable code, oversized expressions, and values outside the supported range. |
| FR-20 | Manage conversation context. | Implemented | Maintain context during page navigation; clear chat and context through Clear conversation or sign-out; `start over` clears context while retaining the transcript; switching topics cancels unrelated pending inputs. |
| FR-21 | Prepare an expense from a receipt photo. | Implemented with local OCR | Add Expense accepts JPG/PNG/WebP photos up to 10 MB and 20 megapixels; local Apple Vision or Tesseract extracts merchant, final total, and purchase date; show the photo beside editable fields; flag missing/ambiguous fields and currencies; require a merchant, positive RM amount, date, category, and explicit confirmation before saving. Save the merchant and optional notes in the expense description. Matching date/amount expenses require separate duplicate acknowledgment. Replacing/discarding/removing the photo, failed rescanning, successful saving, and sign-out clear the draft; database save failure preserves it. No photo or raw OCR text is persisted. |

## 6. Financial and data rules

### Calculations

| Measure | Rule |
| --- | --- |
| Monthly income | Sum amounts where type is Income and the transaction date belongs to the month. |
| Monthly expenses | Sum amounts where type is Expense and the transaction date belongs to the month. |
| Net balance | Monthly income minus monthly expenses. |
| Remaining budget | Monthly budget minus monthly expenses. |
| Budget usage | Monthly expenses divided by a positive monthly budget, multiplied by 100. |
| Goal progress | Saved total divided by target, multiplied by 100; visual progress caps at 100%. |

For example, RM 2,000 income, RM 600 expenses, and an RM 800 budget produce an RM 1,400 net balance, RM 200 remaining budget, and 75% usage. A goal with RM 150 saved toward RM 500 is 30% complete. These are illustrative values, not project records.

The monthly balance has no opening balance or bank reconciliation. Transactions are included according to their recorded date; the current implementation does not exclude future-dated entries within the month. Goal savings do not create expense records. Goal saved totals may exceed their targets.

### Current data model

| Entity | Fields and current constraints |
| --- | --- |
| `transactions` | Auto-increment integer `id`; `type` restricted to Income/Expense; positive `amount` as `REAL`; required `category`; `description` defaulting to an empty string; required `date` text. |
| `budgets` | `month` text primary key; `amount` as `REAL` defaulting to zero. The UI enforces a non-negative amount; the schema has no equivalent check. |
| `savings_goals` | Auto-increment integer `id`; required `name`; positive `target` as `REAL`; non-negative `saved` as `REAL` defaulting to zero; optional `deadline` text. |

The app writes dates as `YYYY-MM-DD` and budget months as `YYYY-MM`. Some requirements are enforced in the interface rather than by database constraints. Chat messages, assistant context, receipt images/drafts, and login state are held in Streamlit session state. Receipt merchant names and optional notes use the existing expense description field; raw photos and OCR text are not stored in SQLite. No user ownership fields exist. Assistant calculators use decimal arithmetic with a 1 trillion magnitude limit, but transaction storage and the rest of the application's calculations still use floats.

## 7. Quality requirements

| ID | Requirement | Current position / proposed verification |
| --- | --- | --- |
| QR-01 | Consistent financial results | Verify representative monthly calculations across Dashboard, Budget Management, Monthly Reports, and the assistant using the same fixture dataset. |
| QR-02 | Exact monetary precision | Proposed: store integer sen and use exact monetary calculations; migrate existing records with documented rounding and reconciliation checks. Current storage uses floats. |
| QR-03 | Reliable persistence and recovery | Verify restart persistence; document manual database backup/restore; propose a guided backup/restore workflow with a successful round-trip check. |
| QR-04 | Local operation | After installing dependencies, core pages, local assets, charts, and assistant responses must work without an external API. Verify in an offline browser session. |
| QR-05 | Clear validation and failure behavior | Proposed: invalid inputs and database failures show actionable messages and do not leave partially saved operations. Database error handling is currently limited. |
| QR-06 | Readable and accessible interaction | Verify keyboard navigation, visible focus, labels, contrast, and form usability in both themes at desktop and mobile viewport sizes. Current CSS includes focus and responsive styles; full validation remains pending. |
| QR-07 | Reproducible setup | Python dependency pins and Linux OCR package declarations are provided. A fresh dependency installation remains unverified. |
| QR-08 | Practical local performance | Proposed target: dashboard and history interactions complete within two seconds with 10,000 transactions on a documented test machine. This target has not been benchmarked. |
| QR-09 | Safe shared deployment | Proposed deployment gate: replace demo credentials with proper authentication, enforce record ownership, define session behavior, and document persistent hosting storage before using shared hosting with real records. |

## 8. Architecture and constraints

The main Python script contains page rendering, SQLite access, and dashboard/report calculations. The separate `budget_assistant.py` module handles conversation rules and financial calculators without database writes or network calls. Streamlit handles the browser interface and session state. pandas prepares tables and CSVs; Altair and Plotly render charts. The local CSS and theme bridge customize Streamlit's interface.

`receipt_scanner.py` validates and normalizes photos through Pillow, invokes local Apple Vision using `receipt_ocr.swift` on macOS (when Swift is available) or the Tesseract command-line engine on other systems, and parses a conservative draft without database access. `receipt_ui.py` owns upload/review state, duplicate warnings, and explicit confirmation, calling the main app's transaction helper only after validation. Receipt content is passed to OCR through stdin. An unavailable OCR engine leaves manual entry usable and displays setup guidance. OCR has a 45-second timeout; large images are resized before recognition. This feature makes no external OCR requests and requires no API key.

The SQLite file lives beside the script and requires write access. All sessions use that file. Data resides on whichever machine runs Streamlit, which may differ from the browser's machine. Deployments with temporary filesystems would require a persistence plan.

Current-month calculations use the server's local date without an application-specific timezone setting. Large-dataset performance is unmeasured; the app loads all transactions on reruns and performs several aggregations in Python. Theme selectors depend on Streamlit's rendered structure, so upgrades require visual checks.

## 9. Known gaps and proposed priorities

Priority definitions: **P1** corrects misleading behavior or blocks safe shared deployment; **P2** improves reliability and completion; **P3** improves maintainability or extends convenience. These priorities are proposals, with no delivery commitments.

| Priority | Work item | Completion evidence |
| --- | --- | --- |
| Completed | Fix expense intent and greeting matching in the assistant. | Regression checks confirm the expense suggestion returns the correct total and greetings do not intercept “this month.” |
| P1 | Fix the optional goal deadline workflow. | Users can select a date before creating a goal; the exact selected date persists. |
| P1 before shared deployment | Replace the shared demo access model. | Independent accounts cannot access each other's records; deployment and session behavior are documented and tested. |
| P2 | Confirm goal deletion. | Cancel preserves the goal; confirmation removes only the selected goal. |
| P2 | Adopt exact money storage and calculations. | Migrated totals reconcile under a documented rounding rule; repeated small amounts aggregate exactly. |
| P2 | Complete budget comparison in monthly reporting. | Selected-month budget and remaining amount are visible, with clear handling for missing budgets and empty months. |
| P2 | Verify reproducible setup and extend regression coverage. | Dependency declarations, assistant checks, and receipt parser/confirmation checks are implemented; remaining work covers fresh setup, application-wide calculations, goal deadline persistence, and other transaction changes. |
| P2 | Improve database failure handling and backup recovery. | Simulated write failures preserve records; a backup restores transactions, budgets, and goals correctly. |
| P3 | Replace deprecated Streamlit sizing arguments and validate themes. | Relevant warnings are resolved and both themes remain usable in browser checks. |
| P3 | Further separate storage, finance calculations, and interface code as the project grows. | Assistant logic is already independent; future refactoring preserves existing behavior and expands independent validation. |

## 10. Validation and release criteria

### Evidence from the November 18, 2026 review

- Python syntax parsing passed.
- The existing SQLite database returned `ok` from its integrity check.
- Demo login and all nine pages rendered without Python exceptions in a temporary copy using Streamlit's testing API and sample data.
- The original review reproduced an incorrect expense-question response; the assistant update fixed it and added regression coverage.
- A form interaction reproduced goal creation with today's deadline before an intended date could be selected.

After the assistant update, 27 standard-library regression tests passed for calculations, conversation context, missing-input collection, date selection, and input validation. A Streamlit integration check passed chat follow-ups across page navigation, conversation clearing, and sign-out resets in a temporary app copy. A database hash check confirmed the original records were unchanged.

These checks did not establish complete end-to-end coverage, browser appearance, accessibility, fresh-install compatibility, or production readiness. Committed tests currently cover the assistant module; the deadline-form issue remains unresolved.

### Proposed gate for the next local-use release

1. Retain the assistant regression checks and fix the deadline defect with focused coverage.
2. Verify create/edit/delete persistence and dependent totals across pages.
3. Check budget behavior at zero, 50%, 80%, 100%, and above 100% usage.
4. Verify empty datasets, year-boundary month selection, CSV contents, and goal completion/over-target behavior.
5. Validate a fresh setup, manual backup/restore, and browser usability in both themes.

Shared deployment additionally requires QR-09. The performance target in QR-08 must be benchmarked before claiming support for that dataset size.

## 11. Success measures

These measures are proposed and have not yet been collected. The current application has no product analytics instrumentation.

| Measure | Proposed target / method |
| --- | --- |
| Financial consistency | Every representative fixture produces matching totals across relevant pages and assistant responses. |
| Suggested-question correctness | Every assistant suggestion returns the intended topic and correct fixture values. |
| Persistence | All record changes survive a restart in the validation scenario. |
| Export accuracy | Downloaded CSV rows and totals match the requested dataset. |
| First-use usability | At least four of five trial users can add income, add an expense, and set a budget without assistance. |
| Recovery | A backup/restore exercise reproduces the source database's records. |

## 12. Decisions to confirm before broader use

- Whether the product will remain a local personal tool or support shared hosting and multiple users.
- Which Python/package versions will be supported and how dependencies will be maintained.
- Which timezone defines the current month in a hosted environment.
- Whether savings should remain a manual total or gain a separate contribution history.
- Whether future versions need CSV import, recurring transactions, or configurable categories.

These decisions do not block the documented local/demo workflow. Setup and usage instructions are in [README.md](README.md).
