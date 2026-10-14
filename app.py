
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

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    pizza_name = request.form.get("pizza")
    quantity = int(request.form.get("quantity", 1))

    pizzas = load_data()
    cart = session.get('cart', {})

    if pizza_name not in pizzas:
        flash("Invalid pizza selected.")
        return redirect(url_for('index'))

    if quantity < 1:
        flash("Quantity must be at least 1.")
        return redirect(url_for('index'))

    if pizza_name in cart:
        cart[pizza_name]['quantity'] += quantity
    else:
        cart[pizza_name] = {
            'price': pizzas[pizza_name]['price'],
            'quantity': quantity
        }

    session['cart'] = cart
    session.modified = True

    suffix = "" if quantity == 1 else "s"
    flash(f"{quantity} {pizza_name}{suffix} added to cart.")

    return redirect(url_for('index'))

@app.route('/select_drink', methods=['POST'])
def select_drink():
    selected_drinks = session.get('selected_drinks', {})
    drinks = load_data()

    selected_keys = request.form.getlist('drinks')

    if selected_keys:
        selected_drinks = {}

        for drink in selected_keys:
            if drink in drinks:
                selected_drinks[drink] = float(drinks[drink]['price'])

        if selected_drinks:
            drink_names = ", ".join(selected_drinks.keys())
            flash(f"Added {drink_names} to your cart!")
        else:
            flash("Invalid drink selected.")
    else:
        selected_drinks = {}
        flash("All drinks removed from your cart.")

    session['selected_drinks'] = selected_drinks
    session.modified = True

    return redirect(url_for('index'))



if __name__ == "__main__":
    app.run(debug=True)
