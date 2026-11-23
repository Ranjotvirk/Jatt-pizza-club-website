
import os
import json
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash

# Project folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "jatt_pizza.db")

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)

app.secret_key = "jatt_pizza_club_secret_key"


# Database connection
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# Create orders table
def init_db():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            pizzas TEXT,
            drinks TEXT,
            sides TEXT,
            pizza_total REAL,
            drinks_total REAL,
            sides_total REAL,
            total REAL,
            date TEXT
        )
    """)

    conn.commit()
    conn.close()


# Initialise database
init_db()


# Load pizza, drinks, and sides data
def load_data():
    pizza_file = os.path.join(BASE_DIR, "data", "pizza.json")
    drinks_file = os.path.join(BASE_DIR, "data", "drinks.json")
    sides_file = os.path.join(BASE_DIR, "data", "sides.json")

    with open(pizza_file, encoding="utf-8") as file:
        pizzas = json.load(file)

    with open(drinks_file, encoding="utf-8") as file:
        drinks = json.load(file)

    with open(sides_file, encoding="utf-8") as file:
        sides = json.load(file)

    return pizzas, drinks, sides


# Calculate order totals
def calculate_totals(cart, selected_drinks, selected_sides):

    pizza_total = sum(
        float(item["price"]) * int(item["quantity"])
        for item in cart.values()
    )

    drinks_total = sum(
        float(price)
        for price in selected_drinks.values()
    )

    sides_total = sum(
        float(price)
        for price in selected_sides.values()
    )

    total = pizza_total + drinks_total + sides_total

    return pizza_total, drinks_total, sides_total, total


# Home page
@app.route("/")
def index():
    return render_template("index.html")


# Separate Order page
@app.route("/order")
def order():
    pizzas, drinks, sides = load_data()

    return render_template(
        "order.html",
        pizza=pizzas,
        pizzas=pizzas,
        drinks=drinks,
        sides=sides,
        cart=session.get("cart", {}),
        selected_drinks=session.get("selected_drinks", {}),
        selected_sides=session.get("selected_sides", {})
    )


# Test page
@app.route("/test")
def test():
    pizzas, drinks, sides = load_data()

    return render_template(
        "index1.html",
        pizza=pizzas,
        pizzas=pizzas,
        drinks=drinks,
        sides=sides,
        cart=session.get("cart", {}),
        selected_drinks=session.get("selected_drinks", {}),
        selected_sides=session.get("selected_sides", {})
    )


# About page
@app.route("/about")
def about():
    return render_template("about.html")


# Order history page
@app.route("/orders")
def order_history():

    orders = []

    try:
        conn = get_db_connection()

        orders = conn.execute(
            "SELECT * FROM orders ORDER BY date DESC"
        ).fetchall()

        conn.close()

    except sqlite3.Error as error:
        print("Database error:", error)
        flash("Order history is currently unavailable.")

    return render_template(
        "order_history.html",
        orders=orders
    )





# Run Flask
if __name__ == "__main__":
    app.run(debug=True)
