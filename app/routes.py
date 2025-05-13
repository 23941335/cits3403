from app import app, db, models, forms
from flask import render_template, redirect, flash, request
import sqlalchemy as sa
from flask_login import current_user, login_user, logout_user, login_required
from data_import import import_csv
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from sqlalchemy.orm import selectinload

if not app.config.get('SECRET_KEY'):
    raise ValueError("Please set the environment variable SECRET_KEY")

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
    teams = sorted(
        list({g.team_a for g in games} | {g.team_b for g in games}),
        key=lambda t: t.team_name.lower()
    )
    # Find the final game to determine the winner
    final_game = max(games, key=lambda g: g.round, default=None)
    final_winner_id = final_game.winning_team if final_game else None

    # Assign status to teams based on the final winner
    team_status = {}
    for team in teams:
        if team.id == final_winner_id:
            team_status[team.id] = "winner"
        else:
            team_status[team.id] = "loser"


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


    return render_template("pages/tournament.html", tournament=tournament, games=games,teams=teams, team_status=team_status)


@app.route("/tournament/delete/<int:tid>", methods=["POST"])
@login_required
def delete_tournament(tid):
    tournament = db.session.get(models.Tournament, tid)
    if not tournament:
        flash("Tournament not found.", "danger")
        return redirect("/history")

    is_owner = db.session.scalar(sa.select(models.TournamentUsers).where(
        models.TournamentUsers.tournament_id == tid,
        models.TournamentUsers.user_id == current_user.id
    ))

    if not is_owner:
        flash("You do not have permission to delete this tournament.", "danger")
        return redirect(f"/tournament?id={tid}")

    try:
        db.session.delete(tournament)
        db.session.commit()
        flash("Tournament deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash("Failed to delete tournament.", "danger")

    return redirect("/history")


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
            if form.visibility.data == -1:
                form.visibility.errors.append("Please select a valid visibility option.")
                return render_template("pages/create-tournament.html", title="Create Tournament", form=form)

            name = form.name.data
            description = form.description.data
            vis_id = form.visibility.data
            start_time = form.start_time.data
            csv_file = form.csv_file.data
            
            tournament = models.Tournament(title=name, description=description, visibility_id=vis_id, start_time=start_time)
            db.session.add(tournament)
            db.session.flush()  # Ensure we can reference the new tournament
            
            tournament_user = models.TournamentUsers(
                tournament_id=tournament.id,
                user_id=current_user.id,
                tournament_role_id=1            # TODO
            )
            db.session.add(tournament_user)
            
            if csv_file:
                import_csv(csv_file.stream, tournament=tournament, commit_changes=False)

            db.session.commit()
            flash("Tournament created!", "success")
            return redirect(f"/tournament?id={tournament.id}")

        except Exception as e:
            db.session.rollback()
            print(e)
            flash("Tournament creation failed!", "danger")
            return render_template("pages/create-tournament.html", title="Create Tournament", form=form)

    # TODO: Add error handling

@app.route("/history")
def history_page():
    stmt = sa.select(models.Tournament).options(selectinload(models.Tournament.users))
    tournaments = db.session.scalars(stmt).all()
    for t in tournaments:
        print(f"Tournament {t.id}: {[u.user_id for u in t.users]}")
        if isinstance(t.created_at, str):
            t.created_at = datetime.fromisoformat(t.created_at)
        if isinstance(t.start_time, str):
            t.start_time = datetime.fromisoformat(t.start_time)
    return render_template("pages/history.html", tournaments=tournaments)

@app.route("/tournament/game")
def tournament_game_view():
    gid = request.args.get("id", type=int)
    if not gid:
        flash("Game ID missing in request", "warning")
        return redirect("/history")

    game = db.session.get(models.Game, gid)
    if not game:
        return render_template("pages/404.html", error=f"Game with ID {gid} not found."), 404

    medal_by_player = {}
    for gm in game.game_medals:
        medal = db.session.get(models.Medal, gm.medal_id)
        if gm.player_id not in medal_by_player:
            medal_by_player[gm.player_id] = []
        medal_by_player[gm.player_id].append(medal.medal_name)

    mvp_name = next((p.player.gamertag for p in game.game_players if 'MVP' in medal_by_player.get(p.player_id, [])), "N/A")
    svp_name = next((p.player.gamertag for p in game.game_players if 'SVP' in medal_by_player.get(p.player_id, [])), "N/A")
    return render_template("pages/stats_game.html", game=game, players=game.game_players, medals=medal_by_player, mvp=mvp_name, svp=svp_name)



@app.route("/tournament/team")
def team_results_page():
    tid = request.args.get("t", type=int)
    team_id = request.args.get("id", type=int)

    if not tid or not team_id:
        flash("Missing tournament or team ID", "warning")
        return redirect("/history")

    tournament = db.session.get(models.Tournament, tid)
    team = db.session.get(models.Team, team_id)

    if not tournament or not team:
        return render_template("pages/404.html", error="Invalid tournament or team ID"), 404

    # Display tournament details for the team
    game_players = db.session.scalars(
        sa.select(models.GamePlayers)
        .where(
            models.GamePlayers.team_id == team_id,
            models.GamePlayers.game.has(models.Game.tournament_id == tid)
        )
    ).all()
    games_played = set()
    kills = deaths = assists = damage = healing = 0
    accuracy_list = []

    for gp in game_players:
        games_played.add(gp.game_id)
        kills += gp.kills
        deaths += gp.deaths
        assists += gp.assists
        damage += gp.damage
        healing += gp.healing
        accuracy_list.append(gp.accuracy_pct)

    kda_ratio = round((kills + assists) / (deaths if deaths > 0 else 1), 2)
    avg_accuracy = round(sum(accuracy_list) / len(accuracy_list), 1) if accuracy_list else 0

    team_summary = {
        'games': len(games_played),
        'kda_ratio': kda_ratio,
        'total_kills': kills,
        'total_assists': assists,
        'total_damage': damage,
        'total_healing': healing,
        'avg_accuracy': avg_accuracy
    }


    return render_template("pages/stats_team.html", team=team, tournament=tournament, game_players=game_players, team_summary=team_summary)



@app.route("/tournament/player")
def tournament_player_view():
    return render_template("pages/stats_player.html")


# 404 not found page
@app.errorhandler(404)
def not_found(err):
    return render_template("pages/404.html", error=err)