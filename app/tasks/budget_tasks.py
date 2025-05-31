from flask import jsonify

from main import celery
from celery.schedules import crontab
from db.models import db, Incomes, Expenses
from sqlalchemy.exc import IntegrityError, OperationalError


@celery.task
def create_next_month_budget():
    """
    TODO Write proper logic for auto creation of budgets based on past and present data. Migrate logic to check for existing budgets, incomes, past budgets to separate methods/tasks
    :return:
    """


"""
TODO Write proper logic for autocreation of expenses and incomes based on already existing ones (proper flag in db)
"""
