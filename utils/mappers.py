def budget_mapper(budget):
    return {
        "budget_id": budget.budget_id,
        "user_id": budget.user_id,
        "budget_month": budget.budget_month,
        "budget_year": budget.budget_year,
        "budget_amount": budget.budget_amount,
        "status_id": budget.status_id,
        "created_at": budget.created_at.strftime("%Y-%m-%d"),
        "updated_at": (
            budget.updated_at.strftime("%Y-%m-%d") if budget.updated_at else None
        ),
    }


def expense_mapper(expense):
    return {
        "expense_id": expense.expense_id,
        "category_id": expense.category_id,
        "amount": expense.amount,
        "description": expense.description,
        "user_id": expense.user_id,
        "expense_date": expense.expense_date.strftime("%Y-%m-%d"),
        "created_at": expense.created_at.strftime("%Y-%m-%d"),
        "updated_at": (
            expense.updated_at.strftime("%Y-%m-%d") if expense.updated_at else None
        ),
        "budget_id": expense.budget_id,
    }
