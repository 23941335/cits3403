from app import app, db, models, forms
from flask import render_template, redirect, flash, request
import sqlalchemy as sa
from flask_login import current_user, login_user, logout_user


@app.route("/")
@app.route("/home")
def home_page():
    return render_template("pages/home.html")


@app.route("/account/signup", methods=["GET", "POST"])
def signup_page():
    form = forms.SignupForm()
    if request.method == "POST" and form.validate_on_submit():
        try:
            new_user = models.User(
                username=form.username.data, 
                email=form.email.data, 
                global_role_id=1
            )
            new_user.set_password(form.password.data)
            db.session.add(new_user)
            db.session.commit()
            flash("Your account has been created!", "success")
            return redirect("/account/login")
        
        except Exception as e:
            db.session.rollback()
            return render_template("pages/signup.html", title="Sign Up", form=form)

    return render_template("pages/signup.html", title="Sign Up", form=form)


@app.route("/account/login", methods=["GET"])
def login_page():
    if current_user.is_authenticated:
        return redirect("/home")
    return render_template("pages/login.html", title="Login", form=forms.LoginForm())


@app.route("/account/login", methods=["POST"])
def api_login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(models.User).where(models.User.username == form.username.data)
        )
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect("/account/login")
        login_user(user, remember=False)  # TODO: Later add form.remember_me.data
        return redirect("/home")
    flash("Invalid username or password")
    return redirect("/account/login")


@app.route("/account/logout")
def user_logout():
    logout_user()
    return redirect("/")


@app.route("/account", methods=["GET"])
def user_account_page():
    if current_user.is_authenticated:
        return render_template("pages/account.html")
    else:
        return redirect("/account/login")


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
