from expensemanager import ExpenseManager
from expense import Expense
from analysis import Analysis
from datetime import datetime
from plotting import Plotting


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
                expense = Expense(amount,category,date,description)
                self._em.partial_save(expense)

            elif choice == '2':
                self.expenses = self._em.load_data()
                print(list(self.expenses.values()))

            elif choice == '3':
                choice = input('Pass ID of item u wish to remove: ')
                self.expenses = self._em.remove_record(choice)

            elif choice == '4':
                self.analysis_menu()

            elif choice == '5':
                print("Exiting the system. Have a great day!")
                break

            else:
                print("Invalid choice. Please enter a number from 1 to 5.")


    def analysis_menu(self):
        an = Analysis(list(self.expenses.values()))
        plt = Plotting()
        while True:
            print("\n--- Expense Analysis ---")
            print("1. Monthly Expenses")
            print("2. Expenses total")
            print("3. Yearly summary")
            print("4. Plot your expenses")
            print("5. Main Menu")

            choice = input("Choose an option (1-5): ")


            if choice == '1':
                month = int(input('Which month do you want to see summary for? '))
                print(f'Total expenses in {datetime.now().month}: {an.sum_month(month)}')
            elif choice == '2':
                print(f'All the expenses so far are totalling to {an.total_sum()}')
            elif choice == '3':
                year = int(input('Which year do you want to see summary for? '))
                print(an.sum_year(year))
            elif choice == '4':
                plt.expense_plot()
            elif choice == '5':
                print("Going back to main menu...")
                break

            else:
                print("Invalid choice. Please enter a number from 1 to 5.")