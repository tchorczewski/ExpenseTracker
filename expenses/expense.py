from datetime import datetime
import operator
import uuid
from utils.validation import Validation


class Expense:
    def __init__(
        self, amount=0, category="Bills", date=datetime.now().date(), description="Nan"
    ):
        self._amount = amount
        self._category = category
        if date == "":
            self._date = datetime.now().date()
        else:
            self._date = date
        self._description = description

    @property
    def amount(self):
        return self._amount

    @amount.setter
    def amount(self, amount):
        if amount >= 0 and isinstance(amount, (int, float)):
            self._amount = amount
        else:
            raise ValueError("Amount has to be non zero number")

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, category):
        if isinstance(category, str):
            self._category = category
        else:
            raise ValueError("Category has to be a text")

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, data):
        if data == "" and self._date == "":
            self._date = datetime.now().date()
        else:
            if Validation.validate_date(data):
                self._date = data

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, description):
        if isinstance(description, str):
            self._description = description
        else:
            raise ValueError("Description has to be a text")

    def __repr__(self):
        return f"Expense(amount={self.amount}, category='{self.category}', date='{self.date}', description='{self.description}')"

    def __str__(self):
        return (
            f"{self.date}: {self.description} (${self.amount}) category {self.category}"
        )

    def to_dict(self):
        uid = str(uuid.uuid4())
        return {
            uid: {
                "amount": self.amount,
                "category": self.category,
                "date": str(self.date),
                "description": self.description,
            }
        }

    def _is_object(self, item: object) -> object:
        if isinstance(item, type):
            return True
        else:
            raise ValueError("Comparison must occur between objects of Expense class")

    def compare_amounts(self, relate, other):
        ops = {
            ">": operator.gt,
            "<": operator.lt,
            ">=": operator.ge,
            "<=": operator.le,
            "==": operator.eq,
            "!=": operator.ne,
        }
        try:
            self._is_object(other)
            if relate in ops:
                return ops[relate](self.amount, other.amount)
            else:
                raise ValueError(
                    f"Unsupported operator '{relate}'. Supported operators are: {', '.join(ops.keys())}"
                )
        except ValueError:
            raise ValueError("The comparison must be between objects of Expense class")
