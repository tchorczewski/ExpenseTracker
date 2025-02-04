from db import db
from app import create_app

if __name__ == "__main__":
    app = create_app()

    with app.app_context():
        db.create_all()
    app.run(debug=True)
