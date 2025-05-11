from app import app, db, models, forms
from flask import render_template, redirect, flash, request
import sqlalchemy as sa
from flask_login import current_user, login_user, logout_user, login_required
from data_import import import_csv
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from collections import defaultdict, Counter


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


@app.route("/account", methods=["GET", "POST"])
@login_required
def user_account_page():
    form = forms.UpdateAccountForm()

    if request.method == "POST" and form.validate_on_submit():
        form_type = request.form.get("form_type")

        if form_type == "edit_username":
            if form.username.data and form.username.data != current_user.username:
                existing_user = db.session.scalar(
                    sa.select(models.User).where(models.User.username == form.username.data)
                )
                if existing_user:
                    flash("Username already taken.", "danger")
                    return redirect("/account")
                current_user.username = form.username.data
                db.session.commit()
                flash("Username updated successfully.", "success")
                return redirect("/account")

        elif form_type == "edit_email":
            if form.email.data and form.email.data != current_user.email:
                existing_user = db.session.scalar(
                    sa.select(models.User).where(models.User.email == form.email.data)
                )
                if existing_user:
                    flash("Email already registered.", "danger")
                    return redirect("/account")
                current_user.email = form.email.data
                db.session.commit()
                flash("Email updated successfully.", "success")
                return redirect("/account")

        elif form_type == "edit_picture":
            if form.picture.data:
                picture_file = form.picture.data
                filename = secure_filename(picture_file.filename)

                # Makesure path is secure
                base_dir = os.path.abspath(os.path.dirname(__file__))
                upload_folder = os.path.join(base_dir, "static", "profile_pics")
                os.makedirs(upload_folder, exist_ok=True)

                save_path = os.path.join(upload_folder, filename)
                picture_file.save(save_path)

                current_user.profile_picture = f"profile_pics/{filename}"
                db.session.commit()
                flash("Profile picture updated successfully.", "success")
                return redirect("/account")

    return render_template("pages/account.html", form=form)



@app.route("/tournament")
def tournament_page():
    tid = request.args.get("id", type=int)
    if not tid:
        flash("Tournament ID missing in request", "warning")
        return redirect("/history")

    tournament = db.session.get(models.Tournament, tid)
    if not tournament:
        return render_template("pages/404.html", error=f"Tournament with ID {tid} not found."), 404
    
    games = tournament.games
    teams = list({g.team_a for g in games} | {g.team_b for g in games})
    for g in games:
        mvp_medal = db.session.query(models.GameMedals)\
            .join(models.Medal)\
            .join(models.Player)\
            .filter(
                models.GameMedals.game_id == g.id,
                models.Medal.medal_name.ilike("mvp")
            ).first()

        svp_medal = db.session.query(models.GameMedals)\
            .join(models.Medal)\
            .join(models.Player)\
            .filter(
                models.GameMedals.game_id == g.id,
                models.Medal.medal_name.ilike("svp")
            ).first()

        g.mvp = mvp_medal.player if mvp_medal else None
        g.svp = svp_medal.player if svp_medal else None


    return render_template("pages/tournament.html", tournament=tournament, games=games,teams=teams)

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
            start_time = form.start_time.data
            csv_file = form.csv_file.data

            tournament = models.Tournament(title=name, description=description, visibility_id=vis_id, start_time=start_time)
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

@app.route("/history")
def history_page():
    tournaments = db.session.scalars(sa.select(models.Tournament)).all()
    for t in tournaments:
        if isinstance(t.created_at, str):
            t.created_at = datetime.fromisoformat(t.created_at)
        if isinstance(t.start_time, str):
            t.start_time = datetime.fromisoformat(t.start_time)
    return render_template("pages/history.html", tournaments=tournaments)


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
