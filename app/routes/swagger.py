from app.swagger_config import SwaggerConfig
from flask_swagger_ui import get_swaggerui_blueprint

swagger_bp = get_swaggerui_blueprint(
    SwaggerConfig.SWAGGER_URL,
    SwaggerConfig.API_URL,
    config={"app_name": "URL Shortener API"},
)
