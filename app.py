from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config["SECRET_KEY"] = "secret123"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///shop.db"

db = SQLAlchemy(app)

################ USER ################

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(200),
        nullable=False
    )

    role = db.Column(
        db.String(20),
        default="user"
    )

################ PRODUCT ################

class Product(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(200))

    price = db.Column(db.Float)

    description = db.Column(db.String(400))

################ CART ################

class Cart(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer)

    product_id = db.Column(db.Integer)

################ HOME ################

@app.route("/")

def home():

    return redirect("/login")

################ REGISTER ################

@app.route("/register", methods=["GET","POST"])

def register():

    if request.method == "POST":

        existing = User.query.filter_by(
            username=request.form["username"]
        ).first()

        if existing:

            return "Username already exists"

        user = User(

            username=request.form["username"],

            password=generate_password_hash(
                request.form["password"]
            ),

            role=request.form["role"]

        )

        db.session.add(user)

        db.session.commit()

        return redirect("/login")

    return render_template("register.html")

################ LOGIN ################

@app.route("/login", methods=["GET","POST"])

def login():

    if request.method == "POST":

        user = User.query.filter_by(
            username=request.form["username"]
        ).first()

        if user and check_password_hash(
                user.password,
                request.form["password"]):

            session["user"] = user.id

            session["role"] = user.role

            return redirect("/dashboard")

        return "Invalid Credentials"

    return render_template("login.html")

################ LOGOUT ################

@app.route("/logout")

def logout():

    session.clear()

    return redirect("/login")

################ DASHBOARD ################

@app.route("/dashboard")

def dashboard():

    products = Product.query.all()

    return render_template(

        "dashboard.html",

        products=products

    )

################ ADMIN ################

@app.route("/admin", methods=["GET","POST"])

def admin():

    if session.get("role") != "admin":

        return "Unauthorized"

    if request.method == "POST":

        product = Product(

            name=request.form["name"],

            price=float(request.form["price"]),

            description=request.form["description"]

        )

        db.session.add(product)

        db.session.commit()

    products = Product.query.all()

    return render_template(

        "admin.html",

        products=products

    )

################ CART ################

@app.route("/cart")

def cart():

    items = Cart.query.filter_by(

        user_id=session.get("user")

    ).all()

    products = []

    total = 0

    for item in items:

        p = Product.query.get(item.product_id)

        if p:

            products.append(p)

            total += p.price

    return render_template(

        "cart.html",

        products=products,

        total=total

    )

################ ADD TO CART ################

@app.route("/addcart/<int:id>")

def addcart(id):

    if "user" not in session:

        return redirect("/login")

    item = Cart(

        user_id=session["user"],

        product_id=id

    )

    db.session.add(item)

    db.session.commit()

    return redirect("/dashboard")

################ CHECKOUT ################

@app.route("/checkout")

def checkout():

    Cart.query.filter_by(

        user_id=session.get("user")

    ).delete()

    db.session.commit()

    return render_template(

        "checkout.html"

    )

if __name__ == "__main__":

    with app.app_context():

        db.create_all()

    app.run(debug=True)