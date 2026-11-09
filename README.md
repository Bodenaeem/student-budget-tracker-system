# 💰 Smart Budget Tracker

### Personal Finance Management System with a Free Budget Assistant

Smart Budget Tracker is a Python-based personal finance management web application developed using **Streamlit**. It helps users manage their income, track expenses, set monthly budgets, monitor savings goals, and understand their financial habits through an interactive and user-friendly dashboard.

The application features a modern **purple-themed glass-style interface**, a responsive layout for mobile phones, tablets, laptops, and desktops, local SQLite database storage, interactive financial charts, and a free rule-based Budget Assistant that provides insights based on recorded financial data.

The latest version introduces an improved login interface, enhanced dashboard styling, responsive layouts, better financial visualizations, and an upgraded user experience across different screen sizes.

---

## 🚀 Features

### 📊 1. Interactive Financial Dashboard

- View total monthly income, expenses, and remaining balance.
- Monitor monthly financial performance.
- Visualize spending patterns using interactive charts.
- Track monthly budget usage with progress indicators.
- Receive notifications when spending approaches or exceeds the budget.
- Display recent financial transactions.
- Monitor savings goal progress.
- View spending distribution by category.

**Dashboard Visualizations:**
- Interactive donut chart for spending breakdown.
- Bar chart comparing expense categories.
- Budget progress indicators.
- Financial summary cards.

### 💵 2. Income and Expense Management

- Add income and expense transactions.
- Organize transactions into categories.
- Record transaction dates and descriptions.
- Edit or delete existing transactions.
- Maintain a detailed financial transaction history.
- View and filter financial records.
- Export filtered transaction data to CSV.

### 🎯 3. Budget Management

- Set monthly spending budgets.
- Compare actual spending against the monthly budget.
- Monitor remaining budget amounts.
- Receive alerts when spending reaches 80% of the budget.
- Identify when monthly expenses reach or exceed the allocated budget.
- Display budget usage percentages.
- Monitor spending through progress bars.

### 🏦 4. Savings Goals

- Create personal savings goals.
- Set target savings amounts.
- Record current savings progress.
- Assign target deadlines.
- Monitor progress toward financial goals.
- View savings progress percentages.
- Delete savings goals when no longer needed.

### 📅 5. Monthly Financial Reports

- Review income and expenses for selected months.
- Analyze monthly financial performance.
- Track spending by category.
- Compare income and expenses.
- Visualize financial trends across multiple months.
- Display monthly income and expense line charts.
- Export monthly transaction reports as CSV files.

### 🤖 6. Free Rule-Based Budget Assistant

The application includes a built-in financial assistant that helps users understand their financial information without requiring paid AI services.

**Assistant Capabilities:**

- Answer questions about monthly income and expenses.
- Display recorded monthly financial balances.
- Provide monthly budget status.
- Identify top spending categories.
- Show savings goal information.
- Offer general savings suggestions.
- Understand questions about previous months.
- Support questions containing specific months and years.
- Maintain conversation history during the active session.
- Provide suggested questions for quick interaction.
- Allow users to clear their conversation history.

**Example Questions:**

- How much did I spend this month?
- What is my balance?
- What is my budget status?
- What is my top spending category?
- Show my savings goals.
- Give me savings tips.
- How much did I spend last month?
- What were my expenses in October 2026?

**Assistant Technology:**

The Budget Assistant uses predefined Python rules and financial calculations rather than an external AI model.

It does not require an API key or paid subscription and works with financial information stored in the local database.

---

## 🆕 7. Fully Responsive Website Design

Smart Budget Tracker now includes a responsive website design that automatically adjusts its layout based on the user's screen size.

The application supports:

- 📱 Mobile phones
- 📱 Tablets
- 💻 Laptops
- 🖥️ Desktop computers

**Responsive Design Improvements:**

- Automatic layout adjustment for different screen sizes.
- Mobile-friendly navigation and sidebar.
- Dashboard cards that adapt to available screen space.
- Financial charts that adjust to smaller screens.
- Forms that stack vertically on mobile devices.
- Responsive typography and headings.
- Improved spacing and padding.
- Mobile-friendly buttons and input fields.
- Better readability on small screens.
- Reduced horizontal overflow.

