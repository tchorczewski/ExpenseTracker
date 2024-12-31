from ui.menu import Menu
from flask import Flask, redirect, url_for, render_template


app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


if __name__ == "__main__":
    # menu = Menu()
    # menu.main_menu()
    app.run(debug=True)
