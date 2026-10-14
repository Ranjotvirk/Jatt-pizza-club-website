
import json
import sqlite3
import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'your_secret_key'


@app.route("/")
def index():
    pizza, drinks = load_data()

    cart = session.get("cart", {})
    selected_drinks = session.get("selected_drinks", {})

    return render_template(
        "index.html",
        pizza=pizza,
        drinks=drinks,
        cart=cart,
        selected_drinks=selected_drinks
    )


def load_data():
    with open("data/pizza.json", encoding="utf-8") as file:
        pizzas = json.load(file)

    with open("data/drinks.json", encoding="utf-8") as file:
        drinks = json.load(file)

    return pizzas, drinks


@app.route("/test")
def test():
    pizza, drinks = load_data()
    cart = session.get("cart", {})

    return render_template(
        "index1.html",
        pizza=pizza,
        drinks=drinks,
        cart=cart
    )

@app.route("/about")
def about():
    return render_template("about.html")


@app.route('/orders')
def order_history():
    return render_template('order_history.html')

@app.route('/checkout')
def checkout():
     return render_template('invoice.html')



if __name__ == "__main__":
    app.run(debug=True)
