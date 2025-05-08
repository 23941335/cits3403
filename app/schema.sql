CREATE TABLE game_mode (
    id INTEGER NOT NULL,
    game_mode_name TEXT NOT NULL,
    PRIMARY KEY (id),
    UNIQUE (game_mode_name)
);

CREATE TABLE hero_role (
    id INTEGER NOT NULL,
    role_name TEXT NOT NULL,
    role_icon TEXT,
    PRIMARY KEY (id),
    UNIQUE (role_name)
);

CREATE TABLE map (
    id INTEGER NOT NULL,
    map_name TEXT NOT NULL,
    map_image TEXT,
    PRIMARY KEY (id),
    UNIQUE (map_name)
);

CREATE TABLE medal (
    id INTEGER NOT NULL,
    medal_name TEXT NOT NULL,
    medal_icon TEXT,
    PRIMARY KEY (id),
    UNIQUE (medal_name)
);

CREATE TABLE permission (
    id INTEGER NOT NULL,
    permission TEXT NOT NULL,
    PRIMARY KEY (id)
);

CREATE UNIQUE INDEX ix_permission_permission ON permission (permission);
CREATE TABLE role (
    id INTEGER NOT NULL,
    role_name TEXT NOT NULL,
    PRIMARY KEY (id)
    UNIQUE (role_name)
);

CREATE UNIQUE INDEX ix_role_role_name ON role (role_name);
CREATE TABLE team (
    id INTEGER NOT NULL,
    team_name TEXT NOT NULL,
    PRIMARY KEY (id)
    UNIQUE(team_name)
);
CREATE UNIQUE INDEX ix_team_team_name ON team (team_name);

CREATE TABLE visibility (
    id INTEGER NOT NULL,
    visibility TEXT NOT NULL,
    PRIMARY KEY (id),
    UNIQUE (visibility)
);

CREATE TABLE hero (
    id INTEGER NOT NULL,
    hero_name TEXT NOT NULL,
    hero_role_id INTEGER NOT NULL,
    hero_image TEXT,
    PRIMARY KEY (id),
    FOREIGN KEY(hero_role_id) REFERENCES hero_role (id),
    UNIQUE (hero_name)
);

CREATE TABLE player (
    id INTEGER NOT NULL,
    gamertag TEXT NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY(team_id) REFERENCES team (id)
    UNIQUE (gamertag)
);

CREATE UNIQUE INDEX ix_player_gamertag ON player (gamertag);
CREATE TABLE role_permissions (
    role_id INTEGER NOT NULL,
    permission_id INTEGER NOT NULL,
    PRIMARY KEY (role_id, permission_id),
    FOREIGN KEY(permission_id) REFERENCES permission (id),
    FOREIGN KEY(role_id) REFERENCES role (id)
);

CREATE TABLE tournament (
    id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    visibility_id INTEGER NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY(visibility_id) REFERENCES visibility (id)
);

CREATE TABLE game (
    id INTEGER NOT NULL,
    tournament_id INTEGER NOT NULL,
    round INTEGER NOT NULL,
    team_a_id INTEGER NOT NULL,
    team_b_id INTEGER NOT NULL,
    winning_team INTEGER,
    is_draw BOOLEAN NOT NULL,
    game_mode_id INTEGER NOT NULL,
    map_id INTEGER NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY(game_mode_id) REFERENCES game_mode (id),
    FOREIGN KEY(map_id) REFERENCES map (id),
    FOREIGN KEY(team_a_id) REFERENCES team (id),
    FOREIGN KEY(team_b_id) REFERENCES team (id),
    FOREIGN KEY(tournament_id) REFERENCES tournament (id),
    FOREIGN KEY(winning_team) REFERENCES team (id)
);

CREATE TABLE user (
    id INTEGER NOT NULL,
    username TEXT NOT NULL,
    password_hash TEXT,
    email TEXT NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    global_role_id INTEGER NOT NULL,
    player_id INTEGER NOT NULL,
    is_active BOOLEAN NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY(global_role_id) REFERENCES role (id),
    FOREIGN KEY(player_id) REFERENCES player (id)
);

CREATE UNIQUE INDEX ix_user_email ON user (email);
CREATE UNIQUE INDEX ix_user_username ON user (username);
CREATE TABLE game_medals (
    game_id INTEGER NOT NULL,
    medal_id INTEGER NOT NULL,
    player_id INTEGER NOT NULL,
    PRIMARY KEY (game_id, medal_id, player_id),
    FOREIGN KEY(game_id) REFERENCES game (id),
    FOREIGN KEY(medal_id) REFERENCES medal (id),
    FOREIGN KEY(player_id) REFERENCES player (id)
);

CREATE TABLE game_players (
    game_id INTEGER NOT NULL,
    player_id INTEGER NOT NULL,
    team_id INTEGER NOT NULL,
    hero_id INTEGER NOT NULL,
    kills INTEGER NOT NULL,
    deaths INTEGER NOT NULL,
    assists INTEGER NOT NULL,
    final_hits INTEGER NOT NULL,
    damage INTEGER NOT NULL,
    damage_blocked INTEGER NOT NULL,
    healing INTEGER NOT NULL,
    accuracy_pct INTEGER NOT NULL,
    PRIMARY KEY (game_id, player_id),
    FOREIGN KEY(game_id) REFERENCES game (id),
    FOREIGN KEY(hero_id) REFERENCES hero (id),
    FOREIGN KEY(player_id) REFERENCES player (id),
    FOREIGN KEY(team_id) REFERENCES team (id)
);

CREATE TABLE tournament_users (
    tournament_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    tournament_role_id INTEGER NOT NULL,
    PRIMARY KEY (tournament_id, user_id),
    FOREIGN KEY(tournament_id) REFERENCES tournament (id),
    FOREIGN KEY(tournament_role_id) REFERENCES role (id),
    FOREIGN KEY(user_id) REFERENCES user (id)
);