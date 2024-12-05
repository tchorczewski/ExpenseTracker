import json
from expense import Expense

class ExpenseManager:
    def __init__(self, expenses=None):
        if expenses is None:
            expenses = []
        self._expenses = expenses

    @property
    def expenses(self):
        return self._expenses
    @expenses.setter
    def expenses(self, expenses):
        self._expenses = expenses

    def load_data(self) -> dict:
        '''
        Loads data from pseudo db in json file
        Returns data in python dict form
        '''
        try:
            with open('data.json', 'r') as file:
                self.expenses = json.load(file)
                return self.expenses
        except FileNotFoundError:
            raise FileNotFoundError('File data.json not found')

    def save_data(self, data) -> bool:
        '''
        Saves data from current session to pseudo db in json file
        Will return True if done successfully
        '''
        existing_data = self.load_data()
        existing_data.update(Expense.to_dict(data))
        try:
            with open('data.json', 'w') as file:
                json.dump(existing_data, file, indent=4)
            return True
        except FileNotFoundError:
            raise FileNotFoundError("File data.json not found")
