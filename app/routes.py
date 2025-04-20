from app import app
from flask import render_template


# Root route
@app.route("/")
def hello_word():
    return "Hello, World!"


# 404 not found page
@app.errorhandler(404)
def not_found(err):
    return render_template("404.html", error=err)
