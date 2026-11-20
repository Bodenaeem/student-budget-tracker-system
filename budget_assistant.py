"""Local conversational budgeting and calculators; no network or database writes."""

import ast
import calendar
import operator
import re
from decimal import Decimal, ROUND_CEILING


NUMBER = r"-?\d[\d,]*(?:\.\d+)?k?"
AMOUNT = rf"(?:rm\s*|myr\s*)?({NUMBER})"
MAX_VALUE = Decimal("1000000000000")


def decimal(value):
    text = str(value).replace(",", "").lower()
    result = Decimal(text[:-1]) * 1000 if text.endswith("k") else Decimal(text)
    if not result.is_finite() or abs(result) > MAX_VALUE:
        raise ValueError("Please use finite numbers of at most 1 trillion.")
    return result


def money(value):
    return f"RM {value:,.2f}"


def matches(pattern, question):
    return re.search(pattern, question, re.I)


def month_for(question, today, previous=None):
    explicit = matches(r"\b(20\d{2})-(\d{2})\b", question)
    if explicit:
        if not 1 <= int(explicit[2]) <= 12:
            raise ValueError("Choose a month from 01 to 12, for example 2026-10.")
        return explicit[0], True
    if matches(r"\b(this|current) month\b", question):
        return today.strftime("%Y-%m"), True
    if matches(r"\b(last|previous) month\b", question):
        year, month = today.year, today.month - 1
        return f"{year if month else year - 1:04d}-{month or 12:02d}", True
    for month in range(1, 13):
        if matches(r"\b(?:" + calendar.month_name[month] + "|" + calendar.month_abbr[month] + r")\b", question):
            year = matches(r"\b(20\d{2})\b", question)
            return f"{int(year[1]) if year else today.year:04d}-{month:02d}", True
    return previous or today.strftime("%Y-%m"), False


def calculate(expression, variables):
    """Evaluate only bounded numeric arithmetic and known financial variables."""
    expression = re.sub(r"\b(?:rm|myr)\s*", "", expression.lower()).replace(",", "")
    expression = expression.replace("×", "*").replace("÷", "/")
    expression = re.sub(r"(\d+(?:\.\d+)?)\s*%", r"(\1/100)", expression)
    if len(expression) > 180:
        raise ValueError("Please use a shorter calculation.")
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError:
        raise ValueError("Use numbers, +, -, *, /, parentheses, or income, expenses, balance and budget.") from None
    if sum(1 for _ in ast.walk(tree)) > 65:
        raise ValueError("Please use a shorter calculation.")
    operations = {ast.Add: operator.add, ast.Sub: operator.sub,
                  ast.Mult: operator.mul, ast.Div: operator.truediv}

    def evaluate(node):
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            result = decimal(ast.get_source_segment(expression, node))
        elif isinstance(node, ast.Name) and node.id in variables:
            result = variables[node.id]
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            result = evaluate(node.operand) * (-1 if isinstance(node.op, ast.USub) else 1)
        elif isinstance(node, ast.BinOp) and type(node.op) in operations:
            left, right = evaluate(node.left), evaluate(node.right)
            if isinstance(node.op, ast.Div) and right == 0:
                raise ValueError("I can't divide by zero. Please use a non-zero divisor.")
            result = operations[type(node.op)](left, right)
        else:
            raise ValueError("Use numbers, +, -, *, /, parentheses, or income, expenses, balance and budget.")
        return decimal(result)

    return evaluate(tree.body)


