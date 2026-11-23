
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


# Checkout and invoice page
@app.route("/invoice", methods=["GET", "POST"])
def checkout():

    # Load menu data for invoice images
    pizzas, drinks, sides = load_data()

    cart = session.get("cart", {})
    selected_drinks = session.get("selected_drinks", {})
    selected_sides = session.get("selected_sides", {})

    # Check if an order number is provided
    order_id = request.args.get("order_id")

    if request.method == "GET" and order_id:

        # Retrieve saved order from database
        conn = get_db_connection()

        saved_order = conn.execute(
            "SELECT * FROM orders WHERE id = ?",
            (order_id,)
        ).fetchone()

        conn.close()

        if saved_order is None:
            flash("Order could not be found.")
            return redirect(url_for("order"))

        # Convert saved JSON data back into dictionaries
        cart = json.loads(saved_order["pizzas"] or "{}")
        selected_drinks = json.loads(saved_order["drinks"] or "{}")
        selected_sides = json.loads(saved_order["sides"] or "{}")

        return render_template(
            "invoice.html",
            order_id=saved_order["id"],
            customer_name=saved_order["customer_name"],
            cart=cart,
            selected_drinks=selected_drinks,
            selected_sides=selected_sides,
            pizzas=pizzas,
            pizza=pizzas,
            drinks=drinks,
            sides=sides,
            pizza_total=saved_order["pizza_total"],
            drinks_total=saved_order["drinks_total"],
            sides_total=saved_order["sides_total"],
            total=saved_order["total"]
        )

    # Calculate current cart totals
    pizza_total, drinks_total, sides_total, total = calculate_totals(
        cart,
        selected_drinks,
        selected_sides
    )

    # Customer submits checkout form
    if request.method == "POST":

        customer_name = request.form.get(
            "customer_name", ""
        ).strip()

        if not customer_name:
            flash("Please enter your name before checking out.")
            return redirect(url_for("checkout"))

        if not cart and not selected_drinks and not selected_sides:
            flash("Your cart is empty. Please add items before checkout.")
            return redirect(url_for("order"))

        # Save customer name
        session["customer_name"] = customer_name

        # Save completed order into SQLite
        try:
            conn = get_db_connection()

            cursor = conn.execute("""
                INSERT INTO orders (
                    customer_name,
                    pizzas,
                    drinks,
                    sides,
                    pizza_total,
                    drinks_total,
                    sides_total,
                    total,
                    date
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                customer_name,
                json.dumps(cart),
                json.dumps(selected_drinks),
                json.dumps(selected_sides),
                pizza_total,
                drinks_total,
                sides_total,
                total,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))

            # Get the new order number
            order_id = cursor.lastrowid

            conn.commit()
            conn.close()

            flash("Your order has been saved successfully.")

            # Redirect to invoice using the saved order number
            return redirect(
                url_for("checkout", order_id=order_id)
            )

        except sqlite3.Error as error:
            print("Database error:", error)
            flash("There was a problem saving your order.")
            return redirect(url_for("checkout"))

    # Display checkout page
    return render_template(
        "checkout.html",
        cart=cart,
        selected_drinks=selected_drinks,
        selected_sides=selected_sides,
        total=total
    )





# Run Flask
if __name__ == "__main__":
    app.run(debug=True)
