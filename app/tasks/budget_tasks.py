from flask import jsonify

from app.services.budget_services import get_budget_for_user
from app.services.budget_task_services import (
    get_users_with_missing_budget,
    get_cyclical_data,
    calculate_budget_amount,
    clone_budget,
    push_budget,
)
from app.services.date_services import get_previous_month, parse_date
from main import celery
from celery.schedules import crontab


@celery.task
def create_next_month_budget():
    user_ids = get_users_with_missing_budget()
    previous_year, previous_month = get_previous_month()
    budgets = []
    for user in user_ids:
        budget, _, _ = get_budget_for_user(
            user, parse_date(previous_year, previous_month)
        )
        incomes, expenses = get_cyclical_data(budget.budget_id)
        budget_amount = calculate_budget_amount(incomes, expenses)
        prepared_budget = clone_budget(budget, budget_amount)
        budgets.append(prepared_budget)

    if not push_budget(budgets):
        print("Error")


# TODO Figure out logic and coupling between creation of cyclical incomes and expenses after budgets are created
