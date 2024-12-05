from expensemanager import ExpenseManager
from expense import Expense

class Menu:
    def main_menu(self):
        while True:
            print("\n--- Expense Tracking System ---")
            print("1. Add Expense")
            print("2. Display Expenses")
            print("3. Remove Expense")
            print("4. Sum Expenses")
            print("5. Exit")

            # Get user choice
            choice = input("Choose an option (1-5): ")

            if choice == '1':
                amount = input("Enter amount: ")
                category = input("Specify Category: ")
                date = input("Enter date of expense: ")
                description = input("Enter description: ")
                em = ExpenseManager()
                expense = Expense(amount,category,date,description)
                em.save_data(expense)

            elif choice == '2':
                em = ExpenseManager()
                print(em.load_data().values())

            elif choice == '3':
               pass

            elif choice == '4':
                pass

            elif choice == '5':
                print("Exiting the system. Have a great day!")
                break

            else:
                print("Invalid choice. Please enter a number from 1 to 5.")
