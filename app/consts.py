from enum import Enum

class PERMISSION(Enum):
    READ   = 'view'
    DELETE = 'delete'
    UPLOAD = 'upload'


class ROLE(Enum):
    DEFAULT = 'default'
    OWNER = 'tournament_owner'

ROLE_PERMISSIONS = {
    ROLE.DEFAULT: [PERMISSION.READ],
    ROLE.OWNER: [PERMISSION.READ, PERMISSION.UPLOAD, PERMISSION.DELETE]
}

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