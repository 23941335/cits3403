from app import app, db, models, forms
from flask import render_template, redirect, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlalchemy as sa
from flask_login import current_user, login_user

@app.route("/")
@app.route("/home")
def home_page():
    return render_template("pages/home.html")

@app.route("/account/login", methods=["GET"])
def login_page():
    if current_user.is_authenticated:
        return redirect("/home")
    return render_template('pages/login.html', title='Login', form=forms.LoginForm())

@app.route("/account/signup", methods=["GET", "POST"])
def signup_page():
    form = forms.SignupForm(request.form)
    if request.method == "POST":
        if form.validate_on_submit():
            new_user = models.User(username=form.username.data, email=form.email.data, global_role_id=1)
            new_user.set_password(form.password.data)
            db.session.add(new_user)
            db.session.commit()
            return redirect("/account/login")
        else:
            return 'form validation failure', 400

    return render_template("pages/signup.html", form=form)

@app.route("/account/login", methods=["POST"])
def api_login():
    form = forms.LoginForm()
    print("Inside api_login()")
    if form.validate_on_submit():
        print("form validated")
        user = db.session.scalar(
            sa.select(models.User).where(models.User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect("/account/login")
        login_user(user, remember=False) # Later add form.remember_me.data
        return redirect("/home")
    flash('Invalid username or password')
    return redirect("/account/login")


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

# API
# @app.route("/api/account/create", methods=["POST"])
# def api_account_create():
#     # TODO
#     pass
