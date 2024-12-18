from datetime import datetime
from utils.validation import validate_date


class Expense:
    def __init__(
        self,
        amount: float = 0,
        category: str = "Bills",
        date: str = None,
        description: str = "Nan",
    ):
        self.amount = amount
        self._category = category
        if not date:
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
            if validate_date(data):
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
        return f"Expense(category='{self.category}', amount={self.amount}, date='{self.date}', description='{self.description}')"

    def __str__(self):
        return (
            f"{self.date}: {self.description} (${self.amount}) category {self.category}"
        )

    def to_dict(self):
        return {
            "amount": self.amount,
            "category": self.category,
            "date": str(self.date),
            "description": self.description,
        }

    @classmethod
    def from_db(cls, db_row):
        return cls(*db_row)
