import urllib.parse
from flask import Flask, render_template, request

app = Flask(__name__)

FOOD = [
    {"name": "Jollof ", "price": 2500, "image": "jollof.jpg"},
    {"name":" chicken", "price": 3000, "image": "chicken.jpg"},
    {"name": "Fried plantain", "price": 1000, "image": "fried plantain.jpg"},
    {"name": "Salad", "price": 1500, "image": "salad.jpg"},
]

DRINKS = [
    {"name": "Chapman", "price": 1500, "image": "chapman.jpg"},
    {"name": "Coke", "price": 500, "image": "coke.jpg"},
    {"name": "Fanta", "price": 500, "image": "fanta.jpg"},
]
# ---- Business details (public information shown on the website) ----
PHONE = "09066572936"
WHATSAPP = "2349066572936"
BANK_NAME = "opay digital bank"
ACCOUNT_NAME = "Vipade Restaurant and Bar"
ACCOUNT_NUMBER = "9066572936"


@app.context_processor
def business_details():
    return {
        "PHONE": PHONE, "WHATSAPP": WHATSAPP, "BANK_NAME": BANK_NAME,
        "ACCOUNT_NAME": ACCOUNT_NAME, "ACCOUNT_NUMBER": ACCOUNT_NUMBER,
    }

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/menu")
def menu():
    return render_template("menu.html", food=FOOD, drinks=DRINKS)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    sent = False
    if request.method == "POST":
        name = request.form["name"]
        message = request.form["message"]
        with open("messages.txt", "a", encoding="utf-8") as f:
            f.write(f"{name}: {message}\n")
        sent = True
    return render_template("contact.html", sent=sent)
@app.route("/order", methods=["GET", "POST"])
def order():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        method = request.form.get("method", "Pickup")
        address = request.form.get("address", "").strip()
        note = request.form.get("note", "").strip()

        items = []
        total = 0
        for i, item in enumerate(FOOD + DRINKS):
            try:
                qty = int(request.form.get(f"qty_{i}", "0"))
            except ValueError:
                qty = 0
            qty = max(0, min(qty, 50))
            if qty > 0:
                cost = qty * item["price"]
                items.append({"name": item["name"], "qty": qty, "cost": cost})
                total += cost

        error = None
        if not name or not phone:
            error = "Please enter your name and phone number."
        elif not items:
            error = "Please choose at least one item."
        elif method == "Delivery" and not address:
            error = "Please enter your delivery address."

        if error:
            return render_template("order.html", food=FOOD, drinks=DRINKS, error=error)

        lines = [f"New order from {name} ({phone})", f"Type: {method}"]
        if method == "Delivery":
            lines.append(f"Address: {address}")
        for it in items:
            lines.append(f"{it['qty']} x {it['name']} = N{it['cost']:,}")
        lines.append(f"Total: N{total:,}")
        if note:
            lines.append(f"Note: {note}")
        text = "\n".join(lines)

        with open("orders.txt", "a", encoding="utf-8") as f:
            f.write(text + "\n---\n")

        wa_link = f"https://wa.me/{WHATSAPP}?text=" + urllib.parse.quote(text)
        return render_template("order_done.html", items=items, total=total,
                               name=name, method=method, wa_link=wa_link)

    return render_template("order.html", food=FOOD, drinks=DRINKS, error=None)

if __name__ == "__main__":
    app.run(debug=True)
