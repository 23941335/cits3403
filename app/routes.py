from app import app
from flask import render_template

# More pages will be added as necessary, but this will get us started.


@app.route("/")
@app.route("/home")
def home_page():
    return render_template("pages/home.html")


@app.route("/account/login")
def login_page():
    return render_template("pages/login.html")


@app.route("/account/signup")
def signup_page():
    return render_template("pages/signup.html")


@app.route("/tournament")
def tournament_page():
    return render_template("pages/tournament.html")


# 404 not found page
@app.errorhandler(404)
def not_found(err):
    return render_template("pages/404.html", error=err)
