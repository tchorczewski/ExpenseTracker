def budget_mapper(budget, budget_status=""):
    return {
        "id": budget.id,
        "user_id": budget.user_id,
        "budget_month": budget.budget_month,
        "budget_year": budget.budget_year,
        "amount": budget.amount,
        "status_id": budget.status_id,
        "status_name": budget_status,
        "is_generated": budget.is_generated,
        "created_at": budget.created_at.strftime("%Y-%m-%d"),
        "updated_at": (
            budget.updated_at.strftime("%Y-%m-%d") if budget.updated_at else None
        ),
    }


def transaction_mapper(transaction, category=""):
    return {
        "id": transaction.id,
        "user_id": transaction.user_id,
        "category_id": transaction.category_id,
        "category_name": category,
        "amount": transaction.amount,
        "date": transaction.date.strftime("%Y-%m-%d"),
        "is_cyclical": transaction.is_cyclical,
        "budget_id": transaction.budget_id,
        "created_at": transaction.created_at.strftime("%Y-%m-%d"),
        "updated_at": (
            transaction.updated_at.strftime("%Y-%m-%d")
            if transaction.updated_at
            else None
        ),
        "type": transaction.type,
    }


def last_operations_mapper(last_operations):
    return {
        "type": last_operations.type,
        "amount": last_operations.amount,
        "date": last_operations.date.strftime("%Y-%m-%d"),
        "category_name": last_operations.name,
    }


def status_mapper(status):
    return {"id": status.id, "name": status.name, "type": status.type}


def category_mapper(category):
    return {
        "id": category.id,
        "name": category.name,
        "type": category.type,
    }