def savings(question, state, goals):
    slots = state.setdefault("slots", {})
    named = next((g for g in goals if matches(r"\b" + re.escape(g["name"]) + r"\b", question)), None)
    if named:
        slots.update(target=decimal(named["target"]), saved=decimal(named["saved"]))
    target = matches(rf"\b(?:save|target|goal|need)\s*(?:of|is|:|=|to)?\s*{AMOUNT}", question)
    saved = matches(rf"\b(?:already saved|have saved|saved so far|saved|currently have)\s*(?:is|:|=)?\s*{AMOUNT}", question)
    contribution = matches(rf"{AMOUNT}\s*(?:per|a|each|/)\s*month\b", question)
    duration = matches(rf"(?<![\w.])(?:(?:in|over|within|for)\s+)?({NUMBER})\s*(months?|years?)\b", question)
    if target and contribution and contribution.start() <= target.start(1) < contribution.end():
        target = None  # A monthly contribution alone is not also a target.
    for key, found in (("target", target), ("saved", saved), ("monthly", contribution)):
        if found:
            slots[key] = decimal(found[1])
    if duration:
        slots["months"] = decimal(duration[1]) * (12 if duration[2].startswith("year") else 1)
        slots.pop("monthly", None)
    elif contribution:
        slots.pop("months", None)
    if matches(rf"^\s*{AMOUNT}\s*(?:months?)?[.!]?\s*$", question):
        field = state.get("pending", "monthly")
        slots[field] = decimal(matches(AMOUNT, question)[1])
        if field == "monthly":
            slots.pop("months", None)
    if any(value < 0 for value in slots.values()):
        state["slots"] = {}
        state["pending"] = "target"
        return "Savings amounts and durations cannot be negative. What amount would you like to save?"
    if not slots.get("target"):
        state["pending"] = "target"
        return "What is your savings target in RM? For example, ‘save RM 3,000 in 6 months’."
    remaining = max(slots["target"] - slots.get("saved", Decimal(0)), Decimal(0))
    if remaining == 0:
        state.pop("pending", None)
        return "You have already reached that savings target. Would you like to plan another one?"
    assumptions = "Assuming no interest or fees" + (" and RM 0 already saved" if "saved" not in slots else "") + "."
    if "months" in slots:
        if slots["months"] <= 0:
            slots.pop("months")
            state["pending"] = "months"
            return "Over how many months? Please enter a number greater than zero."
        # Round up so the suggested monthly saving actually reaches the target.
        monthly = (remaining / slots["months"]).quantize(Decimal("0.01"), rounding=ROUND_CEILING)
        state.pop("pending", None)
        return (f"To reach {money(slots['target'])}, you still need **{money(remaining)}**. "
                f"Save **{money(monthly)} per month** for {slots['months']:g} months.\n\n"
                f"{assumptions} You can follow up with ‘already saved RM 500’ or ‘in 12 months’. This plan does not change your records.")
    if slots.get("monthly", Decimal(0)) > 0:
        months = (remaining / slots["monthly"]).to_integral_value(rounding=ROUND_CEILING)
        state.pop("pending", None)
        return (f"With **{money(slots['monthly'])} per month**, you need **{months:g} months** "
                f"to save the remaining {money(remaining)} toward {money(slots['target'])}.\n\n{assumptions} "
                "Try another monthly amount to compare. This plan does not change your records.")
    state["pending"] = "monthly"
    return (f"Your target is {money(slots['target'])}; {money(remaining)} remains. "
            "How much can you save per month, or over how many months? You can also tell me how much you have already saved.")


def loan(question, state):
    slots = state.setdefault("slots", {})
    principal = matches(rf"\b(?:loan|borrow|principal)\s*(?:of|is|:|=)?\s*{AMOUNT}", question)
    rate = matches(rf"({NUMBER})\s*%", question)
    duration = matches(rf"(?<![\w.])(?:(?:over|for|in)\s+)?({NUMBER})\s*(years?|months?)\b", question)
    if not state.get("pending") and matches(rf"^\s*{AMOUNT}\s*[.!]?\s*$", question):
        return "Is that a new loan amount, annual rate, or term? Try ‘loan RM 5,000’, ‘5%’, or ‘24 months’."
    if principal:
        slots["principal"] = decimal(principal[1])
    if rate:
        slots["rate"] = decimal(rate[1])
    if duration:
        slots["months"] = decimal(duration[1]) * (12 if duration[2].startswith("year") else 1)
    if state.get("pending") and matches(rf"^\s*{AMOUNT}\s*%?\s*(?:months?)?[.!]?\s*$", question):
        slots[state["pending"]] = decimal(matches(AMOUNT, question)[1])
    for field, prompt in (("principal", "How much would you borrow in RM?"),
                          ("rate", "What annual interest rate should I use? For example, ‘6%’. Enter ‘0%’ for an interest-free loan."),
                          ("months", "What is the loan term? For example, ‘over 3 years’ or ‘24 months’. A bare number means months.")):
        if field not in slots:
            state["pending"] = field
            return prompt
    if (slots["principal"] <= 0 or not 0 <= slots["rate"] <= 100
            or not 1 <= slots["months"] <= 1200 or slots["months"] != slots["months"].to_integral_value()):
        state["slots"] = {}
        state["pending"] = "principal"
        return "Use a positive loan amount, an annual rate from 0% to 100%, and a whole-month term from 1 to 1,200 months. What loan amount should I use?"
    monthly_rate = slots["rate"] / 1200
    months = int(slots["months"])
    principal = slots["principal"]
    payment = principal / months if monthly_rate == 0 else principal * monthly_rate / (1 - (1 + monthly_rate) ** (-months))
    total = payment * months
    state.pop("pending", None)
    return (f"Estimated monthly payment: **{money(payment)}** for {months} months.\n\n"
            f"Total repayments: {money(total)}; estimated interest: {money(total - principal)}.\n\n"
            "This uses a fixed annual nominal rate, monthly payments, and a reducing balance. "
            "It excludes fees, insurance, rate changes, and lender-specific rounding; flat-rate loans use a different calculation. "
            "You can change the rate or term in a follow-up.")


