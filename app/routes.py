from app import app, db, models, forms
from flask import render_template, redirect, flash, request
import sqlalchemy as sa
from flask_login import current_user, login_user, logout_user, login_required
from data_import import import_csv


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
                username=form.username.data, email=form.email.data, global_role_id=1
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
        login_identifier = form.username.data
        user = db.session.scalar(
            sa.select(models.User).where(
                sa.or_(
                    models.User.username == login_identifier,
                    models.User.email == login_identifier,
                )
            )
        )
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password", "danger")
            return redirect("/account/login")
        login_user(user, remember=form.remember_me.data)  # TODO: Later add form.remember_me.data
        return redirect("/home")
    flash("Invalid username or password", "danger")
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

@app.route("/create-tournament", methods=["GET"])
@login_required
def new_tournament_page():
    form = forms.CreateTournamentForm()

    visibilities = db.session.scalars(sa.select(models.Visibility)).all()
    form.visibility.choices = [(-1, '- Select -')] + [(v.id, v.visibility.capitalize()) for v in visibilities]

    return render_template("pages/create-tournament.html", form=form)

@app.route("/create-tournament", methods=["POST"])
def create_tournament():
    form = forms.CreateTournamentForm()

    visibilities = db.session.scalars(sa.select(models.Visibility)).all()
    form.visibility.choices = [(-1, '- Select -')] + [(v.id, v.visibility.capitalize()) for v in visibilities]

    if form.validate_on_submit():
        try:
            print(form.visibility.data)
            if form.visibility.data == -1:
                form.visibility.errors.append("Please select a valid visibility option.")
                print(form.visibility.errors) 
                return render_template("pages/create-tournament.html", title="Create Tournament", form=form)


            name = form.name.data
            description = form.description.data
            vis_id = form.visibility.data
            csv_file = form.csv_file.data

            tournament = models.Tournament(title=name, description=description, visibility_id=vis_id)
            db.session.add(tournament)
            
            if csv_file:
                db.session.flush() # ensure we can reference the new tournament
                import_csv(csv_file.stream, tournament=tournament, commit_changes=False)

            db.session.commit()
            flash("Tournament created!", "success")
            return redirect("/tournament")

        except Exception as e:
            db.session.rollback()
            flash("Tournament creation failed!", "danger")
            return render_template("pages/create-tournament.html", title="Create Tournament", form=form)

    # TODO: Add error handling

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
