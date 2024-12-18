from ui.menu import Menu
from db.db_operations import fetch_expense, insert_expense, delete_expense


if __name__ == "__main__":
    menu = Menu()
    menu.main_menu()
