from expensemanager import ExpenseManager
from expense import Expense
from analysis import Analysis
from datetime import datetime

class Menu:
    def __init__(self):
        self._em = ExpenseManager()
        self._expenses = self._em.load_data()

    @property
    def expenses(self):
        return self._expenses
    @expenses.setter
    def expenses(self, data):
        if isinstance(data, dict):
            self._expenses = data
        else:
            raise ValueError('Incorrect passed, should be dict')

    def main_menu(self):
        while True:
            print("\n--- Expense Tracking System ---")
            print("1. Add Expense")
            print("2. Display Expenses")
            print("3. Remove Expense")
            print("4. Perform Analysis")
            print("5. Exit")

            # Get user choice
            choice = input("Choose an option (1-5): ")

            if choice == '1':
                amount = input("Enter amount: ")
                category = input("Specify Category: ")
                date = input("Enter date of expense: ")
                description = input("Enter description: ")
                if date == '':
                    date = datetime.now().replace(microsecond=0)
                expense = Expense(amount,category,date,description)
                self._em.save_data(expense)

            elif choice == '2':
                self.expenses = self._em.load_data()
                print(list(self.expenses.values()))

            elif choice == '3':
                choice = input('Pass ID of item u wish to remove: ')
                if choice in self.expenses:
                    self.expenses.pop(choice)
                    self._em.save_data(self.expenses)
                    self.expenses = self._em.load_data()
                else:
                    print(f'Expense with ID: {choice} not found in DB, check and try again')

            elif choice == '4':
                an = Analysis(list(self.expenses.values()))

                print(f'Total expenses: {an.sum()}')
                print(f'Expenses this month: {an.sum_month()}')

            elif choice == '5':
                print("Exiting the system. Have a great day!")
                break

            else:
                print("Invalid choice. Please enter a number from 1 to 5.")
