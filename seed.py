# This script should be run to populate the database with initial values.

from app import app, db
from app.models import Role, Hero, HeroRole, GameMode, Visibility, Map
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

# List sourced from Marvel Rivals Wiki
# https://marvelrivals.fandom.com/wiki/Heroes
HEROS = {
    'vanguard': [
        { 'name': 'Captain America',     'image': '' },
        { 'name': 'Doctor Strange',      'image': '' },
        { 'name': 'Emma Frost',          'image': '' },
        { 'name': 'Groot',               'image': '' },
        { 'name': 'Hulk',                'image': '' },
        { 'name': 'Magneto',             'image': '' },
        { 'name': 'Peni Parker',         'image': '' },
        { 'name': 'The Thing',           'image': '' },
        { 'name': 'Thor',                'image': '' },
        { 'name': 'Venom',               'image': '' },
    ],
    'duelist': [
        { 'name': 'Black Panther',       'image': '' },
        { 'name': 'Black Widow',         'image': '' },
        { 'name': 'Hawkeye',             'image': '' },
        { 'name': 'Hela',                'image': '' },
        { 'name': 'Human Torch',         'image': '' },
        { 'name': 'Iron Fist',           'image': '' },
        { 'name': 'Iron Man',            'image': '' },
        { 'name': 'Magik',               'image': '' },
        { 'name': 'Mister Fantastic',    'image': '' },
        { 'name': 'Moon Knight',         'image': '' },
        { 'name': 'Namor',               'image': '' },
        { 'name': 'Psylocke',            'image': '' },
        { 'name': 'Scarlet Witch',       'image': '' },
        { 'name': 'Spider-Man',          'image': '' },
        { 'name': 'Squirrel Girl',       'image': '' },
        { 'name': 'Star-Lord',           'image': '' },
        { 'name': 'Storm',               'image': '' },
        { 'name': 'The Punisher',        'image': '' },
        { 'name': 'Winter Soldier',      'image': '' },
        { 'name': 'Wolverine',           'image': '' },
    ],
    'strategist': [
        { 'name': 'Adam Warlock',        'image': '' },
        { 'name': 'Cloak & Dagger',      'image': '' },
        { 'name': 'Invisible Woman',     'image': '' },
        { 'name': 'Jeff the Land Shark', 'image': '' },
        { 'name': 'Loki',                'image': '' },
        { 'name': 'Luna Snow',           'image': '' },
        { 'name': 'Mantis',              'image': '' },
        { 'name': 'Rocket Raccoon',      'image': '' },
    ]
}

MAPS = {
    'convergence': [
        { 'name': 'Central Park',         'image': '' },
        { 'name': 'Hall of Djalia',       'image': '' },
        { 'name': 'Symbiotic Surface',    'image': '' },
        { 'name': 'Shin-Shibuya',         'image': '' },
    ],
    'convoy': [
        { 'name': 'Midtown',              'image': '' },
        { 'name': 'Spider-Islands',       'image': '' },
        { 'name': 'Yggdrasill Path',      'image': '' },
    ],
    'domination': [
        { 'name': "Birnin T'Challa",      'image': '' },
        { 'name': "Hell's Heaven",        'image': '' },
        { 'name': "Krakoa",               'image': '' },
        { 'name': "Royal Palace",         'image': '' },
    ]
}

map_list = [map_item['name'] for gamemode in MAPS.values() for map_item in gamemode]

def populate_heros():
    inserted = 0
    skipped = 0
    for hero_role in HEROS:
        for hero in HEROS[hero_role]:
            insert_succeeded = db_add_hero(hero['name'], hero_role)
            inserted += (1 if insert_succeeded else 0)
            skipped += (1 if not insert_succeeded else 0)
    print(f"Inserted {inserted} records. Skipped {skipped} records.")


if __name__ == '__main__':
    with app.app_context():
        Role.populate_with_list('role_name', ['default', 'administrator', 'moderator'])
        HeroRole.populate_with_list('role_name', ['vanguard', 'duelist', 'strategist'])
        GameMode.populate_with_list('game_mode_name', ['domination', 'convoy', 'convergence'])
        Visibility.populate_with_list('visibility', ['public', 'private'])
        Map.populate_with_list('map_name', map_list, use_casefold=False)
        populate_heros()