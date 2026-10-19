from flask import Flask, render_template, request

app = Flask(__name__)

FOOD = [
    {"name": "Jollof ", "price": 2500, "image": "jollof.jpg"},
    {"name":" chicken", "price": 3000, "image": "chicken.jpg"},
    {"name": "Fried plantain", "price": 1000, "image": "fried_plantain.jpg"},
    {"name": "Salad", "price": 1500, "image": "salad.jpg"},
]

DRINKS = [
    {"name": "Chapman", "price": 1500, "image": "chapman.jpg"},
    {"name": "Coke", "price": 500, "image": "coke.jpg"},
    {"name": "Fanta", "price": 500, "image": "fanta.jpg"},
]


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


if __name__ == "__main__":
    app.run(debug=True)
