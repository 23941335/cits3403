# This script should be run to populate the database with initial values.

from app import app, db
from app.consts import *
from app.models import Role, Hero, HeroRole, GameMode, Visibility, Map, Permission, RolePermissions
import sqlalchemy as sa
import sqlalchemy.exc as sa_exc

def db_add_hero(hero_name: str, hero_role: str, hero_image:str=None):
    hero_exists = db.session.query(Hero).filter(Hero.hero_name.ilike(hero_name.casefold())).first()
    if not hero_exists:
        try:
            qry = db.session.query(HeroRole)
            hr = qry.filter(HeroRole.role_name.ilike(hero_role.casefold())).first()
            if not hr:
                raise sa_exc.NoResultFound(f"Hero role '{hero_role}' does not exist in the database.")
            hero = Hero(
                hero_name=hero_name,
                hero_role_id=hr.id,
                hero_image=hero_image
            )
            db.session.add(hero)
            db.session.commit()
            print(f"Inserted hero: {hero_name} ({hero_role})")
            return True
        except Exception as e:
            db.session.rollback()
            raise
    else:
        print(f"Skipped hero: {hero_name} ({hero_role}) - already exists.")
        return False


def populate_heros():
    inserted = 0
    skipped = 0
    for hero_role in HEROS:
        for hero in HEROS[hero_role]:
            insert_succeeded = db_add_hero(hero['name'], hero_role)
            inserted += (1 if insert_succeeded else 0)
            skipped += (1 if not insert_succeeded else 0)
    print(f"Inserted {inserted} records. Skipped {skipped} records.")

#clear these tables first
def db_add_role_permission(role_name, permission_name):
    role = db.session.query(Role).filter_by(role_name=role_name).first()
    permission = db.session.query(Permission).filter_by(permission=permission_name).first()
    if not role or not permission:
        raise sa_exc.NoResultFound("Role or permission does not exist!")
    
    exists = db.session.query(RolePermissions).filter_by(role_id=role.id, permission_id=permission.id).first()
    if not exists:
        try:
            role_permission = RolePermissions(role_id=role.id, permission_id=permission.id)
            db.session.add(role_permission)
            db.session.commit()
            print(f"Inserted role-permission: {role_name}: {permission_name}")
            return True
        except Exception as e:
            db.session.rollback()
            raise
    else:
        print(f"Skipped role-permission: {role_name}: {permission_name} - already exists.")
        return False

def populate_role_permissions():
    inserted = 0
    skipped = 0
    for role in ROLE_PERMISSIONS:
        for permissions in ROLE_PERMISSIONS[role]:
            insert_succeeded = db_add_hero(hero['name'], hero_role)
            inserted += (1 if insert_succeeded else 0)
            skipped += (1 if not insert_succeeded else 0)
    print(f"Inserted {inserted} records. Skipped {skipped} records.")

def reset_tables(model_list):
    '''Will run DELETE FROM <table>; for each model in the list.'''
    try:
        for model in model_list:
            print(f"Resetting {model.__name__}...")
            db.session.query(model).delete()
    
        db.session.commit()
    
    except:
        print(f"Reset failed - rolled back changes.")
        db.session.rollback()
        raise

if __name__ == '__main__':
    with app.app_context():
        reset_tables([Role, Permission, RolePermissions, Hero, HeroRole, GameMode, Visibility, Map])
        Role.populate_with_list('role_name', [role.value for role in ROLE])
        Permission.populate_with_list('permission', [permission.value for permission in PERMISSION])
        HeroRole.populate_with_list('role_name', ['vanguard', 'duelist', 'strategist'])
        GameMode.populate_with_list('game_mode_name', ['domination', 'convoy', 'convergence'])
        Visibility.populate_with_list('visibility', ['public', 'private'])
        map_list = [map_item['name'] for gamemode in MAPS.values() for map_item in gamemode]
        Map.populate_with_list('map_name', map_list, use_casefold=False)
        populate_heros()