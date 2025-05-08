# This script should be run to populate the database with initial values.

from app import app, db
from app.models import Role, HeroRole, GameMode

if __name__ == '__main__':
    with app.app_context():
        Role.populate_with_list('role_name', ['default', 'administrator', 'moderator'])
        HeroRole.populate_with_list('role_name', ['vanguard', 'duelist', 'strategist'])
        GameMode.populate_with_list('game_mode_name', ['domination']) # TODO: add rest of modes