def cashflow(question, state):
    """Keep user-supplied scenarios separate from the saved transaction totals."""
    slots = state.setdefault("slots", {})
    income = matches(rf"\b(?:income|salary|earn|make|receive)\s*(?:is|of|:|=)?\s*{AMOUNT}", question)
    expenses = matches(rf"\b(?:expenses?|spend|spending|bills?|costs?)\s*(?:is|are|of|:|=)?\s*{AMOUNT}", question)
    purchase = matches(rf"\b(?:afford|buy|purchase)\s*{AMOUNT}", question)
    savings_amount = matches(rf"\b(?:save|saving|savings)\s*(?:is|of|:|=)?\s*{AMOUNT}", question)
    for field, found in (("income", income), ("expenses", expenses), ("purchase", purchase), ("saving", savings_amount)):
        if found:
            slots[field] = decimal(found[1])
    if state.get("pending") and matches(rf"^\s*{AMOUNT}\s*[.!]?\s*$", question):
        slots[state["pending"]] = decimal(matches(AMOUNT, question)[1])
    if any(value < 0 for value in slots.values()):
        state["slots"] = {}
        state["pending"] = "income"
        return "Use non-negative amounts for this scenario. What monthly income should I use?"
    for field, prompt in (("income", "What monthly income should I use for your scenario?"),
                          ("expenses", "What are your total monthly expenses in this scenario? Include bills and regular commitments.")):
        if field not in slots:
            state["pending"] = field
            return prompt
    state.pop("pending", None)
    surplus = slots["income"] - slots["expenses"]
    answer = ("**Scenario using the numbers you gave me** (not your saved transactions):\n\n"
              f"- Monthly income: {money(slots['income'])}\n"
              f"- Monthly expenses: {money(slots['expenses'])}\n"
              f"- Income minus expenses: **{money(surplus)}**\n")
    if "saving" in slots:
        answer += f"- Left after setting aside {money(slots['saving'])} for savings: **{money(surplus - slots['saving'])}**\n"
    if "purchase" in slots:
        answer += f"- Left after an additional {money(slots['purchase'])} purchase: **{money(surplus - slots.get('saving', Decimal(0)) - slots['purchase'])}**\n"
    return answer + "\nI treated these as monthly totals. Any unlisted costs still need to be included. You can change ‘income’, ‘expenses’, or ‘save’ in a follow-up. Nothing has been saved."


HELP = ("I can help you review your records and work through calculations. Try:\n\n"
        "- ‘How much did I spend on Food last month?’\n"
        "- ‘Compare this month with last month’\n"
        "- ‘How much can I spend per day?’\n"
        "- ‘Save RM 3,000 in 6 months’, then ‘already saved RM 500’\n"
        "- ‘Can I afford RM 250?’\n"
        "- ‘I earn RM 3,000 and spend RM 2,000. How much is left?’\n"
        "- ‘Loan RM 10,000 at 6% over 3 years’\n"
        "- ‘Calculate (income - expenses) / 2’ or ‘15% of 200’\n\n"
        "I remember the topic and month during this conversation. These are local rules and calculations, "
        "so I may need you to rephrase. I don't change your records.")


