# This script should be run to populate the database with initial values.

from app import app, db
from app.models import Role
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

if __name__ == '__main__':
    with app.app_context():
        populate_roles()
