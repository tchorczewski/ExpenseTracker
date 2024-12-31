import os
from dotenv import load_dotenv

# Load environment variables from a .env file (recommended)
load_dotenv()

# Database configuration parameters
DB_CONFIG = {
    "dbname": os.getenv(
        "DB_NAME", "expense_tracker"
    ),  # Default value: "expense_tracker"
    "user": os.getenv("DB_USER", "postgres"),  # Default value: "postgres"
    "password": os.getenv("DB_PASSWORD", "password"),  # Default value: "password"
    "host": os.getenv("DB_HOST", "localhost"),  # Default value: "localhost"
    "port": os.getenv("DB_PORT", "5432"),  # Default value: 5432
}
# hej
