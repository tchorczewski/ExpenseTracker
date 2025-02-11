from datetime import datetime, timezone, date
from . import db


class Expenses(db.Model):
    __tablename__ = "expenses"
    expense_id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(
        db.Integer, db.ForeignKey("expense_categories.category_id"), nullable=False
    )
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    description = db.Column(db.String(500))
    expense_date = db.Column(db.Date, nullable=False, default=date.today)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    created_at = db.Column(
        db.DateTime, nullable=False, default=datetime.now(timezone.utc)
    )
    updated_at = db.Column(db.DateTime)

    user = db.relationship("Users", backref="expenses")
    category = db.relationship("ExpenseCategories", backref="expenses")


class Users(db.Model):
    __tablename__ = "users"
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), nullable=False, unique=True)
    email = db.Column(db.String(320), nullable=False, unique=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    user_password = db.Column(db.LargeBinary, nullable=False)
    user_status_id = db.Column(
        db.Integer, db.ForeignKey("user_statuses.status_id"), nullable=False
    )
    user_role_id = db.Column(
        db.Integer, db.ForeignKey("user_roles.role_id"), nullable=False
    )
    created_at = db.Column(
        db.DateTime, nullable=False, default=datetime.now(timezone.utc)
    )
    updated_by = db.Column(db.Integer)
    updated_at = db.Column(db.DateTime)

    role_id = db.relationship("UserRoles", backref="users")
    status_id = db.relationship("UserStatuses", backref="users")


class Budget(db.Model):
    __tablename__ = "budgets"
    budget_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    budget_month = db.Column(db.Integer, nullable=False)
    budget_year = db.Column(db.Integer, nullable=False)
    budget_amount = db.Column(db.Numeric(10, 2), nullable=False)
    status_id = db.Column(
        db.Integer, db.ForeignKey("budget_statuses.status_id"), nullable=False
    )
    created_at = db.Column(
        db.DateTime, nullable=False, default=datetime.now(timezone.utc)
    )
    updated_at = db.Column(db.DateTime)

    user = db.relationship("Users", backref="budgets")
    status = db.relationship("BudgetStatuses", backref="budgets")

    __table_args__ = (
        db.CheckConstraint("budget_month BETWEEN 1 AND 12", name="check_budget_month"),
        db.CheckConstraint("budget_year >= 2000", name="check_budget_year"),
        db.UniqueConstraint(
            "user_id", "budget_month", "budget_year", name="unique_budget_per_user"
        ),
    )


class ExpenseCategories(db.Model):
    __tablename__ = "expense_categories"
    category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(255), nullable=False)


class UserRoles(db.Model):
    __tablename__ = "user_roles"
    role_id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(100), nullable=False)


class UserStatuses(db.Model):
    __tablename__ = "user_statuses"
    status_id = db.Column(db.Integer, primary_key=True)
    status_name = db.Column(db.String(100), nullable=False)
