from expense import Expense
class ExpenseManager:
    def __init__(self, expense):
        self._expense = expense

    @property
    def expense(self):
        return self._expense

    @expense.setter
    def expense(self, expense):
        if isinstance(expense, Expense):
            self._expense = expense
        else:
            raise ValueError('Passed object must be of Expense class')
