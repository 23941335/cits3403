# This script should be run to populate the database with initial values.

from app import app, db
from app.models import Role, HeroRole
import sqlalchemy as sa

# Initial population of roles into the database
# Do not change this
def populate_roles():
    roles = ['default', 'administrator', 'moderator']
    for role in roles:
        existing_role = db.session.scalar(sa.select(Role).where(Role.role_name == role.lower()))
        if existing_role is None:
            db.session.add(Role(role_name=role.lower()))
            print(f'Role {role} will be inserted.')
        else:
            print(f'Role {role} already exists in database.')
    
    db.session.commit()
    print(f'Roles successfully inserted.')

def populate_hero_roles():
    hero_roles = ['vanguard', 'duelist', 'strategist']
    for hero_role in hero_roles:
        existing_role = db.session.scalar(sa.select(HeroRole).where(HeroRole.role_name == hero_role.lower()))
        if existing_role is None:
            db.session.add(HeroRole(role_name=hero_role.lower()))
            print(f'Hero Role {hero_role} will be inserted.')
        else:
            print(f'Hero Role {hero_role} already exists in database.')
    
    db.session.commit()
    print(f'Hero Roles successfully inserted.')

if __name__ == '__main__':
    with app.app_context():
        populate_roles()
        populate_hero_roles()
