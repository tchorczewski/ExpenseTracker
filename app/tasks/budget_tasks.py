from app.services.budget_services import get_budget_for_user
from app.services.budget_task_services import (
    get_users_with_missing_budget,
    get_cyclical_data,
    calculate_budget_amount,
    clone_budget,
    push_data,
    clone_transactions,
)
from app.services.date_services import get_previous_month, parse_date
from main import celery


@celery.task(autoretry_for=(None,), retry_backoff=True, max_retries=3)
def create_next_month_budget():
    user_ids = get_users_with_missing_budget()
    previous_year, previous_month = get_previous_month()
    data = []
    for user in user_ids:
        budget, _, _ = get_budget_for_user(
            user, parse_date(previous_year, previous_month)
        )
        transactions = get_cyclical_data(budget.budget_id)
        budget_amount = calculate_budget_amount(transactions)
        prepared_budget = clone_budget(budget, budget_amount)
        data.append(prepared_budget)
        data.extend(clone_transactions(budget.budget_id, transactions))

    push_data(data)
