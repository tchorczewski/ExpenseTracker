from datetime import datetime


class Expense:
    def __init__(self, amount, category, date, description):
        self._amount = amount
        self._category = category
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
            raise ValueError('Amount has to be non zero number')

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, category):
        if isinstance(category, str):
            self._category = category
        else:
            raise ValueError('Category has to be a text')

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, date):
        if self._validate_date(date):
            self._date = date

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, description):
        if isinstance(description, str):
            self._description = description
        else:
            raise ValueError('Description has to be a text')

    def __repr__(self):
        return f"Expense(amount={self._amount}, category='{self._category}', date='{self._date}', description='{self._description}')"

    def __str__(self):
        return f"{self._date}: {self._description} (${self._amount}) under {self._category}"

    def __lt__(self, other):
        if self._class_check(other):
            return self.amount < other.amount
        else:
            raise ValueError('Comparison must occur between objects of Expense class')

    def __gt__(self, other):
        if self._class_check(other):
            return self.amount > other.amount
        else:
            raise ValueError('Comparison must occur between objects of Expense class')

    def __eq__(self, other):
        if self._class_check(other):
            return self.amount == other.amount
        else:
            raise ValueError('Comparison must occur between objects of Expense class')

    def __le__(self, other):
        if self._class_check(other):
            return self.amount <= other.amount
        else:
            raise ValueError('Comparison must occur between objects of Expense class')

    def __ge__(self, other):
        if self._class_check(other):
            return self.amount >= other.amount
        else:
            raise ValueError('Comparison must occur between objects of Expense class')

    def _class_check(self, item):
        if isinstance(item, Expense):
            return True
        else:
            raise ValueError('Comparison must occur between objects of Expense class')

    def _validate_date(self, date):
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            raise ValueError('Date must be in the format YYYY-MM-DD')

    def to_dict(self):
        return {
            "amount": self._amount,
            "category": self._category,
            "date": self._date,
            "description": self._description,
        }
