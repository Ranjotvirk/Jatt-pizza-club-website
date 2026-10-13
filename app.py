
import json
import sqlite3
import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'your_secret_key'


def load_data():
    with open("data/pizza.json", encoding="utf-8") as file:
        pizzas = json.load(file)

    with open("data/drinks.json", encoding="utf-8") as file:
        drinks = json.load(file)

    return pizzas, drinks


@app.route("/")
def index():
    pizzas, drinks = load_data()

    cart = session.get("cart", {})
    selected_drinks = session.get("selected_drinks", {})

    return render_template(
        "index.html",
        pizzas=pizzas,
        drinks=drinks,
        cart=cart,
        selected_drinks=selected_drinks
    )


if __name__ == "__main__":
    app.run(debug=True)
