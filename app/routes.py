from app import app
from flask import render_template, redirect, request

from app.handle_csv import parse_csv

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

# DATA UPLOAD ROUTES
# based on https://flask.palletsprojects.com/en/stable/patterns/fileuploads/

@app.route('/upload', methods=['POST'])
def upload_file():
    file_upload_name = 'results_file' # the value of the HTML `name` attribute
    
    def is_csv(file_name):
        return '.' in file_name and file_name.rsplit('.', 1)[1].lower() == 'csv'

    print('Files', request.files)

    if file_upload_name not in request.files:
        return "No file part", 400

    file = request.files[file_upload_name]
    if file.filename == '':
        return "No selected file", 400
    
    if file and is_csv(file.filename):
        return "File uploaded sucessfully."

# 404 not found page
@app.errorhandler(404)
def not_found(err):
    return render_template("pages/404.html", error=err)