def reply(question, transactions, budgets, goals, today, context=None):
    """Return an answer and update an optional session-owned conversation context."""
    state = context if context is not None else {}
    q = re.sub(r"\s+", " ", question.lower().replace("’", "'")).strip()
    if not q:
        return "What would you like to work out? " + HELP
    if len(q) > 1000:
        return "Please shorten your question to 1,000 characters so I can work through it."
    if matches(r"^(cancel|start over|reset|new calculation)[.!]?$", q):
        state.clear()
        return "Let's start fresh. What would you like to calculate or review?"
    if matches(r"^(hi|hello|hey|good morning|good evening)( there)?[!.]?$", q):
        return "Hi! I can review your spending or help calculate a savings plan, purchase, or loan payment. What are you working on?"
    if matches(r"^(thanks|thank you|cheers)[!.]?$", q):
        return "You're welcome. You can try another amount, ask about another month, or start a new calculation."
    if matches(r"\b(help|examples?)\b|what can you do|how to use", q):
        return HELP
    try:
        return _reply(q, transactions, budgets, goals, today, state)
    except (ValueError, ArithmeticError) as error:
        return str(error) if isinstance(error, ValueError) else "Those numbers are too large or invalid. Please try smaller, finite numbers."


def _reply(q, transactions, budgets, goals, today, state):
    month, explicit_month = month_for(q, today, state.get("month"))
    state["month"] = month
    label = f"{calendar.month_name[int(month[5:])]} {month[:4]}"

    def totals(selected):
        rows = [t for t in transactions if t["date"].startswith(selected)]
        income = sum((decimal(t["amount"]) for t in rows if t["type"] == "Income"), Decimal(0))
        expenses = sum((decimal(t["amount"]) for t in rows if t["type"] == "Expense"), Decimal(0))
        return rows, income, expenses

    rows, income, expenses = totals(month)
    balance = income - expenses
    budget = decimal(budgets.get(month, 0))
    variables = {"income": income, "expenses": expenses, "balance": balance, "budget": budget,
                 "remaining": budget - expenses}
    categories = {}
    for transaction in rows:
        if transaction["type"] == "Expense":
            category = transaction["category"]
            categories[category] = categories.get(category, Decimal(0)) + decimal(transaction["amount"])
    # Match categories from the entire dataset, including those with no entries this month.
    names = sorted({t["category"] for t in transactions if t["type"] == "Expense"}, key=len, reverse=True)
    category = next((name for name in names if matches(r"\b" + re.escape(name) + r"\b", q)), None)

    intent = None
    scenario_text = re.sub(r"\b20\d{2}-\d{2}\b", "", q)
    scenario_income = matches(rf"\b(?:income|salary|earn|make|receive)\s*(?:is|of|:|=)?\s*{AMOUNT}", scenario_text)
    scenario_expenses = matches(rf"\b(?:expenses?|spend|spending|bills?|costs?)\s*(?:is|are|of|:|=)?\s*{AMOUNT}", scenario_text)
    natural_arithmetic = matches(r"^(?:what is|what's|how much is|work out)\b", q) and matches(r"[+*/%×÷]|\s-\s", q)
    if natural_arithmetic:
        intent = "calculate"
    elif scenario_income or scenario_expenses:
        intent = "cashflow"
    elif matches(r"\b(compare|comparison|versus|vs)\b|more than last month|less than last month", q):
        intent = "compare"
    elif matches(r"\b(loan|borrow|repayment|mortgage|installment|instalment)\b", q):
        intent = "loan"
    elif matches(r"\b(can i afford|afford|buy|purchase)\b", q):
        intent = "afford"
    elif matches(r"\b(per day|daily|a day|each day)\b", q):
        intent = "daily"
    elif matches(r"\b(save|saving)\b.*\d|\b(how long|how many months|how much.*per month)\b.*\b(save|saving|goal)\b|savings plan", q):
        intent = "savings"
    elif matches(r"\b(calculate|compute)\b", q) or re.fullmatch(r"[\d\s.,+*/()%×÷-]+[?]?", q) or matches(r"%\s*of\b", q):
        intent = "calculate"
    elif matches(r"\b(tips?|advice|suggest|reduce|improve)\b|save more|help me save", q):
        intent = "tips"
    elif matches(r"\b(goals?|savings progress|saving targets?)\b", q):
        intent = "goals"
    elif matches(r"\b(budget|limit|overspend|overspent|alert)\b", q):
        intent = "budget"
    elif category or matches(r"\b(categor(?:y|ies)|breakdown|biggest|highest)\b|where.*money|top spend", q):
        intent = "category"
    elif matches(r"\b(balance|left|remaining|net|profit)\b", q):
        intent = "balance"
    elif matches(r"\b(income|earn(?:ed)?|received|salary|make|made)\b", q):
        intent = "income"
    elif matches(r"\b(expenses?|spen[dt]|spending|costs?|paid)\b", q):
        intent = "expenses"
    elif matches(r"\b(summary|overview|finances|financial situation|doing financially)\b", q):
        intent = "summary"

    # Short follow-ups retain a calculator's slots or a report's category/month.
    previous = state.get("intent")
    if intent is None and previous in ("savings", "loan", "afford", "cashflow") and (
            re.search(r"\d", q) or matches(r"how long|per month|what if", q)):
        intent = previous
    if previous == "cashflow" and intent in ("savings", "afford") and not matches(r"\b(in|over|within|for)\s+\d+\s+(months?|years?)\b", q):
        intent = previous
    if intent == "calculate" and previous in ("savings", "loan", "afford", "cashflow") and matches(
            rf"^\s*{AMOUNT}\s*%?\s*[.!]?\s*$", q):
        intent = previous
    if intent is None and explicit_month and previous in ("income", "expenses", "balance", "budget", "category", "summary", "compare", "daily"):
        intent = previous
        category = state.get("category") if previous == "category" else category
    if intent is None:
        return "I can help work that out, but I need a clearer question or some numbers.\n\n" + HELP
    if intent != previous:
        state.pop("pending", None)
        state.pop("slots", None)
    state["intent"] = intent
    if intent == "category":
        state["category"] = category

    if intent == "savings":
        return savings(q, state, goals)
    if intent == "loan":
        return loan(q, state)
    if intent == "cashflow":
        return cashflow(q, state)
    if intent == "calculate":
        expression = re.sub(r"^(?:please\s+)?(?:calculate|compute|what is|what's|how much is|work out)\s*:?\s*", "", q).rstrip("? .")
        expression = re.sub(r"\bof\b", "*", expression)
        expression = re.sub(r"\bmy\s+", "", expression)
        result = calculate(expression, variables)
        data_note = f" Variables use recorded totals for {label}." if re.search(r"[a-z]", re.sub(r"\b(rm|myr)\b", "", expression)) else ""
        return f"**Result: {result:,.2f}**\n\n{expression} = {result:,.2f}.{data_note}"
    if intent == "afford":
        amount = matches(AMOUNT, re.sub(r"\b20\d{2}-\d{2}\b", "", q))
        if not amount:
            state["pending"] = "price"
            return "What would the purchase cost in RM? I'll compare it with your recorded monthly surplus and any budget you set."
        price = decimal(amount[1])
        if price <= 0:
            return "Please enter a purchase price greater than zero."
        state.pop("pending", None)
        if not rows:
            return f"There are no transactions for {label}, so I can't assess {money(price)} against your finances. Add income and expenses first."
        answer = (f"For a hypothetical **{money(price)}** purchase in {label}:\n\n"
                  f"- Recorded income minus expenses: {money(balance)}\n"
                  f"- Surplus after this additional purchase: **{money(balance - price)}**\n")
        if budget > 0:
            answer += f"- Budget remaining afterward: **{money(budget - expenses - price)}**\n"
        else:
            answer += "- No monthly budget is set.\n"
        return answer + "\nThis is a scenario using recorded entries, not a check of available cash. Account for unrecorded bills and commitments before deciding. Nothing has been saved."
    if intent == "daily":
        if month != today.strftime("%Y-%m"):
            return f"A remaining daily allowance only applies to the current month. You selected {label}; ask ‘daily budget this month’."
        if budget <= 0:
            return "Set a positive budget for this month first, then I can divide the remaining budget over the days left."
        days = calendar.monthrange(today.year, today.month)[1] - today.day + 1
        remaining = budget - expenses
        if remaining <= 0:
            return f"You have {money(remaining)} of budget remaining for {label}. There is no positive daily allowance left."
        return (f"You have **{money(remaining)}** left in your {label} budget. Across **{days} days, including today**, "
                f"that is about **{money(remaining / days)} per day**. Recorded expenses, including any future-dated entries in this month, are already counted; upcoming unrecorded bills still need to fit within it.")
    if intent == "compare":
        parts = re.split(r"\b(?:with|versus|vs\.?|to|and)\b", q, maxsplit=1)
        if len(parts) == 2:
            month, _ = month_for(parts[0], today, month)
            state["month"] = month
            label = f"{calendar.month_name[int(month[5:])]} {month[:4]}"
            rows, income, expenses = totals(month)
            balance = income - expenses
        year, mon = map(int, month.split("-"))
        earlier = f"{year if mon > 1 else year - 1:04d}-{mon - 1 if mon > 1 else 12:02d}"
        if len(parts) == 2:
            earlier, _ = month_for(parts[1], today, earlier)
        old_rows, old_income, old_expenses = totals(earlier)
        earlier_label = f"{calendar.month_name[int(earlier[5:])]} {earlier[:4]}"
        answer = (f"**{label} compared with {earlier_label}**\n\n"
                  "| Measure | Selected month | Previous month | Change |\n| --- | ---: | ---: | ---: |\n"
                  f"| Income | {money(income)} | {money(old_income)} | {money(income - old_income)} |\n"
                  f"| Expenses | {money(expenses)} | {money(old_expenses)} | {money(expenses - old_expenses)} |\n"
                  f"| Net balance | {money(balance)} | {money(old_income - old_expenses)} | {money(balance - old_income + old_expenses)} |")
        if not rows or not old_rows:
            answer += "\n\nAt least one month has no recorded transactions; zero means no entries, not confirmed zero activity."
        if month == today.strftime("%Y-%m"):
            answer += "\n\nThe current month may be incomplete; this compares recorded totals, not equal-length periods."
        return answer
    if intent == "goals":
        if not goals:
            return "You have no saved goals yet. Create one in Savings Goals, or tell me ‘save RM 3,000 in 6 months’ to work out a plan."
        return "Your savings goals:\n\n" + "\n".join(
            f"- {g['name']}: {money(decimal(g['saved']))} of {money(decimal(g['target']))} "
            f"({min(decimal(g['saved']) / decimal(g['target']) * 100, Decimal(100)):.0f}% complete)"
            for g in goals[:8]) + "\n\nTo plan one, try ‘save for [goal name] in 6 months’."
    if intent == "budget":
        if budget <= 0:
            return f"No positive budget is set for {label}. Set one in Budget Management to enable tracking."
        return (f"**{label} budget:** {money(budget)}\n\nSpent: {money(expenses)} "
                f"({expenses / budget * 100:.1f}% used). Remaining: **{money(budget - expenses)}**. "
                + ("You are over budget." if expenses > budget else "You have reached your limit." if expenses == budget else "You are within the recorded limit."))
    if intent == "category":
        if category:
            return f"You spent **{money(categories.get(category, Decimal(0)))}** on {category} in {label}."
        if not categories:
            return f"There are no recorded expenses for {label}."
        return f"Spending categories for {label}:\n\n" + "\n".join(
            f"- {name}: {money(amount)} ({amount / expenses * 100:.1f}%)"
            for name, amount in sorted(categories.items(), key=lambda pair: pair[1], reverse=True)[:8])
    if intent == "tips":
        if not rows:
            return f"There are no transactions for {label} yet. Record income and expenses, or tell me a savings target and timeframe so we can calculate a plan."
        answer = f"For {label}, recorded income is {money(income)}, expenses are {money(expenses)}, and the net is **{money(balance)}**.\n\n"
        if categories:
            name = max(categories, key=categories.get)
            answer += f"Your largest expense category is **{name} ({money(categories[name])})**. Reducing that category by 10% would free up **{money(categories[name] / 10)}** in this hypothetical month.\n\n"
        if balance < 0:
            answer += f"Recorded expenses exceed income by {money(-balance)}. Check missing income and upcoming bills before making a savings commitment.\n\n"
        return answer + "What savings target and timeframe would you like to work toward? These examples do not change your budget or records."
    if intent == "income":
        return f"Your recorded income for {label} is **{money(income)}**."
    if intent == "expenses":
        return f"Your recorded expenses for {label} are **{money(expenses)}** across {sum(t['type'] == 'Expense' for t in rows)} transactions."
    if intent == "balance":
        return f"Your recorded net balance for {label} is **{money(balance)}**: income {money(income)} minus expenses {money(expenses)}. This is not your bank balance."
    return (f"**{label} overview**\n\n- Income: {money(income)}\n- Expenses: {money(expenses)}\n"
            f"- Net balance: {money(balance)}\n- Monthly budget: {money(budget) if budget > 0 else 'not set'}\n\n"
            "Would you like to review a category, compare months, or calculate a savings plan?")
