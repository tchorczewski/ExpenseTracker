from datetime import datetime
import operator


class Expense:
    def __init__(self, amount=0, category='Bills', date=datetime.now(), description='Nan'):
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
        return f"Expense(amount={self.amount}, category='{self.category}', date='{self.date}', description='{self.description}')"

    def __str__(self):
        return f"{self.date}: {self.description} (${self.amount}) category {self.category}"

    def _class_check(self, item: object) -> object:
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

    def compare_amounts(self, relate, other):
        ops = {'>': operator.gt,
               '<': operator.lt,
               '>=': operator.ge,
               '<=': operator.le,
               '==': operator.eq,
               '!=': operator.ne}
        try:
            self._class_check(other)
            if relate in ops:
                return ops[relate](self.amount, other.amount)
            else:
                raise ValueError(f"Unsupported operator '{relate}'. Supported operators are: {', '.join(ops.keys())}")
        except ValueError:
            raise ValueError("The comparison must be between objects of Expense class")
