from typing import Optional
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
from app import db
from werkzeug.security import generate_password_hash, check_password_hash

# NOTE:
# 1) DATATYPES: I have used Text here as the datatype for strings. This is the only option
# in SQLite, but you can also use varchars in the model, SQLite will just treat it
# as a TEXT type. If this were needed to be ported to another database, it would be
# better to use a specific type and specify the length, e.g. String(256).

class Team(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    team_name: Mapped[str] = mapped_column(sa.Text, unique=True, index=True)

class Player(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    gamertag: Mapped[str] = mapped_column(sa.Text, unique=True, index=True)

    user: Mapped["User"] = relationship("User", back_populates="player")
    game_players: Mapped[list["GamePlayers"]] = relationship("GamePlayers", back_populates="player")

class Role(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    role_name: Mapped[str] = mapped_column(sa.Text, index=True, unique=True)

    permissions: Mapped[list["Permission"]] = relationship("Permission", secondary="role_permissions", back_populates="roles")

class Permission(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    permission: Mapped[str] = mapped_column(sa.Text, index=True, unique=True)

    roles: Mapped[list["Role"]] = relationship("Role", secondary="role_permissions", back_populates="permissions")

class RolePermissions(db.Model):
    role_id: Mapped[int] = mapped_column(sa.ForeignKey(Role.id), primary_key=True)
    permission_id: Mapped[int] = mapped_column(sa.ForeignKey(Permission.id), primary_key=True)

class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(sa.Text, index=True, unique=True)
    password_hash: Mapped[Optional[str]] = mapped_column(sa.Text)
    email: Mapped[str] = mapped_column(sa.Text, index=True, unique=True)
    # Not sure if we really need create/update dates, but they are common so I included them.
    created_at: Mapped[datetime] = mapped_column(sa.DateTime, default=datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(sa.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    global_role_id: Mapped[int] = mapped_column(sa.ForeignKey(Role.id))
    player_id: Mapped[int] = mapped_column(sa.ForeignKey(Player.id), nullable=True)
    is_active: Mapped[bool] = mapped_column(sa.Boolean)

    player: Mapped["Player"] = relationship("Player", back_populates="user")
    tournaments: Mapped[list["TournamentUsers"]] = relationship("TournamentUsers", back_populates="user")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Visibility(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    visibility: Mapped[str] = mapped_column(sa.Text, unique=True)

    tournaments: Mapped[list["Tournament"]] = relationship("Tournament", back_populates="visibility")

class Tournament(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(sa.Text)
    description: Mapped[str] = mapped_column(sa.Text)
    visibility_id: Mapped[int] = mapped_column(sa.ForeignKey(Visibility.id))

    visibility: Mapped["Visibility"] = relationship("Visibility", back_populates="tournaments")
    users: Mapped[list["TournamentUsers"]] = relationship("TournamentUsers", back_populates="tournament")
    games: Mapped[list["Game"]] = relationship("Game", back_populates="tournament")

class TournamentUsers(db.Model):
    tournament_id: Mapped[int] = mapped_column(sa.ForeignKey(Tournament.id), primary_key=True)
    user_id: Mapped[int] = mapped_column(sa.ForeignKey(User.id), primary_key=True)
    tournament_role_id: Mapped[int] = mapped_column(sa.ForeignKey(Role.id))

    tournament: Mapped["Tournament"] = relationship("Tournament", back_populates="users")
    user: Mapped["User"] = relationship("User", back_populates="tournaments")

class GameMode(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    game_mode_name: Mapped[str] = mapped_column(sa.Text, unique=True)

class Map(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    map_name: Mapped[str] = mapped_column(sa.Text, unique=True)
    map_image: Mapped[str] = mapped_column(sa.Text, nullable=True)

class Game(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    tournament_id: Mapped[int] = mapped_column(sa.ForeignKey(Tournament.id))
    round: Mapped[int]
    team_a_id: Mapped[int] = mapped_column(sa.ForeignKey(Team.id))
    team_b_id: Mapped[int] = mapped_column(sa.ForeignKey(Team.id))
    # References winning team's id, or NULL if game was a draw.
    # But, querying draws should check is_draw to ensure accuracy.
    winning_team: Mapped[int] = mapped_column(sa.ForeignKey(Team.id), nullable=True)
    is_draw: Mapped[bool] = mapped_column(sa.Boolean)
    game_mode_id: Mapped[int] = mapped_column(sa.ForeignKey(GameMode.id))
    map_id: Mapped[int] = mapped_column(sa.ForeignKey(Map.id))

    tournament: Mapped["Tournament"] = relationship("Tournament", back_populates="games")
    game_players: Mapped[list["GamePlayers"]] = relationship("GamePlayers", back_populates="game")

class Medal(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    medal_name: Mapped[str] = mapped_column(sa.Text, unique=True)
    medal_icon: Mapped[str] = mapped_column(sa.Text, nullable=True)

class GameMedals(db.Model):
    game_id: Mapped[int] = mapped_column(sa.ForeignKey(Game.id), primary_key=True)
    medal_id: Mapped[int] = mapped_column(sa.ForeignKey(Medal.id), primary_key=True)
    player_id: Mapped[int] = mapped_column(sa.ForeignKey(Player.id), primary_key=True)

class HeroRole(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    role_name: Mapped[str] = mapped_column(sa.Text, unique=True)
    role_icon: Mapped[str] = mapped_column(sa.Text, nullable=True)

class Hero(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    hero_name: Mapped[str] = mapped_column(sa.Text, unique=True)
    hero_role_id: Mapped[int] = mapped_column(sa.ForeignKey(HeroRole.id))
    hero_image: Mapped[str] = mapped_column(sa.Text, nullable=True)

class GamePlayers(db.Model):
    game_id: Mapped[int] = mapped_column(sa.ForeignKey(Game.id), primary_key=True)
    player_id: Mapped[int] = mapped_column(sa.ForeignKey(Player.id), primary_key=True)
    team_id: Mapped[int] = mapped_column(sa.ForeignKey(Team.id))  # the team the user is representing
    hero_id: Mapped[int] = mapped_column(sa.ForeignKey(Hero.id))  # hero listed on scoreboard
    kills: Mapped[int]
    deaths: Mapped[int]
    assists: Mapped[int]
    final_hits: Mapped[int]
    damage: Mapped[int]
    damage_blocked: Mapped[int]
    healing: Mapped[int]
    accuracy_pct: Mapped[int]

    game: Mapped["Game"] = relationship("Game", back_populates="game_players")
    player: Mapped["Player"] = relationship("Player", back_populates="game_players")