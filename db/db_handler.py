from db.config import DB_CONFIG
import psycopg2


class DatabaseHandler:
    def __init__(self):
        self.conn = None

    def connect(self):
        """Connects to the PostgresSQL database using DB_CONFIG."""
        try:
            self.conn = psycopg2.connect(**DB_CONFIG)
            return self.conn
        except Exception as e:
            print(f"Error connecting to database: {e}")
            return None
