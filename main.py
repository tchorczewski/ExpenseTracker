from db import db
from app import create_app

app = create_app()

# @app.route("/")
# def home():
# return render_template("index.html")

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
