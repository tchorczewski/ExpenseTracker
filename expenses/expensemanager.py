import json
from expenses.expense import Expense
import os


class ExpenseManager:
    def __init__(self, expenses=None):
        if expenses is None:
            expenses = []
        self._expenses = expenses
        self._dir = os.path.dirname(os.path.abspath(__file__))
        self._root_dir = os.path.dirname(self._dir)
        self.data_file_path = os.path.join(self._root_dir, 'data.json')

    @property
    def expenses(self):
        return self._expenses

    @expenses.setter
    def expenses(self, expenses):
        self._expenses = expenses

    def load_data(self) -> dict:
        """
        Loads data from pseudo db in json file
        """
        try:
            with open(self.data_file_path, 'r') as file:
                self.expenses = json.load(file)
                return self._expenses
        except FileNotFoundError:
            raise FileNotFoundError('File data.json not found')

    def partial_save(self, data):
        """
        Saves data from current session to pseudo db in json file
        The app is Naive it assumes the db file already exists.
        """
        existing_data = self.load_data()
        existing_data.update(Expense.to_dict(data))
        try:
            with open(self.data_file_path, 'w') as file:
                json.dump(existing_data, file, indent=4)
        except FileNotFoundError:
            raise FileNotFoundError("File data.json not found")

    def full_save(self, data):
        new_data = dict()
        if isinstance(data, dict):
            for item, value in data.items():
                new_data.update({item: value})
            try:
                with open(self.data_file_path, 'w') as file:
                    json.dump(new_data, file, indent=4)
            except FileNotFoundError:
                raise FileNotFoundError("DB file not found")
        else:
            raise ValueError(f"Incorrect data format passed to full_save method, passed format is {type(data)}")

    def remove_record(self, choice):
        """
        Takes users id of choice and attempts to remove a record from db.
        :param choice: The selection of which record to delete
        :return: Full db after the successful removal of the item
        """
        existing_data = self.load_data()
        if isinstance(choice, str):
            if choice in existing_data:
                existing_data.pop(choice)
                self.full_save(existing_data)
                return self.load_data()
            else:
                print(f'Expense with ID: {choice} not found in DB, check and try again')
