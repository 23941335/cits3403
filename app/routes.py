from app import app, db, models, forms
from flask import render_template, redirect, flash, request, jsonify, session
import sqlalchemy as sa
from flask_login import current_user, login_user, logout_user, login_required
from data_import import import_csv
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from sqlalchemy.orm import selectinload
from collections import defaultdict
from functools import wraps

if not app.config.get('SECRET_KEY'):
    raise ValueError("Please set the environment variable SECRET_KEY")



def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            # Store the requested URL in the session
            session['next'] = request.url
            return redirect(f"/account/login")
        return f(*args, **kwargs)
    return decorated_function



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
        
        login_user(user, remember=form.remember_me.data)

        if 'next' in session:
            next_page = session.get('next')
            session.pop('next')
            if next_page:
                return redirect(next_page)
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
    tournaments = db.session.scalars(
        sa.select(models.Tournament)
        .join(models.TournamentUsers)
        .where(models.TournamentUsers.user_id == current_user.id)
    ).all()

    return render_template("pages/account.html", form=form, tournaments=tournaments)

@app.route("/account/delete-tournament/<int:tournament_id>", methods=["POST"])
@login_required
def delete_user_tournament(tournament_id):
    tournament = db.session.get(models.Tournament, tournament_id)

    # Check if the tournament exists and if the current user is a participant
    if not tournament or not any(tu.user_id == current_user.id for tu in tournament.users):
        flash("You do not have permission to delete this tournament.", "danger")
        return redirect("/account")

    try:
        db.session.delete(tournament)
        db.session.commit()
        flash(f"Tournament {tournament.title} deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash("Failed to delete tournament.", "danger")

    return redirect("/account")



@app.route("/tournament", methods=["GET"])
def tournament_page():
    tid = request.args.get("id", type=int)
    if not tid:
        flash("Tournament ID missing in request", "warning")
        return redirect("/history")

    tournament = db.session.get(models.Tournament, tid)
    if not tournament:
        return render_template("pages/404.html", error=f"Tournament with ID {tid} not found."), 404

    if not tournament.user_can_access(current_user):
        return render_template("pages/404.html", error=f"You do not have access to this tournament."), 403

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
    
    # All users who have the owner role for this tournament (usually will be one, but could support more)
    owners = [tu.user for tu in tournament.users if tu.tournament_role.role_name == 'tournament_owner']
    # All users this tournament has been shared with (i.e. all that have access to it, minus owners).
    users_shared = [tu.user for tu in tournament.users if tu.user not in owners]

    # All users who don't have access to the tournament
    users_unshared = db.session.query(models.User).filter(
        models.User.id.not_in([u.id for u in users_shared]),
        models.User.id.not_in([u.id for u in owners])
    ).all()
    
    form = forms.UserSelectionForm()
    form.tid.data = tournament.id


    return render_template("pages/tournament.html", tournament=tournament, games=games,teams=teams, team_status=team_status,
                           sharedUsers=users_shared, unsharedUsers=users_unshared, owners=owners, form=form)


@app.route("/tournament/share", methods=["POST"])
def share():

    # TODO
    DEFAULT_ROLE_ID = 1

    form = forms.UserSelectionForm()
    if form.validate_on_submit():
        try:
            tournament = db.session.query(models.Tournament).filter_by(id=form.tid.data).one()
            owners = [tu.user for tu in tournament.users if tu.tournament_role.role_name == 'tournament_owner']
            tourn_users_shared = [tu for tu in tournament.users if tu.user not in owners]
            
            
            # Process form to insert values into the database
            user_ids_to_share = []
            if form.selected_users.data:
                user_ids_to_share = [int(uid) for uid in form.selected_users.data.split(',')]

            for user_id in user_ids_to_share:
                existing_tu = db.session.query(models.TournamentUsers).filter_by(
                    tournament_id=form.tid.data,
                    user_id=user_id
                ).first()
                
                if not existing_tu:
                    user = db.session.query(models.User).where(models.User.id == user_id).one()
                    tournament_user = models.TournamentUsers(
                        tournament_id=form.tid.data,
                        user_id=user.id,
                        tournament_role_id=DEFAULT_ROLE_ID
                    )
                    db.session.add(tournament_user)

            # Revoke access to users who have already if deselected
            for tourn_user in tourn_users_shared:
                if tourn_user.user_id not in user_ids_to_share:
                    db.session.delete(tourn_user)

            db.session.commit()

        except Exception as e:
            db.session.rollback()
            raise e
    
    return redirect(f"/tournament?id={form.tid.data}")


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

    #TODO: check user actually has permission to do this

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
            
            tournament_role = db.session.query(models.Role).where(models.Role.role_name == 'tournament_owner').one()

            tournament_user = models.TournamentUsers(
                tournament_id=tournament.id,
                user_id=current_user.id,
                tournament_role_id=tournament_role.id
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

@app.route("/tournament/upload", methods=["POST"])
def tournament_upload():
    '''For uploading data after tournament creation, not initial upload on creation.'''
    try:
        tid = request.form.get('tid')
        if not tid:
            return "Tournament ID required", 400

        tournament = db.session.get(models.Tournament, tid)
        if not tournament:
            return "Tournament not found", 404

        #TODO: check permissions before doing this

        csv_file = request.files.get('file')
        if not csv_file:
            return "No file provided", 400

        #TODO: prevent uploading duplicate data. Consider comparing file hashes, etc.
        import_csv(csv_file.stream, tournament=tournament, commit_changes=True)
        flash("Tournament data uploaded successfully!", "success")
        return redirect(f"/tournament?id={tid}")

    except Exception as e:
        db.session.rollback()
        print(e)
        flash("Failed to upload tournament data", "danger")
        return redirect(f"/tournament?id={tid}")


@app.route("/history", methods=['GET'])
def history_page():
    """Render the tournament history page (initial load before AJAX takes over)."""
    # Render the template without passing data, as AJAX will load the tournaments
    return render_template("pages/history.html")



@app.route("/api/tournaments", methods=['GET'])
def api_get_tournaments():
    """API endpoint to retrieve tournaments with optional search filter and category filter."""
    search_query = request.args.get('search', '').lower()
    filter_type = request.args.get('filter', 'all')  # Filter parameters: 'owned', 'shared', 'discover', or 'all'
    
    # Start with a base query
    stmt = sa.select(models.Tournament).options(
        selectinload(models.Tournament.users).selectinload(models.TournamentUsers.tournament_role),
        selectinload(models.Tournament.visibility)
    )
    
    # Apply search filter if provided
    if search_query:
        stmt = stmt.filter(models.Tournament.title.ilike(f'%{search_query}%'))
    
    # Get all tournaments matching the search criteria
    tournaments = db.session.scalars(stmt).all()
    
    # Filter based on the filter_type
    filtered_tournaments = []
    
    for t in tournaments:
        # Get owners and shared users
        owners = [tu.user for tu in t.users if tu.tournament_role.role_name == 'tournament_owner']
        owner_ids = [user.id for user in owners if user]
        
        is_owner = current_user.is_authenticated and current_user.id in owner_ids
        is_public = t.visibility.visibility == 'public' if hasattr(t, 'visibility') and t.visibility else False
        is_shared = False
        
        if current_user.is_authenticated:
            is_shared = any(tu.user_id == current_user.id and tu.tournament_role.role_name != 'tournament_owner' 
                            for tu in t.users)
        
        # Apply filters
        if filter_type == 'owned' and is_owner:
            filtered_tournaments.append(t)
        elif filter_type == 'shared' and is_shared and not is_public:
            filtered_tournaments.append(t)
        elif filter_type == 'discover' and is_public and not is_owner and not is_shared:
            filtered_tournaments.append(t)
        elif filter_type == 'all':
            if is_owner or is_shared or is_public:
                filtered_tournaments.append(t)
    
    # Convert tournaments to a list of dictionaries
    tournaments_data = []
    for t in filtered_tournaments:
        # Handle date formatting
        created_at = t.created_at
        start_time = t.start_time
        
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        
        if isinstance(start_time, str):
            start_time = datetime.fromisoformat(start_time)
            
        # Build the tournament data dictionary
        tournament_data = {
            'id': t.id,
            'title': t.title,
            'description': t.description,
            'created_at': created_at.isoformat() if created_at else None,
            'start_time': start_time.isoformat() if start_time else None,
            'visibility': {
                'visibility': t.visibility.visibility if hasattr(t, 'visibility') and t.visibility else 'Unknown'
            },
            'users': [{'user_id': link.user_id} for link in t.users] if t.users else [],
            'is_owner': current_user.is_authenticated and current_user.id in [tu.user_id for tu in t.users 
                                                                       if tu.tournament_role.role_name == 'tournament_owner'],
            'is_shared': current_user.is_authenticated and current_user.id in [tu.user_id for tu in t.users 
                                                                       if tu.tournament_role.role_name != 'tournament_owner'],
            'is_public': t.visibility.visibility == 'public' if hasattr(t, 'visibility') and t.visibility else False
        }
        
        tournaments_data.append(tournament_data)
    
    return jsonify({'tournaments': tournaments_data})



@app.route("/tournament/game")
def tournament_game_view():
    tid = request.args.get("t", type=int)
    gid = request.args.get("id", type=int)
    if not tid or not gid:
        flash("Tournament or game ID missing in request", "warning")
        return redirect("/history")

    tournament = db.session.get(models.Tournament, tid)
    game = db.session.get(models.Game, gid)
    
    if not tournament or not game:
        return render_template("pages/404.html", error="Invalid tournament or game ID"), 404
    
    if not tournament.user_can_access(current_user):
        return render_template("pages/404.html", error=f"You do not have access to this tournament."), 403


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
    
    if not tournament.user_can_access(current_user):
        return render_template("pages/404.html", error=f"You do not have access to this tournament."), 403

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
    # Gather all medals belonging to players in this team and this tournament
    total_medals = (
        db.session.query(models.GameMedals)
        .join(models.GameMedals.game)  # JOIN to game
        .filter(
            models.GameMedals.player_id.in_([gp.player_id for gp in game_players]),
            models.Game.tournament_id == tid
        )
        .count()
    )
    total_blocked = 0

    # player stastics list
    player_stats = defaultdict(lambda: {"damage": 0, "healing": 0, "blocked": 0, "games": 0})

    for gp in game_players:
        total_blocked += gp.damage_blocked or 0
        pid = gp.player_id
        player_stats[pid]["damage"] += gp.damage or 0
        player_stats[pid]["healing"] += gp.healing or 0
        player_stats[pid]["blocked"] += gp.damage_blocked or 0
        player_stats[pid]["games"] += 1

    # Average stats
    games_played_count = len(games_played) if games_played else 1

    avg_kda_ratio = round(kda_ratio / games_played_count, 2)
    avg_damage = round(damage / games_played_count, 2)
    avg_healing = round(healing / games_played_count, 2)
    avg_blocked = round(total_blocked / games_played_count, 2)

    player_ids = list(player_stats.keys())
    players_by_id = {
        p.id: p.gamertag for p in db.session.query(models.Player).filter(models.Player.id.in_(player_ids)).all()
    }

    # top players
    def get_top_player(metric):
        best = max(player_stats.items(), key=lambda x: x[1][metric] / max(x[1]["games"], 1), default=None)
        return players_by_id.get(best[0], "N/A") if best else "N/A"

    top_damage_player = get_top_player("damage")
    top_healing_player = get_top_player("healing")
    top_blocked_player = get_top_player("blocked")

    # FMVP
    final_game = db.session.query(models.Game).filter(
        models.Game.tournament_id == tid
    ).order_by(models.Game.round.desc()).first()

    fmvp_player = "N/A"
    if final_game:
        fmvp_medal = next(
            (gm for gm in final_game.game_medals if gm.medal.medal_name.lower() == "mvp"),
            None
        )
        if fmvp_medal and fmvp_medal.player_id in player_ids:
            fmvp_player = players_by_id.get(fmvp_medal.player_id, "N/A")

    team_summary = {
        'games': games_played_count,
        'total_kills': kills,
        'total_deaths': deaths,
        'total_assists': assists,
        'total_damage': damage,
        'total_healing': healing,
        'total_blocked': total_blocked,
        'avg_accuracy': avg_accuracy,
        'kda_ratio': kda_ratio,
        'avg_kda_ratio': avg_kda_ratio,
        'avg_damage': avg_damage,
        'avg_healing': avg_healing,
        'avg_blocked': avg_blocked,
        'total_medals': total_medals,
        'top_damage_player': top_damage_player,
        'top_healing_player': top_healing_player,
        'top_blocked_player': top_blocked_player,
        'fmvp_player': fmvp_player
    }
    # Caluculate the max round number for specific team
    # This is the max round number for the team in the tournament
    # This round number is used to display the correct round in the game view
    round_numbers = [
        gp.game.round for gp in game_players if gp.game and gp.game.round is not None
    ]
    max_round = max(round_numbers) if round_numbers else 1

    stats_cards = [
    {"title": "Total Kills", "value": team_summary["total_kills"]},
    {"title": "Total Deaths", "value": team_summary["total_deaths"]},
    {"title": "Total Assists", "value": team_summary["total_assists"]},
    {"title": "Total Medals", "value": team_summary["total_medals"]},
    {"title": "Total Damage", "value": team_summary["total_damage"]},
    {"title": "Total Healing", "value": team_summary["total_healing"]},
    {"title": "Total Blocked", "value": team_summary.get("total_blocked", "N/A")},
    {"title": "Average Accuracy", "value": f"{team_summary['avg_accuracy']}%"},
    {"title": "Total K/D Ratio", "value": team_summary["kda_ratio"]},
    {"title": "Avg K/D Ratio per Game", "value": team_summary.get("avg_kda_ratio", "N/A")},
    {"title": "Avg Damage per Game", "value": team_summary.get("avg_damage", "N/A")},
    {"title": "Avg Healing per Game", "value": team_summary.get("avg_healing", "N/A")},
    {"title": "Avg Blocked per Game", "value": team_summary.get("avg_blocked", "N/A")},
    {"title": "Top Damage Player", "value": team_summary.get("top_damage_player", "N/A")},
    {"title": "Top Healing Player", "value": team_summary.get("top_healing_player", "N/A")},
    {"title": "Top Blocked Player", "value": team_summary.get("top_blocked_player", "N/A")},
    {"title": "FMVP", "value": team_summary.get("fmvp_player", "N/A")},
    ]

    games = db.session.scalars(
    sa.select(models.Game).where(models.Game.tournament_id == tid)
    ).all()

    chart_data = {
        "rounds": [],
        "kills": [],
        "damage": [],
        "healing": []
    }

    for g in sorted(games, key=lambda x: x.round):
        if g.team_a_id != team.id and g.team_b_id != team.id:
            continue # Skip games not involving the team

        round_label = f"R{g.round}"
        team_gps = [gp for gp in g.game_players if gp.team_id == team.id]

        chart_data["rounds"].append(round_label)
        chart_data["kills"].append(sum(gp.kills for gp in team_gps))
        chart_data["damage"].append(sum(gp.damage for gp in team_gps))
        chart_data["healing"].append(sum(gp.healing for gp in team_gps))



    return render_template("pages/stats_team.html", team=team, tournament=tournament, game_players=game_players, team_summary=team_summary, max_round=max_round, stats_cards=stats_cards, chart_data=chart_data)



@app.route("/tournament/player")
def tournament_player_view():
    pid = request.args.get("id", type=int)
    tid = request.args.get("t", type=int)
    gid = request.args.get("g", type=int)
    if not pid:
        flash("Player ID missing in request", "warning")
        return redirect("/history")
    
    tournament = db.session.get(models.Tournament, tid)

    if not tournament:
        return render_template("pages/404.html", error="Invalid tournament ID"), 404
    
    if not tournament.user_can_access(current_user):
        return render_template("pages/404.html", error=f"You do not have access to this tournament."), 403

    player = db.session.get(models.Player, pid)
    if not player:
        return render_template("pages/404.html", error=f"Player with ID {pid} not found."), 404
    player_games = [gp.game for gp in player.game_players]
    current_game = db.session.get(models.Game, gid) if gid else None
    return render_template("pages/stats_player.html", player=player, player_games=player_games,current_game=current_game)


# 404 not found page
@app.errorhandler(404)
def not_found(err):
    return render_template("pages/404.html", error=err)
