import os
from dotenv import load_dotenv

load_dotenv()
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)


class SwaggerConfig:
    SWAGGER_URL = os.getenv("SWAGGER_URL")
    API_URL = os.getenv("API_URL")
