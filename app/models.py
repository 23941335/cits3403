from typing import Optional
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

# NOTE:
# 1) DATATYPES: I have used Text here as the datatype for strings. This is the only option
# in SQLite, but you can also use varchars in the model, SQLite will just treat it
# as a TEXT type. If this were needed to be ported to another database, it would be
# better to use a specific type and specify the length, e.g. String(256).

# Create a base model inheriting from the db.Model
# so that we can define custom methods shared by all models.
class BaseModel(db.Model):
    __abstract__ = True

    @classmethod
    def get_field(cls, field_name):
        if hasattr(cls, field_name):
            return getattr(cls, field_name)
        raise AttributeError(f"{cls.__name__} has no attribute '{field_name}'")
    
    @classmethod
    def populate_with_list(cls, field_name, values):
        insertions = 0
        already_exist = 0

        for v in values:
            v = v.lower()
            existing_val = db.session.scalar(sa.select(cls).where(cls.get_field(field_name) == v))
            if existing_val is None:
                db.session.add(cls(**{field_name: v}))
                print(f"{cls.__name__}.{field_name} '{v}' will be inserted.")
                insertions += 1
            else:
                print(f"{cls.__name__}.{field_name} '{v}' already exists.")
                already_exist += 1

        db.session.commit()
        print(f'Inserted {insertions} records. Skipped {already_exist} records.')

class Team(BaseModel):
    id: Mapped[int] = mapped_column(primary_key=True)
    team_name: Mapped[str] = mapped_column(sa.Text, unique=True, index=True)

    games_as_team_a: Mapped[list["Game"]] = relationship("Game", foreign_keys="[Game.team_a_id]", back_populates="team_a")
    games_as_team_b: Mapped[list["Game"]] = relationship("Game", foreign_keys="[Game.team_b_id]", back_populates="team_b")

    def __repr__(self):
        return f"<Team '{self.team_name}'>"

class Player(BaseModel):
    id: Mapped[int] = mapped_column(primary_key=True)
    gamertag: Mapped[str] = mapped_column(sa.Text, unique=True, index=True)

    user: Mapped["User"] = relationship("User", back_populates="player")
    game_players: Mapped[list["GamePlayers"]] = relationship("GamePlayers", back_populates="player")

    def __repr__(self):
        return f"<Player '{self.gamertag}'>"

class Role(BaseModel):
    id: Mapped[int] = mapped_column(primary_key=True)
    role_name: Mapped[str] = mapped_column(sa.Text, index=True, unique=True)

    permissions: Mapped[list["Permission"]] = relationship("Permission", secondary="role_permissions", back_populates="roles")

    def __repr__(self):
        return f"<Role '{self.role_name}'>"

class Permission(BaseModel):
    id: Mapped[int] = mapped_column(primary_key=True)
    permission: Mapped[str] = mapped_column(sa.Text, index=True, unique=True)

    roles: Mapped[list["Role"]] = relationship("Role", secondary="role_permissions", back_populates="permissions")

    def __repr__(self):
        return f"<Permission '{self.permission}'>"

class RolePermissions(BaseModel):
    role_id: Mapped[int] = mapped_column(sa.ForeignKey(Role.id), primary_key=True)
    permission_id: Mapped[int] = mapped_column(sa.ForeignKey(Permission.id), primary_key=True)

