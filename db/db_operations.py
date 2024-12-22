from db.db_handler import DatabaseHandler

handler = DatabaseHandler()


def insert_expense(category, amount, description, date):
    query = "INSERT INTO expenses (category,amount,description,date) VALUES(%s ,%s ,%s ,%s);"
    try:
        connection = handler.connect()
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (category, amount, description, date))
                connection.commit()
                print("\nInserted successfully")
    except Exception as e:
        print(f"Error inserting expense: {e}")


def fetch_expense():
    query = "SELECT * from expenses"
    try:
        connection = handler.connect()
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()
                return rows
    except Exception as e:
        print(f"Failed fetching expenses {e}")


def delete_expense(record_id):
    query = "DELETE FROM expenses where id = %s; "
    try:
        connection = handler.connect()
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (record_id,))
                connection.commit()
                print(f"Expense with ID {record_id} has been deleted")
    except Exception as e:
        print(f"Failed to delete epxense {e}")


def fetch_by_month(year: int, month: int) -> tuple:
    """
    Method to return expenses from DB filtered by year and month. Used to create monthly analysis.
    :param year: Year that we want the data to be filtered by
    :param month: Month that we want the data to be filtered by
    :return: Amount and category from db for the year and month that we specified
    """
    query = (
        "SELECT amount, category FROM expenses WHERE DATE_PART('year', date) = %s "
        "AND DATE_PART('month', date) = %s ;"
    )
    rows = []
    try:
        connection = handler.connect()
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (year, month))
                rows = cursor.fetchall()
                return rows
    except Exception as e:
        print(f"Failed fetching expenses {e}")
    return rows


def fetch_by_year(year: int) -> tuple:
    """
    Method to return data from DB filtered by year.
    :param year: Year that we want the data to be filtered by
    :return: Amount and category from db for the year that we specified
    """
    query = "SELECT amount, category FROM expenses WHERE DATE_PART('year', date) = %s ;"
    rows = []
    try:
        connection = handler.connect()
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (year,))
                rows = cursor.fetchall()
                return rows
    except Exception as e:
        print(f"Failed fetching expenses {e}")
    return rows
