from datetime import datetime

from sqlalchemy import select, func, not_
from db import db
from app.services.budget_services import get_budget_for_user
from app.services.date_services import get_previous_month
from db.models import Budgets, Users


def prepare_next_month_data():
    previous_year, previous_month = get_previous_month()
    current_year, current_month = datetime.now().year, datetime.now().month
    current_month_subq = select(Budgets.user_id).filter(
        Budgets.budget_month == current_month, Budgets.budget_year == current_year
    )

    missing_budget_users_stmt = select(func.distinct(Users.user_id)).filter(
        Budgets.budget_year == previous_year,
        Budgets.budget_month == previous_month,
        not_(Budgets.user_id.in_(current_month_subq)),
    )

    user_ids = db.session.execute(missing_budget_users_stmt).scalars().all()