**Responsive Breakpoints:**

| Device | Screen Width | Layout |
|---|---|---|
| Mobile | Up to 700px | Single-column layout |
| Tablet | 701px–1024px | Flexible two-column layout |
| Laptop | Above 1024px | Expanded desktop layout |
| Desktop | Large screens | Full-width dashboard layout |

The responsive design is implemented using **CSS media queries, flexible layouts, and Streamlit components**.

---

## 🔐 8. Login and Authentication Interface

The application includes a customized login page that provides an entry point to the financial dashboard.

**Login Features:**

- Username and password input fields.
- Password masking.
- Login validation.
- Error messages for incorrect credentials.
- Session-based login status.
- Logout functionality.
- Responsive login form.
- Modern financial-themed login design.

**Demo Login Credentials:**

```text
Username: admin
Password: admin123
```

**Note:** The current login system uses predefined demo credentials. It is intended for local demonstration rather than production-grade authentication.

---

## 🎨 9. Modern Purple-Themed User Interface

The application features an improved visual design inspired by modern financial dashboard applications.

**UI Improvements:**

- Purple gradient navigation sidebar.
- Glass-style dashboard cards.
- Semi-transparent interface elements.
- Customized financial background.
- Modern login page with financial illustrations.
- Rounded buttons and input fields.
- Gradient action buttons.
- Improved typography.
- Consistent colors across application pages.
- Modern forms with subtle shadows.
- Improved spacing and visual organization.

The interface uses **custom CSS integrated with Streamlit** to create a consistent experience across the application.

---

## 📈 10. Advanced Financial Visualizations

Smart Budget Tracker uses interactive charts to help users better understand their financial activity.

**Available Charts:**

**Donut Chart**
- Displays expense distribution by category.
- Helps identify major spending areas.
- Uses Plotly for interactive visualization.

**Bar Chart**
- Compares spending across expense categories.
- Makes it easier to identify high-expense categories.

**Line Chart**
- Displays monthly income and expense trends.
- Helps users compare financial performance across months.

**Budget Progress Bar**
- Displays monthly budget usage.
- Helps users identify when spending approaches the budget limit.

---

## 💾 11. Local SQLite Database Storage

The application uses SQLite to store financial information locally.

**Stored Information:**

- Income transactions.
- Expense transactions.
- Monthly budgets.
- Savings goals.
- Transaction dates and descriptions.

**Database Features:**

- Automatic database initialization.
- Persistent local data storage.
- Transaction updates and deletion.
- Structured financial records.
- No external database server required.

The database is stored in:

```text
smart_budget_tracker.db
```

The database file is created locally when the application initializes.

---

## 📥 12. Financial Data Export

Users can export their financial records as CSV files.

**Available Exports:**

- All financial transactions.
- Filtered transaction history.
- Monthly financial transactions.
- Savings goals.
- Monthly budgets.

Exported CSV files can be opened using Microsoft Excel, Google Sheets, or other spreadsheet applications.

---

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| Streamlit | Web application framework |
| SQLite | Local database storage |
| Pandas | Financial data processing |
| Plotly | Interactive donut charts |
| HTML | Custom interface elements |
| CSS | Styling and responsive layouts |
| Python datetime | Transaction dates and monthly calculations |
| Python calendar | Month-based financial queries |
| Python re | Rule-based question matching |

---

## ⚙️ Installation and Setup

### Step 1: Install Python

Make sure Python is installed on your computer.

Check the installed version:

```bash
python3 --version
```

### Step 2: Install Required Libraries

Open your terminal and run:

```bash
python3 -m pip install streamlit pandas plotly
```

### Step 3: Download the Project

Download the project files or clone the GitHub repository.

### Step 4: Open the Project Folder

Navigate to the folder containing the Python application.

### Step 5: Run the Application

If the application file is named `app.py`, run:

