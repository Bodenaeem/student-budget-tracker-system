💰 Smart Budget Tracker System

A simple, user-friendly, and efficient personal finance and budget management application designed to help university students and individuals take control of their daily expenses, track income, and build better financial habits.

Developed as a project for the Diploma in Information Systems at City University Malaysia.

🚀 Features

Income Management: Easily add, edit, and delete income records.

Expense Tracking: Record daily expenses and organize them into clear categories (e.g., Food, Transportation, Shopping, Bills, Entertainment).

Budget Management: Set monthly spending limits and monitor your ongoing expenses against those targets in real-time.

Automated Balance Calculation: Instantly calculates total income, total expenses, and your remaining balance.

Financial Reports & Analytics: View interactive financial summaries, category breakdowns, and simple charts to understand spending habits.

Transaction History: Review all previous income and expense logs seamlessly.

🛠️ Tech Stack & Tools

The system is built using lightweight, efficient, and modern technologies suitable for rapid development and clean architecture:

Programming Language: Python

User Interface: Streamlit

Code Editor: Visual Studio Code

System Design & Modeling: Draw.io (for DFDs and Use Case diagrams)

📱 User Interface Mockup Preview

The user interface is designed to be clean, intuitive, and responsive using Streamlit:

+----------------------------------------+  +----------------------------------------+
| ☰      Expenses   |   Income       🔍  |  | ❮                         ✔      🗑️    |
| 2026   September 2025   Last Month [This]|  | Overview                               |
|                                        |  | Entertainment             November     |
|         /------------------\           |  | ⛃                         13 days      |
|        /     Spent          \          |  | €30.8       €69.2          €100        |
|       |     €34.3            |         |  | 30.8% Spent Remaining                  |
|        \                    /          |  | Budget Analysis                        |
|         \------------------/           |  | ------------------------------------   |
|                                        |  | Suggested Daily: €3.45                 |
| 🔴 Food                   €25.5 (76%)  |  | Current Daily Avg: €1.81               |
| 🟣 Entertainment           €8.8 (25%)  |  | Transactions                           |
|                                        |  | ⛃ Entertainment             -€22.00    |
+----------------------------------------+  +----------------------------------------+


⚙️ Software Development Life Cycle (SDLC)

The project follows a structured SDLC approach:

Requirements Analysis: Identifying student financial pain points and functional requirements.

System Design: Creating Use Case and Data Flow Diagrams (DFD).

Implementation: Writing core Python logic and building the Streamlit UI.

Testing: Validating transaction entries, calculation accuracies, and UI responsiveness.

Evaluation & Documentation: Final system review, report compilation, and presentation preparation.

📂 Project Structure

smart-budget-tracker/
│
├── assets/             # UI mockups, screenshots, and diagrams
├── src/                # Source code (Python & Streamlit components)
│   ├── app.py          # Main Streamlit application entry point
│   └── utils.py        # Calculation and helper logic
│
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation


🚀 Getting Started & Installation

Prerequisites

Python 3.8+ installed on your machine.

Installation Steps

Clone the repository:

git clone https://github.com/your-username/smart-budget-tracker.git
cd smart-budget-tracker


Install dependencies:

pip install -r requirements.txt


Run the Application:

streamlit run src/app.py


⏱️ Project Timeline (8 Weeks)

Week 1: Requirements gathering and problem analysis

Week 2: System design and preparation of diagrams

Week 3: System structure & state management setup

Week 4: Development of income and expense features

Week 5: Development of budget management and dashboard

Week 6: Development of reports and charts

Week 7: System testing and error correction

Week 8: Final documentation and presentation

👥 Author

Student Name: Abdelrahman Ahmed

Student ID: 202505010030

Course: Diploma in Information System

Institution: City University Malaysia

Supervisor/Lecturer: [SA-73]

📚 References

Pressman, R. S., & Maxim, B. R. (2020). Software engineering: A practitioner's approach (9th ed.). McGraw Hill.

Sommerville, I. (2016). Software engineering (10th ed.). Pearson.

Python Software Foundation. Python documentation. https://docs.python.org/3/

Streamlit. Streamlit documentation. https://docs.streamlit.io/
