from datetime import datetime, timezone
from . import db


class Users(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), nullable=False, unique=True)
    email = db.Column(db.String(320), nullable=False, unique=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    password = db.Column(db.LargeBinary, nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey("statuses.id"), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False)
    created_at = db.Column(
        db.DateTime, nullable=False, default=datetime.now(timezone.utc)
    )
    updated_by = db.Column(db.Integer)
    updated_at = db.Column(db.DateTime)

    role = db.relationship("Roles", backref="users")
    status = db.relationship("Statuses", backref="users")


class Budgets(db.Model):
    __tablename__ = "budgets"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    budget_month = db.Column(db.Integer, nullable=False)
    budget_year = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey("statuses.id"), nullable=False)
    created_at = db.Column(
        db.DateTime, nullable=False, default=datetime.now(timezone.utc)
    )
    updated_at = db.Column(db.DateTime)
    is_generated = db.Column(db.Boolean, default=False, nullable=False)

    user = db.relationship("Users", backref="budget")
    status = db.relationship("Statuses", backref="budget")
    transactions = db.relationship("Transactions", backref="budget", lazy="select")

    __table_args__ = (
        db.CheckConstraint("budget_month BETWEEN 1 AND 12", name="check_budget_month"),
        db.CheckConstraint("budget_year >= 2000", name="check_budget_year"),
        db.UniqueConstraint(
            "user_id", "budget_month", "budget_year", name="unique_budget_per_user"
        ),
    )


class Roles(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(100), nullable=False)


class Statuses(db.Model):
    __tablename__ = "statuses"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(
        db.String(100),
        db.CheckConstraint("type IN ('users','budgets')"),
        nullable=False,
    )


class Transactions(db.Model):
    __tablename__ = "transactions"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    is_cyclical = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(
        db.DateTime, nullable=False, default=datetime.now(timezone.utc)
    )
    updated_at = db.Column(db.DateTime)
    budget_id = db.Column(db.Integer, db.ForeignKey("budgets.id"), nullable=False)
    type = db.Column(
        db.String(20),
        db.CheckConstraint("type IN ('income','expense')"),
        nullable=False,
    )

    user = db.relationship("Users", backref="transactions")
    category = db.relationship("Categories", backref="transactions")


class Categories(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    type = db.Column(
        db.String(20),
        db.CheckConstraint("type IN ('income','expense')"),
        nullable=False,
    )