```bash
python3 -m streamlit run app.py
```

If using the provided responsive source file, run:

```bash
python3 -m streamlit run "Smart_Budget_Tracker_Responsive(1).py"
```

### Step 6: Open the Website

Streamlit will display a local website address, usually:

```text
http://localhost:8501
```

Open the address in your browser.

### Step 7: Log In

Use the demo credentials to access the financial dashboard.

---

## 📱 Accessing the Website on Mobile Devices

Smart Budget Tracker can be opened in a mobile browser when the application server is reachable from the device.

To test the responsive website:

1. Run the Streamlit application on your computer.
2. Connect your phone and computer to the same Wi-Fi network.
3. Start Streamlit with network access enabled:

```bash
python3 -m streamlit run app.py --server.address 0.0.0.0
```

4. Find your computer's local IP address.
5. Open the following address on your phone:

```text
http://YOUR_COMPUTER_IP:8501
```

Replace `YOUR_COMPUTER_IP` with your computer's actual local IP address.

Your computer's firewall and network settings must allow the connection.

**Note:** The responsive website is still a Streamlit web application, not a native Android or iOS application.

---

## 📂 Project Structure

A simple project structure is:

```text
Smart-Budget-Tracker/
│
├── app.py
├── requirements.txt
├── README.md
│
└── smart_budget_tracker.db
    (Created automatically)
```

The Python application contains the dashboard, login interface, financial management functions, database operations, reports, and Budget Assistant.

---

## 🔒 Privacy and Data Storage

Smart Budget Tracker stores financial information in a local SQLite database.

- No external AI API is required.
- The Budget Assistant processes locally recorded financial information.
- Financial data is not automatically synchronized with bank accounts.
- Users can export their records.
- The SQLite database can be backed up manually.

The application is designed for personal finance tracking and educational demonstration.

For public deployment, stronger authentication and secure database management should be implemented.

---

## 🔄 Latest Updates

### Version 2.0 — Responsive UI and Dashboard Improvements

**New Features and Enhancements:**

- Added responsive layouts for phones, tablets, laptops, and desktops.
- Improved mobile compatibility using CSS media queries.
- Redesigned the login page.
- Added a modern purple glass-style interface.
- Improved the financial dashboard layout.
- Added an interactive donut chart for expense analysis.
- Improved category comparison charts.
- Enhanced financial metric cards.
- Improved sidebar navigation.
- Added session-based login and logout.
- Improved monthly financial reporting.
- Added CSV export options for financial records.
- Enhanced the free Budget Assistant with suggested questions and conversation history.
- Improved mobile forms, buttons, typography, and spacing.
- Added a customized financial background across the application.

---

## 🎯 Project Objectives

The main objectives of Smart Budget Tracker are:

1. Help users organize personal income and expenses.
2. Encourage better budgeting and financial planning.
3. Provide clear financial information through visual dashboards.
4. Help users monitor savings goals.
5. Offer free, rule-based financial assistance.
6. Provide an accessible financial management website across different devices.
7. Demonstrate practical Python web development, database integration, data visualization, and responsive UI design.

---

## 🚀 Future Improvements

Possible future developments include:

- Native Android and iOS mobile applications.
- Secure user registration and individual accounts.
- Cloud database synchronization.
- Multi-device financial data access.
- Recurring income and expense transactions.
- Additional financial charts and analytics.
- More advanced financial recommendations.
- Optional notifications and reminders.
- Improved authentication and account security.

---

## 📌 Conclusion

Smart Budget Tracker is a personal finance management application that combines budgeting tools, expense tracking, savings goal management, financial reporting, and a free Budget Assistant.

With its updated responsive design, modern purple-themed interface, interactive visualizations, and local SQLite storage, the application provides an accessible way to manage financial information.

The project demonstrates the practical use of **Python, Streamlit, SQLite, Pandas, Plotly, HTML, and CSS** in developing a functional and responsive financial management web application.

---

**💰 Smart Budget Tracker — Manage Your Money. Track Your Goals. Build Better Financial Habits.**
