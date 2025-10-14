def budget_mapper(budget, budget_status=""):
    return {
        "budget_id": budget.budget_id,
        "user_id": budget.user_id,
        "budget_month": budget.budget_month,
        "budget_year": budget.budget_year,
        "budget_amount": budget.budget_amount,
        "status_id": budget.status_id,
        "status_name": budget_status,
        "is_generated": budget.is_generated,
        "created_at": budget.created_at.strftime("%Y-%m-%d"),
        "updated_at": (
            budget.updated_at.strftime("%Y-%m-%d") if budget.updated_at else None
        ),
    }


def expense_mapper(expense, category=""):
    return {
        "expense_id": expense.expense_id,
        "category_name": category,
        "amount": expense.amount,
        "user_id": expense.user_id,
        "date": expense.date.strftime("%Y-%m-%d"),
        "is_cyclical": expense.is_cyclical,
        "created_at": expense.created_at.strftime("%Y-%m-%d"),
        "updated_at": (
            expense.updated_at.strftime("%Y-%m-%d") if expense.updated_at else None
        ),
        "budget_id": expense.budget_id,
    }


def income_mapper(income, category=""):
    return {
        "income_id": income.income_id,
        "user_id": income.user_id,
        "category_name": category,
        "amount": income.amount,
        "date": income.date.strftime("%Y-%m-%d"),
        "is_cyclical": income.is_cyclical,
        "budget_id": income.budget_id,
        "created_at": income.created_at.strftime("%Y-%m-%d"),
        "updated_at": (
            income.updated_at.strftime("%Y-%m-%d") if income.updated_at else None
        ),
    }


def last_operations_mapper(last_operations):
    return {
        "type": f"{'Expense' if last_operations.category_name in {'Housing', 'Transportation','Food & Groceries', "Entertainment", "Healthcare" } else 'Income'}",
        "amount": last_operations.amount,
        "date": last_operations.date.strftime("%Y-%m-%d"),
        "category_name": last_operations.category_name,
    }


def status_mapper(status):
    return {"id": status.status_id, "name": status.status_name}


def category_mapper(category):
    return {
        "id": category.category_id,
        "name": category.category_name,
    }
