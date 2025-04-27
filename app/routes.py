from app import app
from flask import render_template, redirect

# More pages will be added as necessary, but this will get us started.


@app.route("/")
@app.route("/home")
def home_page():
    return render_template("pages/home.html")


@app.route("/account/login", methods=["GET"])
def login_page():
    return render_template("pages/login.html")


@app.route("/account/signup", methods=["GET"])
def signup_page():
    return render_template("pages/signup.html")


@app.route("/account/login", methods=["POST"])
def api_login():
    # temporary placeholder - go to index page
    return redirect("/")


@app.route("/account/signup", methods=["POST"])
def api_create_account():
    # temporary placeholder - go to index page
    return redirect("/")


@app.route("/tournament")
def tournament_page():
    return render_template("pages/tournament.html")


@app.route("/create-tournament")
def new_tournament_page():
    return render_template("pages/create-tournament.html")


@app.route("/tournament/team")
def team_results_page():
    return render_template("pages/stats_team.html")


@app.route("/tournament/game")
def tournament_game_view():
    return render_template("pages/stats_game.html")


@app.route("/tournament/player")
def tournament_player_view():
    return render_template("pages/stats_player.html")


# 404 not found page
@app.errorhandler(404)
def not_found(err):
    return render_template("pages/404.html", error=err)
