from db.db_handler import DatabaseHandler

handler = DatabaseHandler()


def insert_expense(name, amount, description, date):
    query = "INSERT INTO expenses (name,amount,description,date) VALUES(%s ,%s ,%s ,%s)"
    try:
        connection = handler.connect()
        if connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (name, amount, description, date))
                connection.commit()
                print("\nInserted successfully")
    except Exception as e:
        print(f"Error inserting expense: {e}")
        if connection:
            connection.rollback()
    finally:
        if connection:
            connection.close()


def fetch_expense():
    query = "SELECT * from expenses"
    try:
        connection = handler.connect()
        if connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()
                return rows
    except Exception as e:
        print(f"Failed fetching expenses {e}")
    finally:
        if connection:
            connection.close()


def delete_expense(record_id):
    query = "DELETE FROM expenses where id = %s; "
    try:
        connection = handler.connect()
        if connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (record_id,))
                connection.commit()
                print(f"Expense with ID {record_id} has been deleted")
    except Exception as e:
        print(f"Failed to delete epxense {e}")
        if connection:
            connection.rollback()
    finally:
        if connection:
            connection.close()