class User(UserMixin, BaseModel):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(sa.Text, index=True, unique=True)
    password_hash: Mapped[Optional[str]] = mapped_column(sa.Text)
    email: Mapped[str] = mapped_column(sa.Text, index=True, unique=True)
    # Not sure if we really need create/update dates, but they are common so I included them.
    created_at: Mapped[datetime] = mapped_column(sa.DateTime, default=datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(sa.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    global_role_id: Mapped[int] = mapped_column(sa.ForeignKey(Role.id))
    player_id: Mapped[int] = mapped_column(sa.ForeignKey(Player.id), nullable=True)
    is_active: Mapped[bool] = mapped_column(sa.Boolean, default=True)
    profile_picture: Mapped[Optional[str]] = mapped_column(sa.Text, nullable=True)


    player: Mapped["Player"] = relationship("Player", back_populates="user")
    tournaments: Mapped[list["TournamentUsers"]] = relationship("TournamentUsers", back_populates="user")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User '{self.username}', '{self.email}'>"

class Visibility(BaseModel):
    id: Mapped[int] = mapped_column(primary_key=True)
    visibility: Mapped[str] = mapped_column(sa.Text, unique=True)

    tournaments: Mapped[list["Tournament"]] = relationship("Tournament", back_populates="visibility")

    def __repr__(self):
        return f"<Visibility '{self.visibility}'>"

class Tournament(BaseModel):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(sa.Text)
    description: Mapped[str] = mapped_column(sa.Text)
    visibility_id: Mapped[int] = mapped_column(sa.ForeignKey(Visibility.id))

    visibility: Mapped["Visibility"] = relationship("Visibility", back_populates="tournaments")
    users: Mapped[list["TournamentUsers"]] = relationship("TournamentUsers", back_populates="tournament")
    games: Mapped[list["Game"]] = relationship("Game", back_populates="tournament")

    def __repr__(self):
        return f"<Tournament '{self.title}'>"

class TournamentUsers(BaseModel):
    tournament_id: Mapped[int] = mapped_column(sa.ForeignKey(Tournament.id), primary_key=True)
    user_id: Mapped[int] = mapped_column(sa.ForeignKey(User.id), primary_key=True)
    tournament_role_id: Mapped[int] = mapped_column(sa.ForeignKey(Role.id))

    tournament: Mapped["Tournament"] = relationship("Tournament", back_populates="users")
    user: Mapped["User"] = relationship("User", back_populates="tournaments")

class GameMode(BaseModel):
    id: Mapped[int] = mapped_column(primary_key=True)
    game_mode_name: Mapped[str] = mapped_column(sa.Text, unique=True)

    def __repr__(self):
        return f"<GameMode '{self.game_mode_name}'>"

class Map(BaseModel):
    id: Mapped[int] = mapped_column(primary_key=True)
    map_name: Mapped[str] = mapped_column(sa.Text, unique=True)
    map_image: Mapped[str] = mapped_column(sa.Text, nullable=True)

    def __repr__(self):
        return f"<Map '{self.map_name}'>"

class Game(BaseModel):
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
    team_a: Mapped["Team"] = relationship("Team", foreign_keys=[team_a_id], back_populates="games_as_team_a")
    team_b: Mapped["Team"] = relationship("Team", foreign_keys=[team_b_id], back_populates="games_as_team_b")

    def __repr__(self):
        # return f"<Game '{self.team_a.team_name}' vs. '{self.team_b.team_name}'>"
        return f"<Game>"

class Medal(BaseModel):
    id: Mapped[int] = mapped_column(primary_key=True)
    medal_name: Mapped[str] = mapped_column(sa.Text, unique=True)
    medal_icon: Mapped[str] = mapped_column(sa.Text, nullable=True)

    def __repr__(self):
        return f"<Medal '{self.medal_name}'>"


class GameMedals(BaseModel):
    game_id: Mapped[int] = mapped_column(sa.ForeignKey(Game.id), primary_key=True)
    medal_id: Mapped[int] = mapped_column(sa.ForeignKey(Medal.id), primary_key=True)
    player_id: Mapped[int] = mapped_column(sa.ForeignKey(Player.id), primary_key=True)

class HeroRole(BaseModel):
    id: Mapped[int] = mapped_column(primary_key=True)
    role_name: Mapped[str] = mapped_column(sa.Text, unique=True)
    role_icon: Mapped[str] = mapped_column(sa.Text, nullable=True)

    def __repr__(self):
        return f"<HeroRole '{self.role_name}'>"

class Hero(BaseModel):
    id: Mapped[int] = mapped_column(primary_key=True)
    hero_name: Mapped[str] = mapped_column(sa.Text, unique=True)
    hero_role_id: Mapped[int] = mapped_column(sa.ForeignKey(HeroRole.id))
    hero_image: Mapped[str] = mapped_column(sa.Text, nullable=True)

    def __repr__(self):
        return f"<Hero '{self.hero_name}'>"

class GamePlayers(BaseModel):
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

    def __repr__(self):
        return f"<GamePlayers>"

# TODO: is there somewhere better to put this?
@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))