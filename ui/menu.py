from stats.analysis import conditional_sum, total_sum
from stats.plotting import Plotting
from db.db_operations import (
    fetch_expense,
    delete_expense,
    insert_expense,
    fetch_by_year,
    fetch_by_month,
)
from utils.validation import *


class Menu:

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

            if choice == "1":
                amount = get_amount_input()
                category = category_input()
                date = date_input()
                description = input("Enter description: ")
                insert_expense(category, amount, description, date)

            elif choice == "2":
                print(list(map(beautify_data, fetch_expense())))

            elif choice == "3":
                choice = input("Pass ID of item u wish to remove: ")
                delete_expense(choice)

            elif choice == "4":
                self.analysis_menu()

            elif choice == "5":
                print("Exiting the system. Have a great day!")
                break

            else:
                print("Invalid choice. Please enter a number from 1 to 5.")

    def analysis_menu(self):
        while True:
            print("\n--- Expense Analysis ---")
            print("1. Monthly Expenses")
            print("2. Expenses total")
            print("3. Yearly summary")
            print("4. Plot your expenses")
            print("5. Main Menu")

            choice = input("Choose an option (1-5): ")

            if choice == "1":
                year = year_input()
                month = month_input()
                print(
                    f"Total expenses in {month} of {year} is {conditional_sum(list(map(analyze_beautify,
                                                                                 fetch_by_month(year, month))))}"
                )
            elif choice == "2":
                print(
                    f"Total recorded expenses: {total_sum(list(map(beautify_data,fetch_expense())))}"
                )
            elif choice == "3":
                year = year_input()
                print(
                    f"Total expenses in {year}: {conditional_sum(list(map(analyze_beautify, fetch_by_year(year))))}"
                )
            elif choice == "4":
                self.plotting_menu()
            elif choice == "5":
                print("Going back to main menu...")
                break

            else:
                print("Invalid choice. Please enter a number from 1 to 5.")

    def plotting_menu(self):
        self.plt = Plotting()
        while True:
            print("\n ---Data Plotting ---")
            print("1. Yearly average spending")
            print("2. Yearly spending distribution")
            print("3. Monthly spending distribution")
            print("4. ---PlaceHolder---")
            print("5. Back to analysis menu")

            choice = input("Choose an option(1-5): ")

            if choice == "1":
                self.plt.expense_plot()
            if choice == "2":
                year = year_input()
                self.plt.expense_month_year_distribution(year)
            if choice == "3":
                year = year_input()
                month = month_input()
                self.plt.monthly_expense(year, month)
            if choice == "4":
                pass
            if choice == "5":
                print("Going back to analysis menu ...")
                break
            else:
                print("Invalid choice. Please enter a number from 1 to 5")
