from ui.menu import Menu
from db.db_operations import fetch_expense, insert_expense, delete_expense


if __name__ == "__main__":
    # menu = Menu()
    # menu.main_menu()
    insert_expense("TEST", 150.55, "TEST", "12-05-2024")
    delete_expense(1)
    data = fetch_expense()
    print(data)
