import os
from datetime import timedelta
from dotenv import load_dotenv
from celery.schedules import crontab

load_dotenv()


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_TOKEN_LOCATION = ["cookies"]
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        seconds=int(os.getenv("JWT_EXPIRY_SECONDS", 3600))
    )
    JWT_CSRF_IN_COOKIES = False
    JWT_COOKIE_CSRF_PROTECT = False
    CELERY = dict(
        broker_url=os.getenv("BROKER_URL", "redis://redis:6379/0"),
        result_backend=os.getenv("RESULT_BACKEND", "redis://redis:6379/0"),
        task_ignore_result=True,
        task_always_eager=True,
        task_eager_propagates=True,
        timezone="Europe/Warsaw",
        beat_schedule={
            "create_monthly_budget": {
                "task": "app.tasks.budget_tasks.create_next_month_budget",
                "schedule": crontab(hour=15, minute=33, day_of_month=14),
            }
        },
    )
